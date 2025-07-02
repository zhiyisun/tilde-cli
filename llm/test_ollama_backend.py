import pytest
import requests_mock
import requests
from llm.ollama_backend import OllamaBackend

@pytest.fixture
def ollama_backend():
    return OllamaBackend(base_url="http://localhost:11434", model="test_model")

def test_generate_text(ollama_backend):
    with requests_mock.Mocker() as m:
        m.post("http://localhost:11434/api/generate", json={"response": "Hello, world!"})
        response = ollama_backend.generate_text("Hello")
        assert response == "Hello, world!"

def test_generate_text_streaming(ollama_backend):
    with requests_mock.Mocker() as m:
        m.post("http://localhost:11434/api/generate", text='{"response": "Hello"}\n{"response": ", world!"}\n')
        responses = list(ollama_backend.generate_text("Hello", stream=True))
        assert responses == ["Hello", ", world!"]

def test_chat(ollama_backend):
    with requests_mock.Mocker() as m:
        m.post("http://localhost:11434/api/chat", json={"message": {"content": "Chat response."}})
        messages = [{"role": "user", "content": "Hi"}]
        response = ollama_backend.chat(messages)
        assert response == "Chat response."

def test_chat_streaming(ollama_backend):
    with requests_mock.Mocker() as m:
        m.post("http://localhost:11434/api/chat", text='{"message": {"content": "Chat"}}\n{"message": {"content": " response."}}\n')
        messages = [{"role": "user", "content": "Hi"}]
        responses = list(ollama_backend.chat(messages, stream=True))
        assert responses == ["Chat", " response."]

def test_get_embedding(ollama_backend):
    with requests_mock.Mocker() as m:
        m.post("http://localhost:11434/api/embeddings", json={"embedding": [0.1, 0.2, 0.3]})
        embedding = ollama_backend.get_embedding("test text")
        assert embedding == [0.1, 0.2, 0.3]

def test_connection_error(ollama_backend):
    with requests_mock.Mocker() as m:
        m.post("http://localhost:11434/api/generate", exc=requests.exceptions.ConnectionError)
        with pytest.raises(ConnectionError):
            ollama_backend.generate_text("Hello")

def test_key_error(ollama_backend):
    with requests_mock.Mocker() as m:
        m.post("http://localhost:11434/api/generate", json={"unexpected_key": "value"})
        with pytest.raises(ValueError):
            ollama_backend.generate_text("Hello")

