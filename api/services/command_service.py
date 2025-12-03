"""
Command execution service with streaming support
Wraps CommandExecutor for API use with output streaming
"""
import subprocess
import asyncio
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, AsyncGenerator, Callable
from queue import Queue
from threading import Thread

from agent.command_executor import CommandExecutor
from utils.logger import log as logger


class CommandExecutionResult:
    """Result of a command execution"""
    
    def __init__(self, execution_id: str, command: str):
        self.execution_id = execution_id
        self.command = command
        self.status = "running"  # running, completed, failed, cancelled
        self.output = ""
        self.error = ""
        self.return_code: Optional[int] = None
        self.start_time = datetime.now()
        self.end_time: Optional[datetime] = None
        self._process: Optional[subprocess.Popen] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "execution_id": self.execution_id,
            "command": self.command,
            "status": self.status,
            "output": self.output,
            "error": self.error,
            "return_code": self.return_code,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None
        }


class CommandService:
    """
    Service for executing commands with streaming output support.
    Provides both synchronous and asynchronous execution modes.
    """
    
    def __init__(self):
        """Initialize command service"""
        self._executor = CommandExecutor()
        self._active_executions: Dict[str, CommandExecutionResult] = {}
        logger.info("CommandService initialized")
    
    def execute_stream(
        self,
        command: str,
        execution_mode: str = "background",
        on_output: Optional[Callable[[str], None]] = None
    ) -> CommandExecutionResult:
        """
        Execute a command with streaming output
        
        Args:
            command: Command to execute
            execution_mode: "background" (capture output) or "tmux" (use tmux)
            on_output: Optional callback for each output chunk
            
        Returns:
            CommandExecutionResult instance
        """
        execution_id = str(uuid.uuid4())
        result = CommandExecutionResult(execution_id, command)
        self._active_executions[execution_id] = result
        
        logger.info(f"Starting stream execution {execution_id}: {command}")
        
        try:
            if execution_mode == "background":
                # Execute in background and capture output
                process = subprocess.Popen(
                    command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,  # Line buffered
                    universal_newlines=True
                )
                
                result._process = process
                
                # Start threads to read stdout and stderr
                stdout_thread = Thread(
                    target=self._read_stream,
                    args=(process.stdout, result, "output", on_output),
                    daemon=True
                )
                stderr_thread = Thread(
                    target=self._read_stream,
                    args=(process.stderr, result, "error", on_output),
                    daemon=True
                )
                
                stdout_thread.start()
                stderr_thread.start()
                
                # Wait for process completion in a separate thread
                def wait_process():
                    try:
                        process.wait()
                        result.return_code = process.returncode
                        result.end_time = datetime.now()
                        if process.returncode == 0:
                            result.status = "completed"
                        else:
                            result.status = "failed"
                        logger.info(f"Execution {execution_id} completed with code {process.returncode}")
                    except Exception as e:
                        logger.error(f"Error waiting for process: {e}")
                        result.status = "failed"
                        result.error = str(e)
                        result.end_time = datetime.now()
                
                wait_thread = Thread(target=wait_process, daemon=True)
                wait_thread.start()
                
            else:
                # Use existing CommandExecutor for tmux mode
                # This returns immediately, doesn't capture output
                output = self._executor._send_to_tmux(command)
                result.output = output
                result.status = "completed"
                result.end_time = datetime.now()
                result.return_code = 0
                
        except Exception as e:
            logger.error(f"Execution {execution_id} failed: {e}", exc_info=True)
            result.status = "failed"
            result.error = str(e)
            result.end_time = datetime.now()
        
        return result
    
    @staticmethod
    def _read_stream(stream, result: CommandExecutionResult, attr: str, on_output: Optional[Callable[[str], None]]):
        """Read from stream and update result"""
        try:
            for line in iter(stream.readline, ''):
                if not line:
                    break
                
                line_text = line.rstrip('\n\r')
                if not line_text:
                    continue
                
                # Update result
                if attr == "output":
                    result.output += line  # Keep newline for proper formatting
                    logger.debug(f"Execution {result.execution_id} stdout: {line_text[:100]}")
                else:
                    result.error += line
                    logger.debug(f"Execution {result.execution_id} stderr: {line_text[:100]}")
                
                # Call callback if provided
                if on_output:
                    try:
                        on_output(line)
                    except Exception as e:
                        logger.error(f"Error in output callback: {e}")
        except Exception as e:
            logger.error(f"Error reading stream: {e}")
        finally:
            try:
                stream.close()
            except:
                pass
    
    async def execute_stream_async(
        self,
        command: str,
        execution_mode: str = "background"
    ) -> AsyncGenerator[str, None]:
        """
        Execute command and yield output chunks asynchronously
        
        Args:
            command: Command to execute
            execution_mode: Execution mode
            
        Yields:
            Output chunks as strings
        """
        execution_id = str(uuid.uuid4())
        logger.info(f"Starting async stream execution {execution_id}: {command}")
        
        try:
            if execution_mode == "background":
                process = await asyncio.create_subprocess_exec(
                    *command.split() if ' ' not in command else ['bash', '-c', command],
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                # Read stdout and stderr concurrently
                async def read_output(stream, label: str):
                    """Read from stream and yield lines"""
                    while True:
                        line = await stream.readline()
                        if not line:
                            break
                        line_str = line.decode('utf-8', errors='ignore')
                        yield f"[{label}] {line_str}"
                
                # Combine stdout and stderr
                async for line in read_output(process.stdout, "stdout"):
                    yield line
                
                async for line in read_output(process.stderr, "stderr"):
                    yield line
                
                # Wait for process
                await process.wait()
                
                if process.returncode != 0:
                    yield f"\n[ERROR] Command failed with return code {process.returncode}"
                    
            else:
                # For tmux mode, return status message
                output = self._executor._send_to_tmux(command)
                yield output
                
        except Exception as e:
            logger.error(f"Async execution {execution_id} failed: {e}", exc_info=True)
            yield f"[ERROR] Execution failed: {str(e)}"
    
    def get_execution(self, execution_id: str) -> Optional[CommandExecutionResult]:
        """Get execution result by ID"""
        return self._active_executions.get(execution_id)
    
    def cancel_execution(self, execution_id: str) -> bool:
        """Cancel a running execution"""
        result = self._active_executions.get(execution_id)
        if result and result._process and result.status == "running":
            try:
                result._process.terminate()
                result.status = "cancelled"
                result.end_time = datetime.now()
                logger.info(f"Execution {execution_id} cancelled")
                return True
            except Exception as e:
                logger.error(f"Failed to cancel execution {execution_id}: {e}")
                return False
        return False
    
    def cleanup_execution(self, execution_id: str):
        """Remove execution from tracking"""
        if execution_id in self._active_executions:
            del self._active_executions[execution_id]

