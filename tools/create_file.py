import os
from typing import Dict, Any
from .base_tool import BaseTool
import base64
from cryptography.fernet import Fernet

SANDBOX_ROOT = os.path.expanduser("~/.tilde-cli/sandbox")
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

class CreateFileTool(BaseTool):
    @property
    def name(self) -> str:
        return "createFile"

    @property
    def description(self) -> str:
        return "Writes content to a specified file, creating it if it doesn't exist."

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "The absolute path to the file to write."},
                "content": {"type": "string", "description": "The content to write to the file."}
            },
            "required": ["file_path", "content"]
        }

    def execute(self, file_path: str, content: str, encrypt: bool = False) -> str:
        # Expand ~ to home directory
        file_path = os.path.expanduser(file_path)
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            if encrypt:
                key = get_encryption_key()
                fernet = Fernet(key)
                encrypted = fernet.encrypt(content.encode('utf-8'))
                with open(file_path, 'wb') as f:
                    f.write(encrypted)
            else:
                with open(file_path, 'w') as f:
                    f.write(content)
            return f"Successfully wrote to {file_path}"
        except Exception as e:
            return f"Error writing to file {file_path}: {e}"
