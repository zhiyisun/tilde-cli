from abc import ABC, abstractmethod
from typing import Dict, Any, List, Iterator, Union, TypedDict

class ToolCall(TypedDict):
    tool_name: str
    parameters: Dict[str, Any]

class LLMBackend(ABC):
    @abstractmethod
    def generate_text(self, prompt: str, stream: bool = False, **kwargs) -> Union[str, Iterator[str]]:
        pass

    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], tools: List[Dict[str, Any]] = None, stream: bool = False, **kwargs) -> Union[str, Iterator[str], ToolCall]:
        pass

    @abstractmethod
    def get_embedding(self, text: str) -> List[float]:
        pass
