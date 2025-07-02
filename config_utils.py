import os
import json
from typing import Any, Dict

class Config:
    OLLAMA_BASE_URL = "http://localhost:11434"
    OLLAMA_MODEL = "qwen3:30b"
    MEMORY_FILE = "~/.tilde-cli/memory.json"
    LOG_LEVEL = "INFO"
    HIDE_THINK = True  # By default, hide <think> sections

    @classmethod
    def load_config(cls, config_path: str = None):
        """Load config from a JSON file, environment variables, or defaults."""
        config = {}
        # 1. Load from file if provided
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
        # 2. Override with environment variables
        config['OLLAMA_BASE_URL'] = os.environ.get('OLLAMA_BASE_URL', config.get('OLLAMA_BASE_URL', cls.OLLAMA_BASE_URL))
        config['OLLAMA_MODEL'] = os.environ.get('OLLAMA_MODEL', config.get('OLLAMA_MODEL', cls.OLLAMA_MODEL))
        config['MEMORY_FILE'] = os.environ.get('MEMORY_FILE', config.get('MEMORY_FILE', cls.MEMORY_FILE))
        config['LOG_LEVEL'] = os.environ.get('LOG_LEVEL', config.get('LOG_LEVEL', cls.LOG_LEVEL))
        config['HIDE_THINK'] = os.environ.get('HIDE_THINK', config.get('HIDE_THINK', cls.HIDE_THINK))
        # 3. Set as class attributes
        for k, v in config.items():
            setattr(cls, k, v)

    @classmethod
    def as_dict(cls) -> Dict[str, Any]:
        return {
            'OLLAMA_BASE_URL': cls.OLLAMA_BASE_URL,
            'OLLAMA_MODEL': cls.OLLAMA_MODEL,
            'MEMORY_FILE': cls.MEMORY_FILE,
            'LOG_LEVEL': cls.LOG_LEVEL,
            'HIDE_THINK': cls.HIDE_THINK,
        }
