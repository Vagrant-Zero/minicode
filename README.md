# minicode

A minimal Claude Code alternative written in Python, powered by ReAct agent pattern.

## What is this?

`minicode` is a CLI coding assistant that imitates Claude Code's core functionality:
- Interactive chat in the terminal
- Autonomous tool calling via ReAct (Reason + Act) loop
- File operations, grep search, shell commands

## ReAct Pattern

The agent runs in a loop:
1. **Reason** - AI decides which tool to call
2. **Act** - Execute the tool (read, write, edit, glob, grep, bash)
3. **Observe** - Get the tool's output
4. Repeat until no more tools needed

```
❯ 帮我看看 main.py 开头10行

────────────────────────────────────────────────────────────────────────────────

⏺ Reading main.py...

  ─│ 1│ #!/usr/bin/env python3
  ─│ 2│ """minicode - minimal claude code alternative"""
  ─│ 3│
  ─│ 4│ import glob as globlib, json, os, re, subprocess
  ─│ 5│ ...
```

## Tools

| Tool | Description |
|------|-------------|
| `read` | Read file with line numbers |
| `write` | Write content to file |
| `edit` | Replace text in file |
| `glob` | Find files by pattern |
| `grep` | Search files with regex |
| `bash` | Run shell command |

## Configuration

### Environment Variables

```bash
# Anthropic API (default)
ANTHROPIC_API_KEY=sk-ant-...

# Or use OpenRouter / other LLM APIs
LLM_API_KEY=...
LLM_BASE_URL=https://openrouter.ai/api/v1
LLM_MODEL=anthropic/claude-opus-4.5

# Or use Qwen (DashScope)
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL=qwen-plus
```

Or create a `.env` file:

```bash
ANTHROPIC_API_KEY=sk-ant-...
```

## Usage

```bash
# Run
python minicode.py

# Commands
/q or exit    - Quit
/c            - Clear conversation
```

## Architecture

```
User Input → Messages → LLM API → Tool Calls → Execute → Observe → Loop
```

- `make_schema()` - Generates tool definitions for different API providers
- `call_api()` - Sends requests to Anthropic/OpenAI/Qwen
- `parse_response()` - Handles provider-specific response formats
- `run_tool()` - Executes local tools and returns results