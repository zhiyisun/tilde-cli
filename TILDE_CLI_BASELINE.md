# Project Baseline: Tilde CLI (Python Assistant with Modular LLM Backend)

```
 _____ _ _     _         ____ _     ___ 
 |_   _(_) | __| | ___   / ___| |   |_ _|
   | | | | |/ _` |/ _ \ | |   | |    | | 
   | | | | | (_| |  __/ | |___| |___ | | 
   |_| |_|_|\__,_|\___|  \____|_____|___|

```

## Overview
Tilde CLI is a Python-based command-line assistant supporting multiple local or remote LLM (Large Language Model) backends. The project is modular, privacy-first, and designed for extensibility, with all user data stored locally by default. Current development uses Ollama as the default backend, but the architecture allows for future integration with other LLMs such as OpenAI, Llama.cpp, Gemma.cpp, etc.

---

## User Interface
Tilde CLI adopts the same user interface style as gemini-cli:
- **Interactive shell (REPL):** A conversational, session-based prompt where users can type natural language or commands, see LLM responses, and interact with tools.
- **Rich prompt:** The CLI prompt displays context, such as the current working directory, active tool, or session state, similar to gemini-cli.
- **Multi-turn chat:** The interface maintains conversation history, allowing for context-aware, multi-turn interactions.
- **Tool invocation:** When the LLM calls a tool, the UI clearly shows the tool being invoked, its parameters, and the result, with colorized or formatted output.
- **Memory/context display:** The UI can show relevant memory/context snippets as part of the conversation, just like gemini-cli.
- **Command palette/help:** Users can type `help` or use a palette to discover available commands and tools.
- **Scriptable mode:** Tilde CLI also supports non-interactive/scripted usage for automation, just like gemini-cli.

---

## Features

### 1. Command-Line Interface (CLI)
- Accepts user input as commands or natural language prompts.
- Supports both interactive and non-interactive (scriptable) modes.
- Provides help, usage, and command discovery.

### 2. LLM Backend Integration (Modular)
- Configurable support for different LLM backends (e.g., Ollama, local API, cloud API, etc).
- Ollama is integrated by default via HTTP API.
- Interfaces are reserved for future expansion to OpenAI, Llama.cpp, Gemma.cpp, etc.
- Supports text generation, multi-turn chat, and embeddings (if supported by the model).
- Allows model selection and parameter configuration (temperature, max tokens, etc).

### 3. Long-Term Memory
- Stores user facts, preferences, and important context in a local, human-readable file (Markdown or JSON).
- Commands to add, list, search, and remove memory entries.
- Deduplication logic to avoid storing duplicate facts.

### 4. Context Management
- Maintains session context for ongoing conversations.
- Loads relevant memory and context into the prompt for each LLM call.
- Manages context window to fit within model token limits (truncation, summarization, prioritization).
- Supports multi-step agentic workflows: The assistant can plan and execute a sequence of tool calls to achieve a user goal, not just single-step tool invocations. This enables more complex, automated problem solving and coding tasks.

### 5. Tool/Function Calling (Extensible)
- Allows the LLM to call predefined tools (file search, web fetch, shell commands, etc) via a function-calling interface.
- Tools are registered and described in a schema for the LLM to discover and use.
- Tool execution is sandboxed and auditable.
- Multi-step agentic workflows: The LLM can generate and execute a plan involving multiple tool calls, with intermediate reasoning and error recovery, similar to Gemini CLI's agent mode.

### 6. Configuration
- Users can select the LLM backend and related parameters via config file or CLI arguments.
- Other configuration options as before.

### 7. Privacy and Security
- All data is stored locally by default.
- No data is sent to remote servers unless explicitly configured.
- Sensitive operations (e.g., shell commands) require user confirmation.
- Multi-step workflows are auditable and each step is logged for transparency.

### 8. Scriptable and Non-Interactive Mode
- Tilde CLI supports both interactive (REPL) and non-interactive/scriptable usage.
- You can run commands, tools, or multi-step workflows directly from the command line or within scripts, enabling automation and CI/CD integration.
- All features, including agentic workflows, are available in both modes.

---

## Implementation Details

### 1. LLM Backend Abstraction
- Define a unified LLM backend interface (e.g., `LLMBackend` abstract class); all backend implementations must follow this interface.
- Each backend (e.g., Ollama, OpenAI, Llama.cpp) implements its own adapter module (e.g., `ollama_backend.py`, `openai_backend.py`).
- The main CLI dynamically loads and calls the specified backend based on configuration.
- This makes it easy to extend or switch backends in the future without major changes to the main workflow.

#### Ollama Backend (Current Default)
- Uses Python's `requests` or `httpx` to interact with Ollama's HTTP API.
- Implements `/api/generate`, `/api/chat`, `/api/embeddings`, etc.
- Supports streaming and non-streaming responses.

#### Other Backends (Planned/Optional)
- Interface is designed to support future backends such as OpenAI, Llama.cpp, Gemma.cpp, etc.
- Only need to implement the unified interface for seamless integration.

### 2. Memory Management
- Store memory in a local file (e.g., `~/.tilde-cli/memory.md` or `.json`).
- Functions to:
  - Add a fact (with deduplication).
  - List all facts.
  - Search for facts (substring or semantic search).
  - Remove or update facts.
- Use file locking to prevent concurrent write issues.

### 3. Context Handling
- Maintain a session object with conversation history.
- On each LLM call, construct the prompt with:
  - Current user input.
  - Relevant memory entries.
  - Recent conversation turns.
- Implement context window management to fit within model token limits.

### 4. Tool/Function Calling
- Define a schema for tools (name, description, parameters).
- Allow the LLM to request tool execution by emitting a structured response.
- Parse LLM output for tool calls, execute the tool, and feed the result back to the LLM.
- Example tools: file search, web fetch, shell command, calculator.

### 5. CLI Command Structure
- Use Python's `argparse` or a custom parser for command handling.
- Support subcommands (e.g., `memory add`, `memory list`, `chat`, `tool run`).
- Provide clear error messages and help output.

### 6. Configuration
- Config files (YAML/TOML/JSON) and environment variables support LLM backend selection and parameters.
- CLI arguments can temporarily override backend selection.

### 7. Logging and Debugging
- Implement logging with configurable verbosity.
- Provide a debug mode for detailed trace output.

---

## Example Directory Structure

```
tilde-cli/
  main.py
  llm/
    __init__.py
    backend.py         # LLMBackend abstract interface
    ollama_backend.py  # Ollama implementation
    openai_backend.py  # OpenAI implementation (optional/planned)
    llamacpp_backend.py# Llama.cpp implementation (optional/planned)
  memory.py
  context.py
  tools/
    __init__.py
    file_search.py
    web_fetch.py
    shell.py
  config.py
  cli.py
  utils.py
  README.md
  requirements.txt
```

---

## Extensibility
- Adding a new LLM backend only requires implementing the unified interface and registering it.
- Other extensibility options as before.

---

## Security Considerations
- All tool executions should be sandboxed and require explicit user permission.
- Sensitive data in memory should be encrypted or protected if needed.
- Provide clear warnings for potentially dangerous operations.

---

## Future Enhancements
- GUI or web interface.
- Plugin system for third-party tools.
- Remote LLM support (optional).
- Semantic memory search using embeddings.
- Visual workflow/plan editor for agentic multi-step tasks.
- More advanced error recovery and self-correction in agent mode.

---

## Development Environment

Tilde CLI is developed and tested primarily in a Conda environment for ease of dependency management and reproducibility.

- **Conda Environment:**
  - Recommended for local development and testing.
  - Easily manage Python versions and dependencies.
  - Example setup:
    ```sh
    conda create -n tilde-cli python=3.11
    conda activate tilde-cli
    pip install -r requirements.txt
    ```
  - You can add additional dependencies (e.g., for LLM backends) as needed.
- **Container Support:**
  - Optionally, a Dockerfile or dev container setup can be provided for full reproducibility and deployment.
  - For interactive CLI debugging, Conda is usually simpler, but containers are great for CI/CD and sharing.
- **IDE Integration:**
  - VS Code and other modern editors work well with Conda environments for debugging and development.

---

## Reference: Gemini-CLI Tool Descriptions

Below are the main tools supported by gemini-cli. You can use these as a reference for implementing similar tools in your Python/Ollama project.

### 1. Read File Tool
- **Purpose:** Read the contents of a file.
- **Parameters:**
  - `absolute_path` (string): Path to the file.
  - `offset` (int, optional): Line number to start reading from.
  - `limit` (int, optional): Number of lines to read.
- **Behavior:** Returns the file content (optionally a slice), with error handling for missing or out-of-bounds files.

### 2. Write File Tool
- **Purpose:** Write or overwrite content in a file.
- **Parameters:**
  - `absolute_path` (string): Path to the file.
  - `content` (string): Content to write.
- **Behavior:** Writes content to the file, creating it if necessary. May include diff/approval logic for safety.

### 3. List Directory Tool (LS)
- **Purpose:** List files and directories in a given path.
- **Parameters:**
  - `path` (string): Directory to list.
  - `ignore` (list of string, optional): Glob patterns to ignore.
  - `respect_git_ignore` (bool, optional): Whether to respect `.gitignore`.
- **Behavior:** Returns a list of files/directories, optionally filtered.

### 4. Grep Tool
- **Purpose:** Search for a regex pattern in files.
- **Parameters:**
  - `pattern` (string): Regex to search for.
  - `path` (string, optional): Directory to search in.
  - `include` (string, optional): File pattern to include.
- **Behavior:** Returns matching lines and file locations.

### 5. Web Fetch Tool
- **Purpose:** Fetch and return the main content from a web page.
- **Parameters:**
  - `url` (string): The URL to fetch.
- **Behavior:** Downloads and extracts readable content from the page, with timeout and size limits.

### 6. Shell Tool
- **Purpose:** Execute a shell command.
- **Parameters:**
  - `command` (string): The shell command to run.
  - `description` (string, optional): Description for logging.
  - `directory` (string, optional): Directory to run the command in.
- **Behavior:** Runs the command as a subprocess, returns output, and may require user confirmation for safety.

### 7. Edit Tool
- **Purpose:** Edit a file by replacing text.
- **Parameters:**
  - `file_path` (string): File to edit.
  - `old_string` (string): Text to replace.
  - `new_string` (string): Replacement text.
- **Behavior:** Finds and replaces text in the file, with optional diff/approval.

### 8. Memory Tool
- **Purpose:** Save a fact or piece of information to long-term memory.
- **Parameters:**
  - `fact` (string): The fact to remember.
- **Behavior:** Appends the fact to a local memory file, with deduplication and sectioning.

### 9. Read Many Files Tool
- **Purpose:** Read multiple files (e.g., for context ingestion).
- **Parameters:** Typically accepts file patterns or lists.
- **Behavior:** Returns the content of multiple files, possibly with size limits.

### 10. Glob Tool
- **Purpose:** Find files matching a glob pattern.
- **Parameters:**
  - `pattern` (string): Glob pattern.
- **Behavior:** Returns matching file paths.

### 11. Web Search Tool
- **Purpose:** Search the web and return summarized results.
- **Parameters:**
  - `query` (string): Search query.
- **Behavior:** Uses a web search API and returns top results.

### 12. MCP Tools (Advanced/Optional)
- **Purpose:** Interact with Model Context Protocol servers for advanced context or tool integration.
- **Parameters:** Varies.
- **Behavior:** Used for advanced workflows and integrations.

---

**This document is the baseline for your Python-based, Ollama-powered CLI assistant (Tilde CLI). Expand or refine each section as your implementation progresses.**
