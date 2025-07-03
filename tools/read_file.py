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

class ReadFileTool(BaseTool):
    @property
    def name(self) -> str:
        return "read_file"

    @property
    def description(self) -> str:
        return "Reads the content of a specified file. Accepts either 'file_path' or 'path' as the file location."

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "The absolute path to the file to read."},
                "path": {"type": "string", "description": "Alias for file_path."}
            },
            "required": [],
        }

    def execute(self, file_path: str = None, path: str = None, decrypt: bool = False) -> str:
        # Accept either 'file_path' or 'path'
        file_path = file_path or path
        if not file_path:
            return "Error: No file path provided."
        # Expand ~ to home directory
        file_path = os.path.expanduser(file_path)
        try:
            if decrypt:
                key = get_encryption_key()
                fernet = Fernet(key)
                with open(file_path, 'rb') as f:
                    encrypted = f.read()
                content = fernet.decrypt(encrypted).decode('utf-8')
            else:
                with open(file_path, 'r') as f:
                    content = f.read()
            return content
        except FileNotFoundError:
            return f"Error: File not found at {file_path}"
        except Exception as e:
            return f"Error reading file {file_path}: {e}"
