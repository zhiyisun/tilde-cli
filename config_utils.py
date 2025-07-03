
import os
import json
from typing import Any, Dict

PROJECT_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")
USER_CONFIG_DIR = os.path.expanduser("~/.tilde-cli")
USER_CONFIG_PATH = os.path.join(USER_CONFIG_DIR, "config.json")


class Config:
    OLLAMA_BASE_URL = "http://localhost:11434"
    OLLAMA_MODEL = "qwen3:30b"
    MEMORY_FILE = "~/.tilde-cli/memory.json"
    LOG_LEVEL = "INFO"
    HIDE_THINK = True  # By default, hide <think> sections

    @classmethod
    def ensure_user_config(cls):
        """Ensure ~/.tilde-cli/config.json exists, copying from project if needed."""
        if not os.path.exists(USER_CONFIG_PATH):
            os.makedirs(USER_CONFIG_DIR, exist_ok=True)
            if os.path.exists(PROJECT_CONFIG_PATH):
                with open(PROJECT_CONFIG_PATH, "r") as src, open(USER_CONFIG_PATH, "w") as dst:
                    dst.write(src.read())
        return USER_CONFIG_PATH

    @classmethod
    def load_config(cls, config_path: str = None):
        """Load config from ~/.tilde-cli/config.json, copying from project if needed."""
        config_file = config_path or cls.ensure_user_config()
        config = {}
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
        # 2. Override with environment variables
        config['OLLAMA_BASE_URL'] = os.environ.get('OLLAMA_BASE_URL', config.get('OLLAMA_BASE_URL', cls.OLLAMA_BASE_URL))
        config['OLLAMA_MODEL'] = os.environ.get('OLLAMA_MODEL', config.get('OLLAMA_MODEL', cls.OLLAMA_MODEL))
        config['MEMORY_FILE'] = os.environ.get('MEMORY_FILE', config.get('MEMORY_FILE', cls.MEMORY_FILE))
        config['LOG_LEVEL'] = os.environ.get('LOG_LEVEL', config.get('LOG_LEVEL', cls.LOG_LEVEL))
        config['HIDE_THINK'] = json.loads(str(os.environ.get('HIDE_THINK', config.get('HIDE_THINK', cls.HIDE_THINK))).lower() if str(os.environ.get('HIDE_THINK', config.get('HIDE_THINK', cls.HIDE_THINK))).lower() in ['true','false'] else 'true')
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


    @classmethod
    def save_config(cls, config_path: str = None):
        config_file = config_path or USER_CONFIG_PATH
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        with open(config_file, 'w') as f:
            json.dump(cls.as_dict(), f, indent=2)

    @classmethod
    def set_config(cls, key: str, value: Any, config_path: str = None):
        setattr(cls, key, value)
        cls.save_config(config_path)
