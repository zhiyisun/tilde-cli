
import os
from typing import Dict, Any
from .base_tool import BaseTool
import base64
from cryptography.fernet import Fernet
try:
    from .sandbox_control import is_sandbox_enabled
except ImportError:
    def is_sandbox_enabled():
        return True

# Define a sandbox root directory (e.g., user's home or workspace)
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

class EditFileTool(BaseTool):
    @property
    def name(self) -> str:
        return "edit_file"

    @property
    def description(self) -> str:
        return "Edit a file by replacing text. Finds and replaces text in the file, with optional diff/approval."

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "File to edit."},
                "old_string": {"type": "string", "description": "Text to replace."},
                "new_string": {"type": "string", "description": "Replacement text."},
                "require_approval": {"type": "boolean", "description": "Require user approval before saving changes (optional)."}
            },
            "required": ["file_path", "old_string", "new_string"]
        }

    def execute(self, file_path: str, old_string: str, new_string: str, require_approval: bool = False, encrypt: bool = False) -> str:
        # Expand ~ to home directory before sandbox check
        file_path = os.path.expanduser(file_path)
        # Sandbox enforcement (disable if sandbox is disabled)
        if is_sandbox_enabled() and not is_path_in_sandbox(file_path):
            return f"Security error: Editing is only allowed inside {SANDBOX_ROOT}. Attempted path: {file_path}"
        try:
            if encrypt:
                key = get_encryption_key()
                fernet = Fernet(key)
                with open(file_path, 'rb') as f:
                    encrypted = f.read()
                content = fernet.decrypt(encrypted).decode('utf-8')
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            if old_string not in content:
                return f"'{old_string}' not found in {file_path}. No changes made."
            new_content = content.replace(old_string, new_string)
            if require_approval:
                print("--- Diff Preview ---")
                import difflib
                diff = difflib.unified_diff(content.splitlines(), new_content.splitlines(), fromfile='before', tofile='after', lineterm='')
                for line in diff:
                    print(line)
                confirm = input("Apply these changes? (yes/no): ")
                if confirm.lower() != 'yes':
                    return "Edit cancelled by user."
            if encrypt:
                encrypted = fernet.encrypt(new_content.encode('utf-8'))
                with open(file_path, 'wb') as f:
                    f.write(encrypted)
            else:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
            return f"Successfully edited {file_path}."
        except Exception as e:
            return f"Error editing file: {e}"
