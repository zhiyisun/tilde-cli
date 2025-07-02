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

def is_path_in_sandbox(file_path: str) -> bool:
    abs_path = os.path.abspath(file_path)
    return abs_path.startswith(os.path.abspath(SANDBOX_ROOT))

try:
    from .sandbox_control import is_sandbox_enabled
except ImportError:
    def is_sandbox_enabled():
        return True

class ReadFileTool(BaseTool):
    @property
    def name(self) -> str:
        return "read_file"

    @property
    def description(self) -> str:
        return "Reads the content of a specified file."

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "The absolute path to the file to read."}
            },
            "required": ["file_path"]
        }

    def execute(self, file_path: str, decrypt: bool = False) -> str:
        # Expand ~ to home directory before sandbox check
        file_path = os.path.expanduser(file_path)
        # Sandbox enforcement (disable if sandbox is disabled)
        if is_sandbox_enabled() and not is_path_in_sandbox(file_path):
            return f"Security error: Reading is only allowed inside {SANDBOX_ROOT}. Attempted path: {file_path}"
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
