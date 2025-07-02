import json
import os
import re
import stat
from typing import List, Dict

class MemoryManager:
    def __init__(self, memory_file: str = os.path.expanduser("~/.tilde-cli/memory.json")):
        self.memory_file = os.path.expanduser(memory_file)
        self.memory = self._load_memory()

    def _load_memory(self) -> List[Dict[str, str]]:
        if not os.path.exists(self.memory_file):
            os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
            with open(self.memory_file, 'w') as f:
                json.dump([], f)
            return []
        with open(self.memory_file, 'r') as f:
            return json.load(f)

    def _save_memory(self):
        with open(self.memory_file, 'w') as f:
            json.dump(self.memory, f, indent=4)
        # Security: set file permissions to user-only (0600)
        try:
            os.chmod(self.memory_file, stat.S_IRUSR | stat.S_IWUSR)
        except Exception:
            pass

    def add_fact(self, fact: str) -> bool:
        # Improved deduplication: case-insensitive, trims whitespace
        fact_clean = fact.strip().lower()
        for entry in self.memory:
            if entry.get("fact", "").strip().lower() == fact_clean:
                return False  # Fact already exists
        self.memory.append({"fact": fact.strip()})
        self._save_memory()
        return True

    def update_fact(self, old_fact: str, new_fact: str) -> bool:
        old_clean = old_fact.strip().lower()
        for entry in self.memory:
            if entry.get("fact", "").strip().lower() == old_clean:
                entry["fact"] = new_fact.strip()
                self._save_memory()
                return True
        return False

    def list_facts(self) -> List[Dict[str, str]]:
        return self.memory

    def search_facts(self, query: str) -> List[Dict[str, str]]:
        results = []
        query_words = set(word.lower() for word in re.findall(r'\b\w+\b', query))
        for entry in self.memory:
            fact_content = entry.get("fact", "").lower()
            if any(word in fact_content for word in query_words):
                results.append(entry)
        return results

    def semantic_search_facts(self, query: str) -> List[Dict[str, str]]:
        # Placeholder for future embedding-based search
        # For now, just call search_facts
        return self.search_facts(query)

    def remove_fact(self, fact: str) -> bool:
        initial_len = len(self.memory)
        self.memory = [entry for entry in self.memory if entry.get("fact") != fact]
        if len(self.memory) < initial_len:
            self._save_memory()
            return True
        return False