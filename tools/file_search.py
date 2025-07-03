import os
import fnmatch
from typing import List, Dict, Any
from .base_tool import BaseTool

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
        # Expand ~ to home directory
        path = os.path.expanduser(path)
        matches = []
        for root, _, filenames in os.walk(path):
            for filename in fnmatch.filter(filenames, pattern):
                matches.append(os.path.join(root, filename))
        return matches
