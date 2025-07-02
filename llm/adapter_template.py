from .model_adapter import BaseModelAdapter

class YourModelAdapter(BaseModelAdapter):
    def build_tool_definitions(self, tools):
        # TODO: Return tool definitions in the format required by your model
        raise NotImplementedError("Implement build_tool_definitions for your model.")

    def parse_response_stream(self, response_generator):
        """
        TODO: Parse the response stream from your model.
        Yields (tool_call, text_chunk) pairs. Only one of tool_call or text_chunk will be not None per yield.
        """
        raise NotImplementedError("Implement parse_response_stream for your model.")
