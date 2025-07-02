from .base_adapter import BaseModelAdapter
import json

class GemmaModelAdapter(BaseModelAdapter):
    def build_tool_definitions(self, tools):
        # Gemma3:27b expects OpenAI Function Calling API format: [{"type": "function", "function": {...}}]
        return [{"type": "function", "function": tool.to_dict()} for tool in tools.values()]

    def parse_response_stream(self, response_generator):
        """
        Yields (tool_call, text_chunk) pairs. Only one of tool_call or text_chunk will be not None per yield.
        Looks for OpenAI-style function_call in the response.
        """
        for chunk in response_generator:
            # If chunk is a dict with 'function_call', treat as tool call
            if isinstance(chunk, dict) and "function_call" in chunk:
                func = chunk["function_call"]
                tool_call = {
                    "tool_name": func.get("name"),
                    "parameters": func.get("arguments", {})
                }
                yield (tool_call, None)
                continue
            # If chunk is a JSON string, try to parse
            if isinstance(chunk, str):
                try:
                    obj = json.loads(chunk)
                    if isinstance(obj, dict) and "function_call" in obj:
                        func = obj["function_call"]
                        tool_call = {
                            "tool_name": func.get("name"),
                            "parameters": func.get("arguments", {})
                        }
                        yield (tool_call, None)
                        continue
                except Exception:
                    pass
            yield (None, chunk)
