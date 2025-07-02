from abc import ABC, abstractmethod

class BaseModelAdapter(ABC):
    """Base class for model-specific prompt/response handling."""
    def __init__(self, model_name):
        self.model_name = model_name

    @abstractmethod
    def build_tool_definitions(self, tools):
        """Return the tool definitions in the format required by the model."""
        pass

    @abstractmethod
    def parse_response_stream(self, response_generator):
        """Yield (tool_call, text_chunk) pairs from the model's response stream."""
        pass
