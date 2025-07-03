import os
import re
import fnmatch
from typing import Dict, Any, List
from .base_tool import BaseTool
import base64
from cryptography.fernet import Fernet

class GrepTool(BaseTool):
    @property
    def name(self) -> str:
        return "grep"

    @property
    def description(self) -> str:
        return "Search for a regex pattern in files. Returns matching lines and file locations."

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "pattern": {"type": "string", "description": "Regex to search for."},
                "path": {"type": "string", "description": "Directory to search in (default: .)"},
                "include": {"type": "string", "description": "File pattern to include (e.g., *.py) (optional)"}
            },
            "required": ["pattern"]
        }

    def execute(self, pattern: str, path: str = ".", include: str = None, decrypt: bool = False) -> List[str]:
        # Expand ~ to home directory
        path = os.path.expanduser(path)
        results = []
        regex = re.compile(pattern)
        key = None
        fernet = None
        if decrypt:
            key = self._get_encryption_key()
            fernet = Fernet(key)
        for root, _, files in os.walk(path):
            for fname in files:
                if include and not fnmatch.fnmatch(fname, include):
                    continue
                fpath = os.path.join(root, fname)
                try:
                    if decrypt:
                        with open(fpath, 'rb') as f:
                            encrypted = f.read()
                        content = fernet.decrypt(encrypted).decode('utf-8')
                        for i, line in enumerate(content.splitlines(), 1):
                            if regex.search(line):
                                results.append(f"{fpath}:{i}: {line.strip()}")
                    else:
                        with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                            for i, line in enumerate(f, 1):
                                if regex.search(line):
                                    results.append(f"{fpath}:{i}: {line.strip()}")
                except Exception:
                    continue
        return results

    def _get_encryption_key(self):
        if not os.path.exists(ENCRYPTION_KEY_FILE):
            os.makedirs(os.path.dirname(ENCRYPTION_KEY_FILE), exist_ok=True)
            key = Fernet.generate_key()
            with open(ENCRYPTION_KEY_FILE, 'wb') as f:
                f.write(key)
        else:
            with open(ENCRYPTION_KEY_FILE, 'rb') as f:
                key = f.read()
        return key
