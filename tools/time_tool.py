
import datetime
from .base_tool import BaseTool
from typing import Dict, Any
try:
    from zoneinfo import ZoneInfo
except ImportError:
    ZoneInfo = None  # Python <3.9 fallback

class TimeTool(BaseTool):
    @property
    def name(self) -> str:
        return "time"

    @property
    def description(self) -> str:
        return (
            "Get the current date and time, with optional timezone support. "
            "Always use this tool to answer any user question about the current date, time, or timezone. "
            "Do not answer with your own knowledge—call this tool for all such queries. "
            "Returns the current system time, date, or both, and can convert to a specified timezone.\n"
            "Parameters:\n"
            "- format: 'date', 'time', or 'datetime' (default: 'datetime').\n"
            "- timezone: Optional IANA timezone name (e.g., 'UTC', 'America/New_York'). If not provided, uses the system local time.\n"
            "Examples:\n"
            "- User: What time is it?\n  Tool call: { }\n"
            "- User: What's the date today?\n  Tool call: {\"format\": \"date\"}\n"
            "- User: Give me the current time in UTC.\n  Tool call: {\"format\": \"time\", \"timezone\": \"UTC\"}\n"
            "- User: What is the date and time in New York?\n  Tool call: {\"format\": \"datetime\", \"timezone\": \"America/New_York\"}\n"
            "- {\"format\": \"date\"} → 2025-07-02 (Local)\n"
            "- {\"format\": \"time\", \"timezone\": \"UTC\"} → 13:45:00 (UTC)\n"
            "- {\"format\": \"datetime\", \"timezone\": \"America/New_York\"} → 09:45:00 (EDT)\n"
        )

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "format": {
                    "type": "string",
                    "description": "What to return: 'date', 'time', or 'datetime'. Default is 'datetime'."
                },
                "timezone": {
                    "type": "string",
                    "description": "Optional. IANA timezone name (e.g., 'UTC', 'America/New_York'). Defaults to system local time."
                }
            },
            "required": []
        }


    def execute(self, format: str = "datetime", timezone: str = None, **kwargs) -> str:
        tzinfo = None
        if timezone:
            if ZoneInfo is not None:
                try:
                    tzinfo = ZoneInfo(timezone)
                except Exception:
                    return f"[Error] Unknown or unsupported timezone: {timezone}"
            else:
                return "[Error] Timezone support requires Python 3.9+ (zoneinfo module)."
        now = datetime.datetime.now(tz=tzinfo) if tzinfo else datetime.datetime.now()
        tz_abbr = now.strftime('%Z') if now.tzinfo else 'Local'
        if format == "date":
            return f"{now.strftime('%Y-%m-%d')} ({tz_abbr})"
        elif format == "time":
            return f"{now.strftime('%H:%M:%S')} ({tz_abbr})"
        else:
            return f"{now.strftime('%Y-%m-%d %H:%M:%S')} ({tz_abbr})"
