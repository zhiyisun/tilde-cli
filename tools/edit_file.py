import os
from typing import Dict, Any
from .base_tool import BaseTool
import base64
from cryptography.fernet import Fernet

ENCRYPTION_KEY_FILE = os.path.expanduser("~/.tilde-cli/.key")

def get_encryption_key():
    if not os.path.exists(ENCRYPTION_KEY_FILE):
        os.makedirs(os.path.dirname(ENCRYPTION_KEY_FILE), exist_ok=True)
        key = Fernet.generate_key()
        with open(ENCRYPTION_KEY_FILE, 'wb') as f:
            f.write(key)
    else:
        with open(ENCRYPTION_KEY_FILE, 'rb') as f:
            key = f.read()
    return key

class EditFileTool(BaseTool):
    @property
    def name(self) -> str:
        return "edit_file"

    @property
    def description(self) -> str:
        return "Edit the content of a specified file."

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "The absolute path to the file to edit."},
                "content": {"type": "string", "description": "The new content to write to the file."}
            },
            "required": ["file_path", "content"]
        }

    def execute(self, file_path: str, content: str) -> str:
        # Expand ~ to home directory
        file_path = os.path.expanduser(file_path)
        try:
            with open(file_path, 'w') as f:
                f.write(content)
            return f"Successfully edited {file_path}"
        except Exception as e:
            return f"Error editing file {file_path}: {e}"
