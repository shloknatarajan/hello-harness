# Hello Harness

A simple AI agent harness inspired by Claude Code, built from scratch for learning purposes. This project demonstrates how to create a conversational AI agent that can interact with the local filesystem using tools.

## Features

- **Interactive REPL**: Chat with an AI agent in a command-line interface
- **File System Tools**: The agent can read files, edit files, search content, and list directories
- **Tool Execution**: Supports function calling with visual feedback
- **Conversation Memory**: Maintains context throughout the conversation
- **Modern Python**: Built with Python 3.12+ using modern dependencies

## Available Tools

The agent has access to the following tools:

- `read_file`: Read contents of files on the filesystem
- `edit_file`: Create new files or edit existing ones with exact string replacement
- `grep`: Search file contents using regex patterns
- `ls`: List files and directories with glob pattern support
- `bash`: Execute shell commands (if enabled)

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd hello-harness
   ```

2. **Set up Python environment** (requires Python 3.12+):
   ```bash
   # Using uv (recommended)
   uv sync
   
   # Or using pip
   pip install -e .
   ```

3. **Set up environment variables**:
   Create a `.env` file in the root directory:
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   ```

## Usage

**Run the interactive agent**:
```bash
python main.py
```

**Example interaction**:
```
hello-harness (type 'quit' to exit)

> Can you show me what files are in the src directory?
[tool: ls({'path': 'src'})]
I can see the src directory contains:
- agent_loop.py: The main agent execution loop
- cli.py: Command-line interface and REPL
- messages.py: Message and conversation handling
- prompt.py: System prompt definition
- tools/: Directory containing tool implementations

> Can you read the main.py file?
[tool: read_file({'file_path': 'main.py'})]
The main.py file is the entry point for the application...

> quit
```

## Project Structure

```
hello-harness/
├── main.py              # Entry point
├── src/
│   ├── cli.py          # CLI and REPL implementation
│   ├── agent_loop.py   # Core agent execution loop
│   ├── messages.py     # Conversation management
│   ├── prompt.py       # System prompt
│   └── tools/          # Tool implementations
│       ├── __init__.py
│       ├── read_file.py
│       ├── edit_file.py
│       ├── grep.py
│       ├── ls.py
│       └── bash.py
├── pyproject.toml      # Project configuration
└── README.md
```

## How It Works

The core of this project is the **agent loop** — the pattern that lets an LLM use tools iteratively to accomplish tasks. Here's how it works in detail:

### The Outer REPL Loop (`cli.py`)

The CLI runs a standard read-eval-print loop:

1. Print a prompt (`> `) and wait for user input
2. Append the user's message to the `Conversation` object
3. Call `run_agent_loop(conversation)` — this is where the interesting stuff happens
4. When the agent loop returns, go back to step 1

### The Inner Agent Loop (`agent_loop.py`)

This is the key piece. `run_agent_loop` runs a **while-True loop** that keeps calling the LLM until it produces a response with no tool calls:

```
while True:
    1. Send the full conversation history + system prompt + tool schemas to the LLM
    2. Get the response message
    3. Append the assistant message to the conversation
    4. If the message has text content, print it
    5. If there are NO tool calls → break (turn is done)
    6. For each tool call in the response:
       a. Parse the tool name and JSON arguments
       b. Execute the tool (read a file, run grep, etc.)
       c. Append the tool result to the conversation
    7. Loop back to step 1 — the LLM now sees the tool results and decides what to do next
```

The critical insight is that **the LLM decides when it's done**. It can chain multiple tool calls across multiple iterations — for example, listing a directory, then reading a file it found, then editing that file — all from a single user request. The loop only exits when the LLM returns a message without any tool calls, which typically means it's ready to respond to the user with a final answer.

### Conversation State (`messages.py`)

The `Conversation` class maintains the full message history as a list of dicts following the OpenAI message format (which LiteLLM uses as its common interface):

- **User messages**: `{"role": "user", "content": "..."}`
- **Assistant messages**: `{"role": "assistant", "content": "...", "tool_calls": [...]}` — may include both text and tool call requests
- **Tool results**: `{"role": "tool", "tool_call_id": "...", "content": "..."}` — each result is tied back to its tool call by ID

Every iteration of the agent loop sends the **entire conversation history** to the LLM. This means the model always has full context of what it has already done, what tool results it received, and what the user originally asked for.

### Tool Registry (`tools/__init__.py`)

Tools are registered in a simple dict mapping names to modules. Each tool module exports:
- `SCHEMA`: A JSON schema dict describing the tool's name, description, and parameters (sent to the LLM so it knows how to call it)
- `run(**kwargs)`: A function that executes the tool and returns a string result

This makes it easy to add new tools — just create a module with `SCHEMA` and `run`, then register it in the `TOOLS` dict.

### Diagram

```
User Input
    │
    ▼
┌─────────────────────────────────┐
│         Agent Loop              │
│                                 │
│  ┌───────────────────────────┐  │
│  │  Send conversation + tools│  │
│  │  to LLM                  │  │
│  └─────────┬─────────────────┘  │
│            │                    │
│            ▼                    │
│     ┌─────────────┐            │
│     │ Tool calls? │──No──► Print response, exit loop
│     └──────┬──────┘            │
│            │ Yes               │
│            ▼                    │
│  ┌───────────────────────────┐  │
│  │  Execute tools, append   │  │
│  │  results to conversation │  │
│  └───────────┬───────────────┘  │
│              │                  │
│              └──── loop back ───┘
│                                 │
└─────────────────────────────────┘
    │
    ▼
Wait for next user input
```

## Configuration

The agent uses Claude 4 Sonnet by default. You can modify the model in `src/agent_loop.py`:

```python
MODEL = "anthropic/claude-sonnet-4-20250514"
```

LiteLLM supports many providers, so you can easily switch to other models like:
- `openai/gpt-4`
- `anthropic/claude-3-sonnet-20240229`
- `gemini/gemini-pro`

