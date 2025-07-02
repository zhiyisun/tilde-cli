from llm.qwen_adapter import QwenModelAdapter
from llm.gemma_adapter import GemmaModelAdapter

# Only keep get_model_adapter here
def get_model_adapter(model_name):
    model_name_lower = model_name.lower()
    if model_name_lower.startswith("gemma"):
        return GemmaModelAdapter(model_name)
    # Default: treat as Qwen for now, can add more logic here
    return QwenModelAdapter(model_name)
