from .base_adapter import BaseModelAdapter
import json
import logging

class QwenModelAdapter(BaseModelAdapter):
    def build_tool_definitions(self, tools):
        # Qwen expects [{"type": "function", "function": ...}]
        return [{"type": "function", "function": tool.to_dict()} for tool in tools.values()]

    def parse_response_stream(self, response_generator):
        """
        Yields (tool_call, text_chunk) pairs. Only one of tool_call or text_chunk will be not None per yield.
        Skips <think> tags, detects tool calls as dict or JSON string.
        """
        for chunk in response_generator:
            if isinstance(chunk, str) and chunk.strip().lower().startswith("<think"):
                yield (None, chunk)
                continue
            if isinstance(chunk, dict):
                if ("tool_name" in chunk or "name" in chunk):
                    yield (chunk, None)
                    continue
            elif isinstance(chunk, str):
                try:
                    tool_call_candidate = json.loads(chunk)
                    if isinstance(tool_call_candidate, dict) and ("tool_name" in tool_call_candidate or "name" in tool_call_candidate):
                        yield (tool_call_candidate, None)
                        continue
                except Exception:
                    pass
            yield (None, chunk)
