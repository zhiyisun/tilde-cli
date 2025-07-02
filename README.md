# tilde-cli

**tilde-cli** is a command-line AI assistant that integrates local LLMs, tool execution, and memory for advanced automation and productivity. It supports dynamic tool invocation, file and directory operations, shell commands, and more, all with robust sandbox security controls.

## Features

- **Local LLM Integration**: Uses local models (e.g., Ollama) for chat and tool reasoning.
- **Tool System**: Extensible set of tools for file search, grep, file editing, shell commands, web fetch, and more.
- **Memory**: Persistent memory for context-aware conversations.
- **Dynamic Sandbox Security**: Restrict or allow file/directory access at runtime via a central control tool.
- **Rich Output**: Uses `rich` for beautiful CLI output.
- **Easy Extensibility**: Add new tools by implementing a simple interface.

## Installation

1. Clone the repository:
   ```sh
   git clone <repo-url>
   cd tilde-cli
   ```

2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

3. (Optional) Set up your local LLM backend (e.g., [Ollama](https://ollama.com/)).

## Usage

Run the CLI:
```sh
python main.py
```

You can interact with the assistant, ask questions, and invoke tools. Example:
```sh
python cli.py chat "List all Python files in the current directory."
```

## Tools

- `file_search`: Search for files matching a pattern.
- `grep`: Search for regex patterns in files.
- `read_file`: Read file contents.
- `createFile`: Create or write to a file.
- `edit_file`: Edit an existing file.
- `shell`: Run shell commands (sandboxed).
- `list_directory`: List files and directories.
- `web_fetch`: Fetch web content.
- `memory_tool`: List or add to memory.
- `time`: Get the current date/time.
- `sandbox_control`: Enable/disable sandbox security at runtime.

## Sandbox Security

By default, all file and shell operations are restricted to `~/.tilde-cli/sandbox`. You can enable or disable this restriction at runtime using the `sandbox_control` tool:

- **Check status**:
  ```
  python cli.py chat "Check sandbox status."
  ```
- **Disable sandbox**:
  ```
  python cli.py chat "Disable sandbox security."
  ```
- **Enable sandbox**:
  ```
  python cli.py chat "Enable sandbox security."
  ```

## Configuration

Edit `config.py` or use environment variables to set model, backend, and other options.

## Development

- Add new tools in the `tools/` directory and register them in `tools/__init__.py`.
- Run tests with:
  ```sh
  pytest
  ```

## Requirements

- Python 3.8+
- See `requirements.txt` for dependencies.