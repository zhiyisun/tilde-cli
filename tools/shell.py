import subprocess
import shlex
from typing import Dict, Any

from .base_tool import BaseTool
try:
    from .sandbox_control import is_sandbox_enabled
except ImportError:
    def is_sandbox_enabled():
        return True

class ShellTool(BaseTool):
    @property
    def name(self) -> str:
        return "shell"

    @property
    def description(self) -> str:
        return (
            "Run any Linux shell command or application.\n"
            "- Use this tool if no other tool can fulfill the user's request.\n"
            "- Supports any command-line program, script, or utility available in the system shell.\n"
            "- Returns both standard output (stdout) and error (stderr).\n"
            "- For long-running commands (loops, scripts with sleep), specify the estimated execution time in seconds with the 'timeout' parameter.\n"
            "  - If not specified, the command will be terminated after 60 seconds.\n"
            "  - To run until finished, set 'timeout' to 0.\n"
            "- If the command produces multi-line or iterative output, consider redirecting output to a file (e.g., 'output.txt') for later analysis.\n\n"
            "Example usage:\n"
            "- List files: {\"command\": \"ls -l\"}\n"
            "- Long loop for 120 seconds: {\"command\": \"for i in {1..10}; do echo $i; sleep 12; done\", \"timeout\": 120}\n"
            "- Run until finished: {\"command\": \"bash myscript.sh\", \"timeout\": 0}\n"
            "- Save output to file: {\"command\": \"ls -l > output.txt 2>&1\"}"
        )

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "The shell command to execute."}
            },
            "required": ["command"]
        }

    def execute(self, command: str, require_confirmation: bool = True, working_directory: str = None, timeout: int = None) -> Dict[str, str]:
        # Security: require explicit confirmation unless overridden or sandbox is disabled
        sandbox = is_sandbox_enabled()
        if require_confirmation and sandbox:
            print(f"[SECURITY WARNING] About to execute shell command: {command}")
            confirm = input("Are you sure you want to run this command? (yes/no): ")
            if confirm.lower() != "yes":
                return {"error": "Shell command execution cancelled by user."}
        # Timeout logic
        if timeout is None:
            timeout = 60  # default
        if timeout == 0:
            timeout_arg = None  # Wait until finished
        else:
            timeout_arg = timeout
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                check=True,
                cwd=working_directory or None,
                timeout=timeout_arg
            )
            return {"stdout": result.stdout, "stderr": result.stderr}
        except subprocess.TimeoutExpired as e:
            return {"stdout": e.stdout or '', "stderr": e.stderr or '', "error": f"Command timed out after {timeout} seconds."}
        except subprocess.CalledProcessError as e:
            return {"stdout": e.stdout, "stderr": e.stderr, "error": str(e)}
