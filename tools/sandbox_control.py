from .base_tool import BaseTool
from typing import Any, Dict

# Global flag for sandbox security (default: enabled)
SANDBOX_ENABLED = True

def set_sandbox(enabled: bool):
    global SANDBOX_ENABLED
    SANDBOX_ENABLED = enabled

def is_sandbox_enabled() -> bool:
    return SANDBOX_ENABLED

class SandboxControlTool(BaseTool):
    @property
    def name(self) -> str:
        return "sandbox_control"

    @property
    def description(self) -> str:
        return "Check or set the sandbox security limitation for tool execution (e.g., shell commands)."

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "enabled": {"type": "boolean", "description": "Enable (True) or disable (False) the sandbox security."},
                "status": {"type": "boolean", "description": "If True, just return the current sandbox status."}
            },
            "anyOf": [
                {"required": ["enabled"]},
                {"required": ["status"]}
            ]
        }

    def execute(self, enabled: bool = None, status: bool = None, **kwargs) -> str:
        if status:
            return f"Sandbox security is {'ENABLED' if is_sandbox_enabled() else 'DISABLED'}."
        if enabled is not None:
            set_sandbox(enabled)
            return f"Sandbox security is now {'ENABLED' if enabled else 'DISABLED'}."
        return "Specify either 'enabled' to set or 'status' to check sandbox security."
