from .file_search import FileSearchTool
from .shell import ShellTool
from .read_file import ReadFileTool
from .create_file import CreateFileTool
from .web_fetch import WebFetchTool
from .list_directory import ListDirectoryTool
from .grep import GrepTool
from .edit_file import EditFileTool

from .memory_tool import ListMemoryTool, AddMemoryTool

from .time_tool import TimeTool
# Add sandbox control tool
from .think_toggle import ThinkToggleTool
from .sandbox_control import SandboxControlTool

# Add new tools here as needed

def get_all_tools():
    """Return a dictionary of all available tool instances, keyed by tool name."""
    tools = [
        FileSearchTool(),
        ShellTool(),
        ReadFileTool(),
        CreateFileTool(),
        WebFetchTool(),
        ListDirectoryTool(),
        GrepTool(),
        EditFileTool(),
        ListMemoryTool(),
        AddMemoryTool(),
        TimeTool(),
        ThinkToggleTool(),
        SandboxControlTool(),
    ]
    return {tool.name: tool for tool in tools}

def get_tool_schema():
    """Return a list of all tool schemas (name, description, parameters) for help/command palette."""
    return [tool.to_dict() for tool in get_all_tools().values()]

def list_tool_names():
    """Return a list of all available tool names."""
    return list(get_all_tools().keys())
