#!/usr/bin/env python3
"""
LINA Forensics Manager
=====================

Advanced digital forensics tool integration for LINA.
Provides specialized forensics capabilities and tool management.

Author: LINA Development Team
Version: 3.0.0
"""

import os
import json
import subprocess
from typing import Dict, List, Any, Optional
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table

console = Console()


class ForensicsManager:
    """
    Advanced forensics manager for LINA with specialized tool integration.
    """
    
    def __init__(self):
        """Initialize the forensics manager."""
        self.forensics_tools = self._load_forensics_tools()
        self.available_tools = self._get_available_tools()
        
    def _load_forensics_tools(self) -> Dict[str, Dict[str, Any]]:
        """Load forensics tool configurations."""
        tools = {}
        registries_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'core', 'registries')
        
        forensics_tools = [
            'volatility_registry.json',
            'autopsy_registry.json', 
            'tshark_registry.json',
            'sleuthkit_registry.json',
            'strings_registry.json',
            'foremost_registry.json',
            'binwalk_registry.json'
        ]
        
        for tool_file in forensics_tools:
            tool_path = os.path.join(registries_path, tool_file)
            if os.path.exists(tool_path):
                try:
                    with open(tool_path, 'r') as f:
                        tool_config = json.load(f)
                        tools[tool_config['tool_name']] = tool_config
                except Exception as e:
                    console.print(f"[red]Error loading {tool_file}: {e}[/red]")
                    
        return tools
    
    def _get_available_tools(self) -> List[str]:
        """Check which forensics tools are available on the system."""
        available = []
        for tool_name in self.forensics_tools.keys():
            try:
                result = subprocess.run(['which', tool_name], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    available.append(tool_name)
            except:
                pass
        return available
    
    def get_forensics_tools(self) -> Dict[str, Dict[str, Any]]:
        """Get all forensics tools."""
        return self.forensics_tools
    
    def get_available_tools(self) -> List[str]:
        """Get list of available forensics tools."""
        return self.available_tools
    
    def is_tool_available(self, tool_name: str) -> bool:
        """Check if a specific forensics tool is available."""
        return tool_name in self.available_tools
    
    def get_tool_parameters(self, tool_name: str) -> List[Dict[str, Any]]:
        """Get parameters for a specific forensics tool."""
        if tool_name in self.forensics_tools:
            return self.forensics_tools[tool_name].get('parameters', [])
        return []
    
    def execute_forensics_command(self, tool_name: str, parameters: List[str], 
                                input_file: Optional[str] = None, 
                                output_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute a forensics command with proper error handling.
        
        Args:
            tool_name: Name of the forensics tool
            parameters: List of parameters to pass to the tool
            input_file: Input file path (if applicable)
            output_dir: Output directory (if applicable)
            
        Returns:
            Dictionary with execution results
        """
        if not self.is_tool_available(tool_name):
            return {
                'success': False,
                'error': f"Forensics tool '{tool_name}' is not available on this system",
                'output': '',
                'command': ''
            }
        
        # Build command
        command = [tool_name] + parameters
        
        if input_file:
            # Add input file parameter based on tool
            if tool_name == 'volatility':
                command.extend(['-f', input_file])
            elif tool_name == 'tshark':
                command.extend(['-r', input_file])
            elif tool_name == 'foremost':
                command.extend(['-i', input_file])
        
        if output_dir:
            # Add output directory parameter based on tool
            if tool_name == 'foremost':
                command.extend(['-o', output_dir])
            elif tool_name == 'tshark':
                command.extend(['-w', os.path.join(output_dir, f"{tool_name}_output.pcap")])
        
        try:
            console.print(f"[cyan]Executing forensics command: {' '.join(command)}[/cyan]")
            
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                cwd=output_dir if output_dir else None
            )
            
            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr,
                'command': ' '.join(command),
                'return_code': result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': f"Command timed out after 5 minutes",
                'output': '',
                'command': ' '.join(command)
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Execution error: {str(e)}",
                'output': '',
                'command': ' '.join(command)
            }
    
    def get_installation_commands(self) -> Dict[str, str]:
        """Get installation commands for missing forensics tools."""
        return {
            'volatility3': 'pip install volatility3',
            'sleuthkit': 'sudo apt-get install sleuthkit',
            'foremost': 'sudo apt-get install foremost',
            'binwalk': 'sudo apt-get install binwalk',
            'tshark': 'sudo apt-get install tshark',
            'autopsy': 'sudo apt-get install autopsy',
            'strings': 'sudo apt-get install binutils'  # strings is part of binutils
        }
    
    def prompt_tool_installation(self, missing_tools: List[str]) -> bool:
        """Prompt user to install missing forensics tools."""
        if not missing_tools:
            return True
            
        console.print(Panel.fit(
            Text.assemble(
                ("🔧 Missing Forensics Tools Detected", "bold yellow"),
                ("\n\n", ""),
                ("LINA can install these tools automatically to enable full forensics capabilities.", "cyan"),
                ("\n", ""),
                ("Missing tools: ", "white"),
                (", ".join(missing_tools), "red")
            ),
            title="⚠️  TOOL INSTALLATION REQUIRED",
            border_style="yellow"
        ))
        
        # Show installation commands
        install_commands = self.get_installation_commands()
        commands_table = Table(title="📦 Installation Commands", show_header=True, border_style="cyan")
        commands_table.add_column("Tool", style="bold white", width=15)
        commands_table.add_column("Installation Command", style="green", width=50)
        
        for tool in missing_tools:
            if tool in install_commands:
                commands_table.add_row(tool, install_commands[tool])
        
        console.print(commands_table)
        
        # Ask user if they want to install
        try:
            from rich.prompt import Confirm
            install_choice = Confirm.ask("\n🤔 Would you like LINA to install these tools automatically?", default=True)
            return install_choice
        except ImportError:
            # Fallback if rich.prompt is not available
            response = input("\n🤔 Would you like LINA to install these tools automatically? (y/N): ").lower()
            return response in ['y', 'yes']
    
    def install_missing_tools(self, missing_tools: List[str]) -> Dict[str, bool]:
        """Install missing forensics tools."""
        install_results = {}
        install_commands = self.get_installation_commands()
        
        console.print(Panel.fit(
            Text.assemble(
                ("🚀 Installing Missing Forensics Tools", "bold green"),
                ("\n\n", ""),
                ("LINA is installing the required tools...", "cyan")
            ),
            title="📦 INSTALLATION IN PROGRESS",
            border_style="green"
        ))
        
        for tool in missing_tools:
            if tool in install_commands:
                console.print(f"[cyan]Installing {tool}...[/cyan]")
                try:
                    import subprocess
                    result = subprocess.run(
                        install_commands[tool].split(),
                        capture_output=True,
                        text=True,
                        timeout=300  # 5 minute timeout
                    )
                    
                    if result.returncode == 0:
                        console.print(f"[green]✅ {tool} installed successfully![/green]")
                        install_results[tool] = True
                    else:
                        console.print(f"[red]❌ Failed to install {tool}: {result.stderr}[/red]")
                        install_results[tool] = False
                        
                except subprocess.TimeoutExpired:
                    console.print(f"[red]❌ Installation of {tool} timed out[/red]")
                    install_results[tool] = False
                except Exception as e:
                    console.print(f"[red]❌ Error installing {tool}: {e}[/red]")
                    install_results[tool] = False
        
        return install_results
    
    def auto_install_missing_tools(self) -> bool:
        """Automatically detect and install missing forensics tools."""
        missing_tools = set(self.forensics_tools.keys()) - set(self.available_tools)
        
        if not missing_tools:
            console.print("[green]✅ All forensics tools are available![/green]")
            return True
        
        # Prompt user for installation
        if self.prompt_tool_installation(list(missing_tools)):
            install_results = self.install_missing_tools(list(missing_tools))
            
            # Check if installation was successful
            successful_installs = [tool for tool, success in install_results.items() if success]
            failed_installs = [tool for tool, success in install_results.items() if not success]
            
            if successful_installs:
                console.print(f"[green]✅ Successfully installed: {', '.join(successful_installs)}[/green]")
                # Refresh available tools
                self.available_tools = self._get_available_tools()
            
            if failed_installs:
                console.print(f"[red]❌ Failed to install: {', '.join(failed_installs)}[/red]")
                console.print("[yellow]You can install these manually using the commands shown above.[/yellow]")
            
            return len(failed_installs) == 0
        else:
            console.print("[yellow]⚠️  Installation cancelled. Some forensics capabilities may be limited.[/yellow]")
            return False
    
    def display_forensics_status(self) -> None:
        """Display forensics tools status."""
        console.print(Panel.fit(
            Text.assemble(
                ("🔬 LINA Forensics Manager Status", "bold yellow"),
                ("\n\n", ""),
                ("Digital Forensics Tools Integration", "cyan")
            ),
            title="🔍 FORENSICS STATUS",
            border_style="yellow"
        ))
        
        # Available tools table
        if self.available_tools:
            tools_table = Table(title="✅ Available Forensics Tools", show_header=True, border_style="green")
            tools_table.add_column("Tool", style="bold white", width=15)
            tools_table.add_column("Description", style="cyan", width=40)
            tools_table.add_column("Parameters", style="green", width=10)
            
            for tool in self.available_tools:
                if tool in self.forensics_tools:
                    params_count = len(self.forensics_tools[tool].get('parameters', []))
                    tools_table.add_row(tool, f"Digital forensics tool", f"{params_count} params")
            
            console.print(tools_table)
        else:
            console.print("[red]No forensics tools are currently available on this system.[/red]")
        
        # Missing tools
        missing_tools = set(self.forensics_tools.keys()) - set(self.available_tools)
        if missing_tools:
            console.print(Panel(
                Text.assemble(
                    ("⚠️  Missing Tools:", "bold red"),
                    ("\n", ""),
                    (", ".join(missing_tools), "red"),
                    ("\n\n", ""),
                    ("Install these tools to enable full forensics capabilities.", "yellow")
                ),
                title="⚠️  MISSING TOOLS",
                border_style="red"
            ))
            
            # Show installation commands
            install_commands = self.get_installation_commands()
            console.print(Panel(
                Text.assemble(
                    ("📦 Installation Commands:", "bold cyan"),
                    ("\n", ""),
                    *[f"{tool}: {cmd}\n" for tool, cmd in install_commands.items() if tool in missing_tools]
                ),
                title="🔧 INSTALLATION GUIDE",
                border_style="cyan"
            ))
    
    def get_forensics_recommendations(self, analysis_type: str) -> List[str]:
        """
        Get forensics tool recommendations based on analysis type.
        
        Args:
            analysis_type: Type of forensics analysis (memory, disk, network, etc.)
            
        Returns:
            List of recommended tools
        """
        recommendations = {
            'memory': ['volatility3', 'strings'],
            'disk': ['sleuthkit', 'foremost', 'strings'],
            'network': ['tshark', 'strings'],
            'general': ['autopsy', 'sleuthkit', 'strings'],
            'malware': ['volatility3', 'strings', 'sleuthkit'],
            'timeline': ['sleuthkit', 'volatility3'],
            'recovery': ['foremost', 'sleuthkit'],
            'firmware': ['binwalk', 'strings']
        }
        
        return recommendations.get(analysis_type.lower(), ['autopsy', 'sleuthkit', 'strings'])
    
    def create_forensics_workflow(self, analysis_type: str, input_file: str, 
                                 output_dir: str) -> List[Dict[str, Any]]:
        """
        Create a forensics workflow for the specified analysis type.
        
        Args:
            analysis_type: Type of forensics analysis
            input_file: Input file path
            output_dir: Output directory
            
        Returns:
            List of workflow steps
        """
        recommendations = self.get_forensics_recommendations(analysis_type)
        workflow = []
        
        for tool in recommendations:
            if self.is_tool_available(tool):
                if tool == 'volatility3':
                    workflow.append({
                        'tool': tool,
                        'command': f"volatility3 -f {input_file} --profile=Win7SP1x64 pslist",
                        'description': "List running processes from memory dump"
                    })
                elif tool == 'sleuthkit':
                    workflow.append({
                        'tool': tool,
                        'command': f"sleuthkit mmls {input_file}",
                        'description': "List partition table from disk image"
                    })
                elif tool == 'tshark':
                    workflow.append({
                        'tool': tool,
                        'command': f"tshark -r {input_file} -T fields -e frame.number -e frame.time",
                        'description': "Extract packet information from pcap file"
                    })
                elif tool == 'strings':
                    workflow.append({
                        'tool': tool,
                        'command': f"strings -a {input_file} > {output_dir}/strings_output.txt",
                        'description': "Extract ASCII strings from file"
                    })
                elif tool == 'foremost':
                    workflow.append({
                        'tool': tool,
                        'command': f"foremost -t all -i {input_file} -o {output_dir}/foremost_output",
                        'description': "Recover all known file types from disk image"
                    })
                elif tool == 'binwalk':
                    workflow.append({
                        'tool': tool,
                        'command': f"binwalk -e {input_file} -C {output_dir}/binwalk_output",
                        'description': "Extract files from firmware"
                    })
                elif tool == 'autopsy':
                    workflow.append({
                        'tool': tool,
                        'command': f"autopsy --case {output_dir}/autopsy_case --data {input_file}",
                        'description': "Create autopsy case for analysis"
                    })
        
        return workflow


def get_forensics_manager() -> ForensicsManager:
    """Get the forensics manager instance."""
    return ForensicsManager()
