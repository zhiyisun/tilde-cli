from .base_tool import BaseTool
from config_utils import Config
from typing import Dict, Any

class ThinkToggleTool(BaseTool):
    @property
    def name(self) -> str:
        return "think_toggle"

    @property
    def description(self) -> str:
        return (
            "Enable or disable showing the <think>...</think> section in LLM responses. "
            "Set 'enabled' to true to show <think> blocks, or false to hide them. "
            "\nParameters:\n"
            "- enabled: boolean. If true, show <think> blocks. If false, hide them.\n"
            "\nExamples:\n"
            "- {\"enabled\": true}   # Show <think> sections in LLM output\n"
            "- {\"enabled\": false}  # Hide <think> sections in LLM output\n"
        )

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "enabled": {
                    "type": "boolean",
                    "description": "If true, show <think> blocks. If false, hide them."
                },
                "status": {
                    "type": "boolean",
                    "description": "If true, query the current state instead of changing it. If set, 'enabled' is ignored."
                }
            },
            "required": [],
        }

    def execute(self, enabled: bool = None, status: bool = None, **kwargs) -> str:
        if status:
            is_on = not getattr(Config, 'HIDE_THINK', True)
            return f"<think> sections are currently {'shown' if is_on else 'hidden'} in LLM responses."
        if enabled is None:
            return "Please provide 'enabled': true or false, or 'status': true to query the current state."
        Config.HIDE_THINK = not enabled
        Config.set_config('HIDE_THINK', not enabled)
        if enabled:
            return "<think> sections will now be shown in LLM responses."
        else:
            return "<think> sections will now be hidden in LLM responses."
