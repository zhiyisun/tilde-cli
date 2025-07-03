from llm.qwen_adapter import QwenModelAdapter
 

# Only keep get_model_adapter here
def get_model_adapter(model_name):
    model_name_lower = model_name.lower()
    # Default: treat as Qwen for now, can add more logic here
    return QwenModelAdapter(model_name)
