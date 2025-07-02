import os
import fnmatch
from typing import List, Dict, Any
from .base_tool import BaseTool

try:
    from .sandbox_control import is_sandbox_enabled
except ImportError:
    def is_sandbox_enabled():
        return True

SANDBOX_ROOT = os.path.expanduser("~/.tilde-cli/sandbox")
ENCRYPTION_KEY_FILE = os.path.expanduser("~/.tilde-cli/.key")

def is_path_in_sandbox(file_path: str) -> bool:
    abs_path = os.path.abspath(file_path)
    return abs_path.startswith(os.path.abspath(SANDBOX_ROOT))

class FileSearchTool(BaseTool):
    @property
    def name(self) -> str:
        return "file_search"

    @property
    def description(self) -> str:
        return "Searches for files matching a pattern in a given directory."

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "pattern": {"type": "string", "description": "The glob pattern to search for (e.g., *.txt, **/*.py)"},
                "path": {"type": "string", "description": "The directory to start the search from (default: current directory)"}
            },
            "required": ["pattern"]
        }

    def execute(self, pattern: str, path: str = ".") -> List[str]:
        # Expand ~ to home directory before sandbox check
        path = os.path.expanduser(path)
        # Sandbox enforcement (disable if sandbox is disabled)
        if is_sandbox_enabled() and not is_path_in_sandbox(path):
            return [f"Security error: File search is only allowed inside {SANDBOX_ROOT}. Tried to access: {path}"]
        matches = []
        for root, _, filenames in os.walk(path):
            for filename in fnmatch.filter(filenames, pattern):
                matches.append(os.path.join(root, filename))
        return matches
