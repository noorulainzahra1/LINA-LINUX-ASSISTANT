# agent/command_executor.py
# Architect: The 'hands' of the LINA framework.
#
# PHOENIX RE-ARCHITECTURE: This agent is now hyper-specialized and simplified.
# Its ONLY job is to take a final, complete shell command string and execute it
# in an external terminal. It interactively prompts the user for the execution
# style (Persistent via tmux or Separate windows) for each command. All logic
# for Python tools and runner scripts is now obsolete and has been REMOVED.

import subprocess
import time
from typing import Dict, Any, Union

from rich.console import Console
from rich.prompt import Prompt
from utils.logger import log

console = Console()
# The unique name for our persistent tmux execution session.
LINA_EXEC_SESSION = "lina_exec"

class CommandExecutor:
    """
    Executes a final shell command string in an external terminal, allowing the
    user to choose between a persistent session or separate windows for each command.
    """
    def __init__(self):
        """Initializes the executor and the name for the dedicated tmux session."""
        self.tmux_session_name = LINA_EXEC_SESSION
        self._session_checked = False # A flag to avoid checking for the session on every command

    def execute(self, command: str) -> str:
        """
        The single, unified execution method. It takes a final command string
        and orchestrates the interactive execution flow.

        Args:
            command: The complete, final shell command string to execute.
        
        Returns:
            A string containing a status message of the execution.
        """
        if not isinstance(command, str):
            msg = f"Invalid task type for executor: expected 'str', got '{type(command)}'"
            log.error(msg)
            return msg
        
        # For every command, we ask the user how they want to run it.
        return self._select_and_run_shell_command(command)

    def _select_and_run_shell_command(self, command: str) -> str:
        """Prompts the user to select an execution mode for the command."""
        console.print("\n--- [bold cyan]Execution Mode Selection[/bold cyan] ---")
        prompt_text = (
            "[bold]Choose execution mode[/bold]\n\n"
            "[1] [bold green]Persistent[/bold green]: Run in the dedicated session terminal (uses tmux).\n"
            "[2] [bold magenta]Separate[/bold magenta]:   Run in a new, single-use terminal.\n\n"
            "Enter choice"
        )
        choice = Prompt.ask(prompt_text, choices=["1", "2"], default="1")
        mode = 'persistent' if choice == '1' else 'separate'
        
        if mode == 'separate':
            return self._run_in_separate_terminal(command)
        else:
            return self._send_to_tmux(command)

    def _ensure_tmux_session_exists(self):
        """
        Checks if the dedicated tmux session exists. If not, it creates the session
        by launching a new terminal window that starts tmux.
        """
        if self._session_checked:
            return

        try:
            subprocess.run(
                ['tmux', 'has-session', '-t', self.tmux_session_name],
                check=True, capture_output=True, text=True
            )
            log.info(f"Persistent tmux session '{self.tmux_session_name}' already exists.")
        except (subprocess.CalledProcessError, FileNotFoundError):
            log.info(f"Persistent tmux session '{self.tmux_session_name}' not found. Creating new session.")
            try:
                # Try different terminal emulators common in Kali Linux
                terminal_options = [
                    ['gnome-terminal', '--', 'tmux', 'new-session', '-s', self.tmux_session_name],
                    ['xfce4-terminal', '--title=LINA-Execution-Window', '-e', f'tmux new-session -s {self.tmux_session_name}'],
                    ['konsole', '-e', f'tmux new-session -s {self.tmux_session_name}'],
                    ['xterm', '-e', f'tmux new-session -s {self.tmux_session_name}'],
                    ['terminator', '-e', f'tmux new-session -s {self.tmux_session_name}']
                ]
                
                terminal_launched = False
                for term_cmd in terminal_options:
                    try:
                        console.print(f"\n[bold magenta]Launching persistent execution terminal ({self.tmux_session_name})...[/bold magenta]")
                        subprocess.Popen(term_cmd)
                        terminal_launched = True
                        time.sleep(2)  # Give the terminal and tmux server time to initialize
                        break
                    except FileNotFoundError:
                        continue
                
                if not terminal_launched:
                    console.print("[bold red]Error: No suitable terminal found. Please install gnome-terminal, xfce4-terminal, konsole, xterm, or terminator.[/bold red]")
                    raise FileNotFoundError("No suitable terminal emulator found")
                    
            except Exception as e:
                console.print(f"[bold red]Error: Failed to launch terminal: {e}[/bold red]")
                raise
        
        self._session_checked = True

    def _send_to_tmux(self, command: str) -> str:
        """Sends a command string to the persistent tmux session for execution."""
        try:
            self._ensure_tmux_session_exists()
            target_pane = f'{self.tmux_session_name}:0.0'
            subprocess.run(['tmux', 'send-keys', '-t', target_pane, 'C-c'], check=True, capture_output=True)
            subprocess.run(['tmux', 'send-keys', '-t', target_pane, command, 'C-m'], check=True, capture_output=True)
            log.info(f"Sent command to tmux session '{self.tmux_session_name}': {command}")
            console.print(f"[green]✓ Command sent to persistent execution terminal.[/green]")
            return f"Command sent to persistent terminal: {command}"
        except Exception as e:
            log.error(f"Failed to send command to tmux: {e}", exc_info=True)
            console.print(f"[bold red]Error: Failed to send command to the execution terminal. Is it closed?[/bold red]")
            return "Error: Failed to send command to the persistent terminal."

    def _run_in_separate_terminal(self, command: str) -> str:
        """Launches a command in a new, single-use terminal window."""
        log.info(f"Executing in separate terminal: '{command}'")
        try:
            term_command = f"bash -c '{command}; echo; echo \"[Process finished. Press Enter to close.]\"; read'"
            console.print(f"\n--- [magenta]LAUNCHING IN NEW TERMINAL[/magenta] ---\n$ {command}\n")
            
            # Try different terminal emulators available in Kali Linux
            terminal_options = [
                ['gnome-terminal', '--', 'bash', '-c', f'{command}; echo; echo "[Process finished. Press Enter to close.]"; read'],
                ['xfce4-terminal', '--hold', '--title=LINA-Task', '-e', term_command],
                ['konsole', '--hold', '-e', term_command],
                ['xterm', '-hold', '-e', term_command],
                ['terminator', '-e', term_command]
            ]
            
            for term_cmd in terminal_options:
                try:
                    subprocess.Popen(term_cmd)
                    console.print("[green]✓ Command launched successfully in a new terminal.[/green]")
                    return "Command launched successfully in a new terminal."
                except FileNotFoundError:
                    continue
            
            # If no terminal found, fall back to background execution with output
            console.print("[yellow]No GUI terminal found. Running in background...[/yellow]")
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
            output = f"STDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}\n\nReturn Code: {result.returncode}"
            console.print(f"[cyan]Command Output:[/cyan]\n{output}")
            return f"Background execution completed. {output}"
            
        except subprocess.TimeoutExpired:
            error_msg = "Command timed out after 30 seconds"
            log.error(error_msg)
            console.print(f"[bold red]{error_msg}[/bold red]")
            return error_msg
        except Exception as e:
            error_msg = f"Failed to launch command: {e}"
            log.error(error_msg, exc_info=True)
            console.print(f"[bold red]{error_msg}[/bold red]")
            return error_msg