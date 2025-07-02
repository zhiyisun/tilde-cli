import argparse
import os
import json
from llm.ollama_backend import OllamaBackend
from llm.model_adapter import get_model_adapter
from memory import MemoryManager
from context import ContextManager, Session
from config_utils import Config
from tools import get_all_tools
from utils import setup_logging
from rich.console import Console
from rich.markdown import Markdown

class TildeCLI:
    def __init__(self):
        self.console = Console()
        # Load config from file or env
        Config.load_config()
        setup_logging(Config.LOG_LEVEL)
        self.llm_backend = OllamaBackend(base_url=Config.OLLAMA_BASE_URL, model=Config.OLLAMA_MODEL)
        self.model_adapter = get_model_adapter(Config.OLLAMA_MODEL)
        self.memory_manager = MemoryManager(memory_file=Config.MEMORY_FILE)
        self.context_manager = ContextManager()
        self.session = Session()  # Persistent session for chat history
        self.tools = get_all_tools()
        # Qwen3:30b tool format
        self.tool_definitions = self.model_adapter.build_tool_definitions(self.tools)
        # Local tool backend only (no remote execution)

        self.backend = self

        # Add system prompt with tool usage examples and strong tool-use instructions
        base_prompt = self.llm_backend.get_system_prompt() if hasattr(self.llm_backend, 'get_system_prompt') else None
        tool_instruction = (
            "\nIMPORTANT: For any user question about the current date, time, or timezone, you MUST call the 'time' tool. "
            "Do NOT answer from your own knowledge. Always use the 'time' tool for all such queries, even if the user does not specify a format or timezone. "
            "If the user asks for the time, date, or timezone, call the tool and present the result.\n"
        )
        if base_prompt:
            self.system_prompt = base_prompt + tool_instruction
        else:
            self.system_prompt = tool_instruction

        self.parser = self._setup_parser()

    def execute_tool(self, tool, params):
        return tool.execute(**params)

        # Add system prompt with tool usage examples and strong tool-use instructions
        base_prompt = self.llm_backend.get_system_prompt() if hasattr(self.llm_backend, 'get_system_prompt') else None
        tool_instruction = (
            "\nIMPORTANT: For any user question about the current date, time, or timezone, you MUST call the 'time' tool. "
            "Do NOT answer from your own knowledge. Always use the 'time' tool for all such queries, even if the user does not specify a format or timezone. "
            "If the user asks for the time, date, or timezone, call the tool and present the result.\n"
        )
        if base_prompt:
            self.system_prompt = base_prompt + tool_instruction
        else:
            self.system_prompt = tool_instruction

    def _setup_parser(self):
        parser = argparse.ArgumentParser(description="Tilde CLI - A Python-based command-line assistant.")
        parser.add_argument('--remote', type=str, help='Remote SSH server in user@host[:key_path] format')
        subparsers = parser.add_subparsers(dest="command", help="Available commands")

        # Chat command
        chat_parser = subparsers.add_parser("chat", help="Start an interactive chat session with the LLM.")
        chat_parser.add_argument("prompt", nargs='?', help="Initial prompt for the chat session.")

        # Memory commands
        memory_parser = subparsers.add_parser("memory", help="Manage long-term memory.")
        memory_subparsers = memory_parser.add_subparsers(dest="memory_command", help="Memory commands")

        memory_add_parser = memory_subparsers.add_parser("add", help="Add a fact to memory.")
        memory_add_parser.add_argument("fact", type=str, help="The fact to add.")

        memory_list_parser = memory_subparsers.add_parser("list", help="List all facts in memory.")

        memory_search_parser = memory_subparsers.add_parser("search", help="Search for facts in memory.")
        memory_search_parser.add_argument("query", type=str, help="The query to search for.")

        memory_remove_parser = memory_subparsers.add_parser("remove", help="Remove a fact from memory.")
        memory_remove_parser.add_argument("fact", type=str, help="The fact to remove.")

        # Tool commands
        tool_parser = subparsers.add_parser("tool", help="Run a tool directly.")
        tool_subparsers = tool_parser.add_subparsers(dest="tool_command", help="Tool commands")

        tool_run_parser = tool_subparsers.add_parser("run", help="Run a specific tool by name.")
        tool_run_parser.add_argument("name", type=str, help="The name of the tool to run.")
        tool_run_parser.add_argument("--params", type=str, default="{}", help="Tool parameters as a JSON string.")

        tool_list_parser = tool_subparsers.add_parser("list", help="List all available tools.")

        # Add a top-level help command
        help_parser = subparsers.add_parser("help", help="Show help for commands or tools.")
        help_parser.add_argument("topic", nargs="?", default=None, help="Command or tool name to get help for.")

        # Session management commands
        session_parser = subparsers.add_parser("session", help="Session management")
        session_subparsers = session_parser.add_subparsers(dest="session_cmd")
        session_subparsers.add_parser("save", help="Save current session")
        session_subparsers.add_parser("load", help="Load a session")
        session_subparsers.add_parser("reset", help="Reset current session")

        return parser

    def run(self):
        args = self.parser.parse_args()

        if args.command == "chat":
            self._handle_chat(args.prompt)
        elif args.command == "memory":
            self._handle_memory_command(args)
        elif args.command == "tool":
            self._handle_tool_command(args)
        elif args.command == "help":
            self._handle_help_command(args)
        elif args.command == "session":
            self._handle_session_command(args)
            return
        else:
            self.parser.print_help()

    def _handle_chat(self, initial_prompt: str = None):
        print("Starting chat session. Type 'exit' to quit.")
        prompt_str = "\033[1;32m\033[1m~\033[0m "
        # Enable command history and arrow key navigation if readline is available
        try:
            import readline
            histdir = os.path.expanduser("~/.tilde-cli")
            os.makedirs(histdir, exist_ok=True)
            histfile = os.path.join(histdir, "history")
            try:
                readline.read_history_file(histfile)
            except FileNotFoundError:
                pass
            import atexit
            atexit.register(readline.write_history_file, histfile)
            def pre_input_hook():
                import sys
                # Always clear the line and redraw the prompt before every input
                sys.stdout.write('\r' + ' ' * 120 + '\r')
                sys.stdout.write(prompt_str)
                sys.stdout.flush()
            readline.set_pre_input_hook(pre_input_hook)
        except ImportError:
            readline = None
        if initial_prompt:
            self._process_and_get_llm_response(initial_prompt)

        while True:
            try:
                # Do not print the prompt here; pre_input_hook handles it for every input
                user_input = input()
                if user_input.lower() == 'exit':
                    break
                self._process_and_get_llm_response(user_input)
            except EOFError:
                print("\nExiting Tilde CLI.")
                break

    def _process_and_get_llm_response(self, user_input: str):
        # Search for relevant facts based on the user's input
        relevant_facts = self.memory_manager.search_facts(user_input)
        relevant_fact_strings = [fact["fact"] for fact in relevant_facts]

        # Prepend relevant facts to the user's input for the current turn
        if relevant_fact_strings:
            memory_prefix = "Here is some relevant information from your memory: " + "; ".join(relevant_fact_strings) + "\n\n"
            user_input = memory_prefix + user_input
        # Add the modified user input to the conversation history
        self.context_manager.add_message("user", user_input)
        self.session.add_turn("user", user_input)
        self._get_llm_response(call_depth=0)

    def _get_llm_response(self, call_depth=0, max_depth=5):
        if call_depth > max_depth:
            print(f"[Warning] Maximum tool execution recursion depth ({max_depth}) reached. Aborting further tool calls.")
            return
        max_tokens = 2048
        messages = self._get_context_window(self.session.history, max_tokens)
        # Insert system prompt as first message if available
        if self.system_prompt:
            messages = ([{"role": "system", "content": self.system_prompt}] + messages)
        import threading
        import time
        stop_spinner = threading.Event()
        spinner_thread = threading.Thread(target=self._spinner, args=(stop_spinner,))
        spinner_thread.start()
        timeout_seconds = 60
        response_exception = [None]
        result_holder = {}
        def llm_worker():
            try:
                response_generator = self.llm_backend.chat(messages, tools=self.tool_definitions, stream=True)
                full_response_content = ""
                tool_call = None
                hide_think = getattr(Config, 'HIDE_THINK', True)
                in_think_block = False
                for tool_call_candidate, text_chunk in self.model_adapter.parse_response_stream(response_generator):
                    if tool_call_candidate:
                        tool_call = tool_call_candidate
                        break
                    if text_chunk is not None:
                        text = str(text_chunk)
                        if hide_think:
                            # Remove entire <think>...</think> blocks, even if split across chunks
                            if not in_think_block:
                                if text.strip().lower().startswith("<think"):
                                    in_think_block = True
                                    # If </think> is in the same chunk, end block
                                    if "</think>" in text.lower():
                                        in_think_block = False
                                        after = text.lower().split("</think>", 1)[1]
                                        if after.strip():
                                            full_response_content += after
                                    continue
                            else:
                                # Already in <think> block, look for end
                                if "</think>" in text.lower():
                                    in_think_block = False
                                    after = text.lower().split("</think>", 1)[1]
                                    if after.strip():
                                        full_response_content += after
                                continue
                        if not in_think_block:
                            full_response_content += text
                result_holder['tool_call'] = tool_call
                result_holder['full_response_content'] = full_response_content
            except Exception as e:
                response_exception[0] = e

        llm_thread = threading.Thread(target=llm_worker)
        llm_thread.start()
        llm_thread.join(timeout_seconds)
        stop_spinner.set()
        spinner_thread.join()
        if llm_thread.is_alive():
            self.console.print("\n[red]Error: LLM backend timed out after 60 seconds.[/red]")
            return
        if response_exception[0] is not None:
            self.console.print(f"Error communicating with LLM: {response_exception[0]}")
            return
        tool_call = result_holder.get('tool_call')
        full_response_content = result_holder.get('full_response_content', "")
        if tool_call:
            tool_name = tool_call.get("tool_name") or tool_call.get("name")
            parameters = tool_call.get("parameters", {})
            if tool_name not in self.tools:
                self.console.print(f"[Warning] LLM requested unknown tool: '{tool_name}'. Registered tools: {list(self.tools.keys())}")
                self.context_manager.add_message("assistant", f"[Warning] LLM requested unknown tool: '{tool_name}'.")
                self.session.add_turn("assistant", f"[Warning] LLM requested unknown tool: '{tool_name}'.")
                return
            # Prevent repeated think_toggle calls for the same value in a single turn
            if tool_name == "think_toggle":
                # Use session or context to store last toggle value for this turn
                last_toggle = getattr(self, '_last_think_toggle', None)
                requested = parameters.get('enabled')
                if last_toggle is not None and requested == last_toggle:
                    self.console.print("[dim][think_toggle already set to this value in this turn][/dim]", highlight=False)
                    return
                self._last_think_toggle = requested
            # Expand ~ to home directory for any 'path' or 'file' parameter
            expanded_parameters = parameters.copy()
            for key in ["path", "file", "dir"]:
                if key in expanded_parameters and isinstance(expanded_parameters[key], str):
                    expanded_parameters[key] = os.path.expanduser(expanded_parameters[key])
            self.console.print(f"\nTilde: Executing tool '{tool_name}' with parameters {expanded_parameters}...")
            if tool_name == "ls" and "dir" in expanded_parameters and "path" not in expanded_parameters:
                expanded_parameters["path"] = expanded_parameters.pop("dir")
            # For LLM-initiated shell tool calls, skip confirmation
            if tool_name == "shell" and "require_confirmation" not in expanded_parameters:
                expanded_parameters["require_confirmation"] = False
            tool_output = self.backend.execute_tool(self.tools[tool_name], expanded_parameters)
            self.console.print(f"Tilde (tool output): {tool_output}")
            # For think_toggle, add a state message to the conversation so LLM sees the effect
            if tool_name == "think_toggle":
                state_msg = f"<think> sections are now {'shown' if not getattr(Config, 'HIDE_THINK', True) else 'hidden'}."
                self.context_manager.add_message("tool", str(tool_output) + "\n" + state_msg)
                self.session.add_turn("tool", str(tool_output) + "\n" + state_msg, tool=tool_name)
            else:
                self.context_manager.add_message("tool", str(tool_output))
                self.session.add_turn("tool", str(tool_output), tool=tool_name)
            self._get_llm_response(call_depth=call_depth+1, max_depth=max_depth)
        else:
            # Render the full response as markdown at once for proper formatting
            self.console.print()
            self._render_markdown(full_response_content)
            # Show a subtle status if <think> sections are currently hidden
            if getattr(Config, 'HIDE_THINK', True):
                self.console.print("[dim][Hint: <think> sections hidden][/dim]", highlight=False)
            self.context_manager.add_message("assistant", full_response_content)
            self.session.add_turn("assistant", full_response_content)

    def _spinner(self, stop_event):
        import itertools
        import time
        import sys
        # Alternate between two emoji faces for animation
        emoji1 = "🤔"
        emoji2 = "⏳"
        spinner_icons = [emoji1, emoji2]
        for icon in itertools.cycle(spinner_icons):
            if stop_event.is_set():
                break
            sys.stdout.write(f"\r\033[33mTilde is thinking {icon}\033[0m")
            sys.stdout.flush()
            time.sleep(0.8)  # Spinner: set to 0.8 seconds
        sys.stdout.write("\r" + " " * 40 + "\r")
        sys.stdout.flush()

    def _render_markdown(self, text):
        # Try to render as markdown, fallback to plain text if not valid
        try:
            self.console.print(Markdown(text))
        except Exception:
            self.console.print(text)

    def _get_context_window(self, history, max_tokens):
        # Use tiktoken to count tokens (or fallback to word count if not available)
        try:
            import tiktoken
            enc = tiktoken.encoding_for_model("gpt-3.5-turbo")
            def count_tokens(msgs):
                return sum(len(enc.encode(m.get("content", ""))) for m in msgs)
        except ImportError:
            def count_tokens(msgs):
                return sum(len(m.get("content", "").split()) for m in msgs)
        except Exception:
            def count_tokens(msgs):
                return sum(len(m.get("content", "").split()) for m in msgs)
        # Start from the most recent, add until token limit
        window = []
        total = 0
        for msg in reversed(history):
            tokens = count_tokens([msg])
            if total + tokens > max_tokens:
                break
            window.insert(0, msg)
            total += tokens
        # If still too long, summarize older turns
        if total > max_tokens and len(window) > 2:
            summary = self._summarize_turns(window[:-2])
            window = [summary] + window[-2:]
        return window

    def _summarize_turns(self, turns):
        # Improved summarization: if too long, call LLM to summarize, else concatenate
        text = "\n".join([f"{t['role']}: {t['content']}" for t in turns])
        if len(text) > 500:
            # Use the LLM itself to summarize the earlier conversation
            try:
                summary_prompt = (
                    "Summarize the following conversation in 2-3 sentences, preserving important facts, context, and user intent.\n" + text[:2000]
                )
                summary = self.llm_backend.generate_text(summary_prompt, max_tokens=128, temperature=0.2)
                if len(summary) > 400:
                    summary = summary[:400] + "..."
                return {"role": "system", "content": f"Summary of earlier conversation: {summary}"}
            except Exception as e:
                # Fallback to truncation if LLM call fails
                text = text[:500] + "..."
        return {"role": "system", "content": f"Summary of earlier conversation: {text}"}

    def _handle_memory_command(self, args):
        if args.memory_command == "add":
            if self.memory_manager.add_fact(args.fact):
                print(f"Fact added: {args.fact}")
            else:
                print(f"Fact already exists: {args.fact}")
        elif args.memory_command == "list":
            facts = self.memory_manager.list_facts()
            if facts:
                print("Memory facts:")
                for i, fact in enumerate(facts):
                    print(f"{i+1}. {fact}")
            else:
                print("No facts in memory.")
        elif args.memory_command == "search":
            results = self.memory_manager.search_facts(args.query)
            if results:
                print(f"Found {len(results)} matching facts:")
                for i, fact in enumerate(results):
                    print(f"{i+1}. {fact}")
            else:
                print(f"No facts found matching '{args.query}'.")
        elif args.memory_command == "remove":
            if self.memory_manager.remove_fact(args.fact):
                print(f"Fact removed: {args.fact}")
            else:
                print(f"Fact not found: {args.fact}")

    def _handle_tool_command(self, args):
        if args.tool_command == "run":
            tool_name = args.name
            params = args.params
            import json
            try:
                params_dict = json.loads(params)
            except Exception as e:
                print(f"Invalid JSON for parameters: {e}")
                return
            if tool_name not in self.tools:
                print(f"Tool '{tool_name}' not found. Use 'tool list' to see available tools.")
                return
            tool = self.tools[tool_name]
            print(f"Running tool '{tool_name}' with parameters: {params_dict}")
            # For shell tool, require confirmation
            if tool_name == "shell":
                confirm = input("This will execute a shell command. Are you sure? (yes/no): ")
                if confirm.lower() != "yes":
                    print("Aborted.")
                    return
            result = tool.execute(**params_dict)
            print(f"Result: {result}")
        elif args.tool_command == "list":
            from tools import get_tool_schema
            print("Available tools:")
            for tool in get_tool_schema():
                print(f"- {tool['name']}: {tool['description']}")

    def _handle_help_command(self, args):
        topic = args.topic
        if not topic:
            print("Tilde CLI Help:\n")
            print("Available commands:")
            print("  chat [prompt]         Start an interactive chat session with the LLM.")
            print("  memory <subcommand>   Manage long-term memory (add, list, search, remove).")
            print("  tool <subcommand>     Run or list available tools.")
            print("  help [topic]          Show help for a command or tool.")
            print("\nUse 'help <command>' or 'help <tool>' for more details.")
        else:
            # Check if topic is a tool
            from tools import get_all_tools, get_tool_schema
            tools = get_all_tools()
            if topic in tools:
                tool = tools[topic]
                schema = tool.to_dict()
                print(f"Tool: {schema['name']}")
                print(f"Description: {schema['description']}")
                print("Parameters:")
                for param, desc in schema['parameters']['properties'].items():
                    print(f"  {param}: {desc['description']}")
                return
            # Otherwise, print command help
            if topic == "chat":
                print("chat [prompt]\n  Start an interactive chat session with the LLM. Optionally provide an initial prompt.")
            elif topic == "memory":
                print("memory <add|list|search|remove> ...\n  Manage long-term memory. Subcommands:\n    add <fact>      Add a fact to memory.\n    list            List all facts.\n    search <query>  Search for facts.\n    remove <fact>   Remove a fact.")
            elif topic == "tool":
                print("tool <run|list> ...\n  Run or list available tools.\n    run <name> --params '{...}'  Run a tool by name with parameters as JSON.\n    list                      List all available tools.")
            else:
                print(f"No help found for '{topic}'.")

    def _handle_session_command(self, args):
        if args.session_cmd == "save":
            self.session.save()
            print("Session saved.")
        elif args.session_cmd == "load":
            self.session.load()
            print("Session loaded.")
        elif args.session_cmd == "reset":
            self.session.reset()
            print("Session reset.")

if __name__ == "__main__":
    TildeCLI().run()
