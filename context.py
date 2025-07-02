import json
import os
from typing import List, Dict, Any, Optional

SESSION_DIR = os.path.expanduser("~/.tilde-cli/sessions")
os.makedirs(SESSION_DIR, exist_ok=True)

class Session:
    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id or "default"
        self.history: List[Dict[str, Any]] = []  # Each turn: {"role": "user"/"assistant"/"tool", "content": ...}
        self.metadata: Dict[str, Any] = {}

    def add_turn(self, role: str, content: str, tool: Optional[str] = None):
        turn = {"role": role, "content": content}
        if tool:
            turn["tool"] = tool
        self.history.append(turn)

    def get_recent(self, n: int = 10) -> List[Dict[str, Any]]:
        return self.history[-n:]

    def save(self):
        path = os.path.join(SESSION_DIR, f"{self.session_id}.json")
        with open(path, "w") as f:
            json.dump({"history": self.history, "metadata": self.metadata}, f, indent=2)

    def load(self):
        path = os.path.join(SESSION_DIR, f"{self.session_id}.json")
        if os.path.exists(path):
            with open(path, "r") as f:
                data = json.load(f)
                self.history = data.get("history", [])
                self.metadata = data.get("metadata", {})

    def reset(self):
        self.history = []
        self.metadata = {}

class ContextManager:
    def __init__(self):
        self.conversation_history: List[Dict[str, str]] = []

    def add_message(self, role: str, content: str):
        self.conversation_history.append({"role": role, "content": content})

    def get_conversation_history(self, limit: int = -1) -> List[Dict[str, str]]:
        if limit == -1:
            return self.conversation_history
        return self.conversation_history[-limit:]

    def get_full_context(self) -> List[Dict[str, str]]:
        # This is a simplified example. In a real scenario, you'd manage token limits.
        return self.conversation_history

    def clear_context(self):
        self.conversation_history = []
