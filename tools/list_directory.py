import os
import fnmatch
from typing import Dict, Any, List
from .base_tool import BaseTool

class ListDirectoryTool(BaseTool):
    @property
    def name(self) -> str:
        return "ls"

    @property
    def description(self) -> str:
        return "List files and directories in a given path, with optional ignore patterns."

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Directory to list (default: current directory)"},
                "ignore": {"type": "array", "items": {"type": "string"}, "description": "Glob patterns to ignore (optional)"},
                "respect_git_ignore": {"type": "boolean", "description": "Whether to respect .gitignore (optional)"}
            },
            "required": []
        }

    def execute(self, path: str = ".", ignore: List[str] = None, respect_git_ignore: bool = False) -> List[str]:
        # Expand ~ to home directory
        path = os.path.expanduser(path)
        entries = []
        ignore = ignore or []
        try:
            # If respect_git_ignore is True, parse .gitignore patterns
            gitignore_patterns = []
            if respect_git_ignore:
                gitignore_path = os.path.join(path, '.gitignore')
                if os.path.exists(gitignore_path):
                    with open(gitignore_path, 'r') as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#'):
                                gitignore_patterns.append(line)
            for entry in os.listdir(path):
                skip = False
                for pattern in ignore:
                    if fnmatch.fnmatch(entry, pattern):
                        skip = True
                        break
                if not skip and respect_git_ignore:
                    for pattern in gitignore_patterns:
                        if fnmatch.fnmatch(entry, pattern):
                            skip = True
                            break
                if skip:
                    continue
                entries.append(entry)
            return entries
        except Exception as e:
            return [f"Error: {e}"]
