import requests
import json
from typing import Dict, Any, List, Iterator, Union
from .backend import LLMBackend, ToolCall

class OllamaBackend(LLMBackend):
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama2"):
        self.base_url = base_url
        self.model = model

    def generate_text(self, prompt: str, **kwargs) -> str:
        url = f"{self.base_url}/api/generate"
        payload = {"model": self.model, "prompt": prompt, **kwargs}
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()["response"]

    def chat(self, messages: List[Dict[str, str]], tools: List[Dict[str, Any]] = None, stream: bool = False, **kwargs) -> Union[str, Iterator[str], ToolCall]:
        url = f"{self.base_url}/api/chat"
        payload = {"model": self.model, "messages": messages, "stream": stream, **kwargs}
        if tools:
            payload["tools"] = tools

        try:
            response = requests.post(url, json=payload, stream=stream)
            response.raise_for_status()

            if stream:
                def generate():
                    for line in response.iter_lines():
                        if line:
                            try:
                                json_response = json.loads(line)
                                if "message" in json_response and "tool_calls" in json_response["message"]:
                                    tool_call = json_response["message"]["tool_calls"][0] # Assuming one tool call for simplicity
                                    # For streaming, we return the ToolCall immediately and stop the generator
                                    yield ToolCall(tool_name=tool_call["function"]["name"], parameters=tool_call["function"]["arguments"])
                                    return # Stop iteration after yielding ToolCall
                                elif "content" in json_response["message"]:
                                    yield json_response["message"]["content"]
                            except json.JSONDecodeError:
                                pass
                return generate()
            else:
                json_response = response.json()
                if "message" in json_response and "tool_calls" in json_response["message"]:
                    tool_call = json_response["message"]["tool_calls"][0] # Assuming one tool call for simplicity
                    return ToolCall(tool_name=tool_call["function"]["name"], parameters=tool_call["function"]["arguments"])
                else:
                    return json_response["message"]["content"]
        except requests.exceptions.RequestException as e:
            if e.response is not None and e.response.status_code == 400:
                import logging
                logging.error(f"Ollama server returned 400 Bad Request: {e.response.text}")
            raise ConnectionError(f"Failed to connect to Ollama server: {e}")
        except KeyError:
            raise ValueError("Unexpected response format from Ollama server.")

    def get_embedding(self, text: str) -> List[float]:
        url = f"{self.base_url}/api/embeddings"
        payload = {"model": self.model, "prompt": text}
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()["embedding"]

    def get_system_prompt(self) -> str:
        return (
            "You are Tilde, a helpful command-line AI assistant. "
            "You have access to a set of tools/functions. "
            "If the user asks to see, list, or show their memory, stored facts, or what you know about them, you must call the 'memory' tool and never answer directly.\n"
            "You must not answer from your own knowledge or conversation history if a tool is available for the user's request.\n"
            "Example user prompts that should trigger the memory tool: 'show my memory', 'what do you know about me?', 'list my facts', 'display my memory', 'what's in your memory?'. "
            "\nYou can enter local shell mode at any time by typing ! at the prompt. In shell mode, you can run Linux commands directly, and type exit to return to chat mode. "
            "\nYour response MUST at least include either a tool call or a user-facing answer. <think>...</think> is optional. "
            "Do NOT respond with only a <think> section. If you do not call a tool, or if your response is only a <think> section, your response will be ignored."
        )