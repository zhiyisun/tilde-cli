from .base_tool import BaseTool
from memory import MemoryManager
from typing import Any, Dict

class ListMemoryTool(BaseTool):
    @property
    def name(self) -> str:
        return "list_memory"

    @property
    def description(self) -> str:
        return (
            "List all facts or information stored in the assistant's long-term memory. "
            "Use this tool ONLY to display or show the user's memory. This tool does NOT add or change memory. "
            "No parameters are needed. "
            "Example: If the user says 'show my memory', 'list my facts', or 'what do you know about me?', call this tool."
        )

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {},
            "required": []
        }

    def execute(self, **kwargs) -> Any:
        mm = MemoryManager()
        return mm.list_facts()

class AddMemoryTool(BaseTool):
    @property
    def name(self) -> str:
        return "add_memory"

    @property
    def description(self) -> str:
        return (
            "Add a new fact or information to the assistant's long-term memory. "
            "Use this tool ONLY to store a new fact, note, or piece of information for future reference. "
            "This tool does NOT list or show memory. "
            "Example: If the user says 'remember that my favorite color is blue', 'add to my memory: I live in Paris', or 'store the fact that my birthday is July 2', call this tool."
        )

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "fact": {
                    "type": "string",
                    "description": "The fact or information to add to memory."
                }
            },
            "required": ["fact"]
        }

    def execute(self, fact: str, **kwargs) -> Any:
        mm = MemoryManager()
        added = mm.add_fact(fact)
        if added:
            return f"Fact added: {fact}"
        else:
            return f"Fact already exists: {fact}"
