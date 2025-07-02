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
        return "Executes a shell command."

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "The shell command to execute."}
            },
            "required": ["command"]
        }

    def execute(self, command: str, require_confirmation: bool = True, working_directory: str = None) -> Dict[str, str]:
        # Security: require explicit confirmation unless overridden or sandbox is disabled
        sandbox = is_sandbox_enabled()
        if require_confirmation and sandbox:
            print(f"[SECURITY WARNING] About to execute shell command: {command}")
            confirm = input("Are you sure you want to run this command? (yes/no): ")
            if confirm.lower() != "yes":
                return {"error": "Shell command execution cancelled by user."}
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                check=True,
                cwd=working_directory or None
            )
            return {"stdout": result.stdout, "stderr": result.stderr}
        except subprocess.CalledProcessError as e:
            return {"stdout": e.stdout, "stderr": e.stderr, "error": str(e)}
