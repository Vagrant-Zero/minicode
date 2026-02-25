#!/usr/bin/env python3
"""minicode - minimal claude code alternative"""

# TODO: 使用官方 SDK (openai-python, anthropic-python) 替换 urllib
# 当前使用 urllib 导致:
# - 消息格式需要手动转换，容易出错
# - tool_calls 响应格式不正确

import glob as globlib, json, os, re, subprocess, urllib.request, urllib.error
from dotenv import load_dotenv

OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY")
API_URL = "https://openrouter.ai/api/v1/messages" if OPENROUTER_KEY else "https://api.anthropic.com/v1/messages"
MODEL = os.environ.get("MODEL", "anthropic/claude-opus-4.5" if OPENROUTER_KEY else "claude-opus-4-5")
API_PROVIDER = "anthropic"  # 默认使用 Anthropic 格式

# ANSI colors
RESET, BOLD, DIM = "\033[0m", "\033[1m", "\033[2m"
BLUE, CYAN, GREEN, YELLOW, RED = (
    "\033[34m",
    "\033[36m",
    "\033[32m",
    "\033[33m",
    "\033[31m",
)


# --- init config  ---
def initConfig():
    LLM_API_KEY = os.environ.get("LLM_API_KEY")
    if not LLM_API_KEY:
        return
    # 更新全局变量
    global MODEL
    global API_URL
    global OPENROUTER_KEY
    global API_PROVIDER
    MODEL = os.environ.get("LLM_MODEL")
    API_URL = os.environ.get("LLM_BASE_URL")
    OPENROUTER_KEY = LLM_API_KEY

    # 根据 API_URL 判断 provider 类型
    url_lower = API_URL.lower()
    if "openrouter" in url_lower:
        API_PROVIDER = "openrouter"
    elif "dashscope" in url_lower or "aliyuncs" in url_lower:
        API_PROVIDER = "qwen"
    else:
        API_PROVIDER = "anthropic"

# --- Tool implementations ---


def read(args):
    lines = open(args["path"]).readlines()
    offset = args.get("offset", 0)
    limit = args.get("limit", len(lines))
    selected = lines[offset : offset + limit]
    return "".join(f"{offset + idx + 1:4}| {line}" for idx, line in enumerate(selected))


def write(args):
    with open(args["path"], "w") as f:
        f.write(args["content"])
    return "ok"


def edit(args):
    text = open(args["path"]).read()
    old, new = args["old"], args["new"]
    if old not in text:
        return "error: old_string not found"
    count = text.count(old)
    if not args.get("all") and count > 1:
        return f"error: old_string appears {count} times, must be unique (use all=true)"
    replacement = (
        text.replace(old, new) if args.get("all") else text.replace(old, new, 1)
    )
    with open(args["path"], "w") as f:
        f.write(replacement)
    return "ok"


def glob(args):
    pattern = (args.get("path", ".") + "/" + args["pat"]).replace("//", "/")
    files = globlib.glob(pattern, recursive=True)
    files = sorted(
        files,
        key=lambda f: os.path.getmtime(f) if os.path.isfile(f) else 0,
        reverse=True,
    )
    return "\n".join(files) or "none"


def grep(args):
    pattern = re.compile(args["pat"])
    hits = []
    for filepath in globlib.glob(args.get("path", ".") + "/**", recursive=True):
        try:
            for line_num, line in enumerate(open(filepath), 1):
                if pattern.search(line):
                    hits.append(f"{filepath}:{line_num}:{line.rstrip()}")
        except Exception:
            pass
    return "\n".join(hits[:50]) or "none"


def bash(args):
    proc = subprocess.Popen(
        args["cmd"], shell=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True
    )
    output_lines = []
    try:
        while True:
            line = proc.stdout.readline()
            if not line and proc.poll() is not None:
                break
            if line:
                print(f"  {DIM}│ {line.rstrip()}{RESET}", flush=True)
                output_lines.append(line)
        proc.wait(timeout=30)
    except subprocess.TimeoutExpired:
        proc.kill()
        output_lines.append("\n(timed out after 30s)")
    return "".join(output_lines).strip() or "(empty)"


# --- Tool definitions: (description, schema, function) ---

TOOLS = {
    "read": (
        "Read file with line numbers (file path, not directory)",
        {"path": "string", "offset": "number?", "limit": "number?"},
        read,
    ),
    "write": (
        "Write content to file",
        {"path": "string", "content": "string"},
        write,
    ),
    "edit": (
        "Replace old with new in file (old must be unique unless all=true)",
        {"path": "string", "old": "string", "new": "string", "all": "boolean?"},
        edit,
    ),
    "glob": (
        "Find files by pattern, sorted by mtime",
        {"pat": "string", "path": "string?"},
        glob,
    ),
    "grep": (
        "Search files for regex pattern",
        {"pat": "string", "path": "string?"},
        grep,
    ),
    "bash": (
        "Run shell command",
        {"cmd": "string"},
        bash,
    ),
}


def run_tool(name, args):
    try:
        return TOOLS[name][2](args)
    except Exception as err:
        return f"error: {err}"


def make_schema(provider=None):
    if provider is None:
        provider = API_PROVIDER

    result = []
    for name, (description, params, _fn) in TOOLS.items():
        properties = {}
        required = []
        for param_name, param_type in params.items():
            is_optional = param_type.endswith("?")
            base_type = param_type.rstrip("?")
            properties[param_name] = {
                "type": "integer" if base_type == "number" else base_type
            }
            if not is_optional:
                required.append(param_name)

        if provider == "anthropic":
            # Anthropic 格式
            result.append({
                "name": name,
                "description": description,
                "input_schema": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            })
        else:
            # OpenAI/Qwen 格式
            result.append({
                "type": "function",
                "function": {
                    "name": name,
                    "description": description,
                    "parameters": {
                        "type": "object",
                        "properties": properties,
                        "required": required,
                    },
                },
            })
    return result


def call_api(messages, system_prompt):
    # 根据 provider 选择不同格式
    is_openai = API_PROVIDER != "anthropic"

    # 转换消息格式
    api_messages = format_messages_for_api(messages)

    # 构建请求体
    if is_openai:
        # OpenAI/Qwen 格式：system 在 messages 数组中
        request_body = {
            "model": MODEL,
            "max_tokens": 8192,
            "messages": [{"role": "system", "content": system_prompt}] + api_messages,
            "tools": make_schema(),
        }
    else:
        # Anthropic 格式
        request_body = {
            "model": MODEL,
            "max_tokens": 8192,
            "system": system_prompt,
            "messages": api_messages,
            "tools": make_schema(),
        }

    # 构建 headers
    headers = {
        "Content-Type": "application/json",
    }
    if is_openai:
        headers["Authorization"] = f"Bearer {OPENROUTER_KEY}"
    else:
        headers["anthropic-version"] = "2023-06-01"
        headers["x-api-key"] = os.environ.get("ANTHROPIC_API_KEY", "")

    request = urllib.request.Request(
        API_URL,
        data=json.dumps(request_body).encode(),
        headers=headers,
    )
    try:
        response = urllib.request.urlopen(request)
        return json.loads(response.read())
    except urllib.error.HTTPError as e:
        # 打印更详细的错误信息
        error_body = e.read().decode() if e.fp else ""
        raise Exception(f"HTTP {e.code}: {error_body}")


def separator():
    try:
        columns = os.get_terminal_size().columns
    except OSError:
        columns = 80
    return f"{DIM}{'─' * min(columns, 80)}{RESET}"


def render_markdown(text):
    return re.sub(r"\*\*(.+?)\*\*", f"{BOLD}\\1{RESET}", text)


def parse_response(response):
    """解析不同 API 的响应格式"""
    if API_PROVIDER == "anthropic":
        # Anthropic 格式：response["content"] 是数组
        return response.get("content", [])
    else:
        # OpenAI/Qwen 格式：response["choices"][0]["message"]
        message = response.get("choices", [{}])[0].get("message", {})
        blocks = []

        # 文本内容
        if message.get("content"):
            blocks.append({"type": "text", "text": message["content"]})

        # 工具调用
        for tool_call in message.get("tool_calls", []):
            func = tool_call.get("function", {})
            blocks.append({
                "type": "tool_use",
                "id": tool_call.get("id", ""),
                "name": func.get("name", ""),
                "input": json.loads(func.get("arguments", "{}")),
            })

        return blocks


def format_messages_for_api(messages):
    """将内部消息格式转换为 API 要求的格式"""
    if API_PROVIDER == "anthropic":
        # Anthropic 格式：直接返回
        return messages
    else:
        # OpenAI/Qwen 格式：需要转换
        formatted = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]

            if role == "user" and isinstance(content, list):
                # tool_results 列表需要转换为单独的 tool 消息
                for item in content:
                    if item.get("type") == "tool_result":
                        formatted.append({
                            "role": "tool",
                            "tool_call_id": item.get("tool_use_id", ""),
                            "content": item.get("content", ""),
                        })
            elif role == "assistant" and isinstance(content, list):
                # assistant 消息可能有 tool_use，需要提取为 tool_calls
                text_content = ""
                tool_calls = []
                for block in content:
                    if block.get("type") == "text":
                        text_content += block.get("text", "")
                    elif block.get("type") == "tool_use":
                        tool_calls.append({
                            "id": block.get("id", ""),
                            "type": "function",
                            "function": {
                                "name": block.get("name", ""),
                                "arguments": json.dumps(block.get("input", {})),
                            }
                        })
                # 只有文本内容时直接添加，有 tool_calls 时需要特殊处理
                if tool_calls:
                    formatted.append({
                        "role": role,
                        "content": text_content if text_content else None,
                        "tool_calls": tool_calls,
                    })
                elif text_content:
                    formatted.append({"role": role, "content": text_content})
            else:
                formatted.append(msg)

        # 移除 None 值
        for msg in formatted:
            keys_to_remove = [k for k, v in msg.items() if v is None]
            for k in keys_to_remove:
                del msg[k]

    return formatted


def main():
    print(f"{BOLD}minicode{RESET} | {DIM}{MODEL} ({API_PROVIDER}) | {os.getcwd()}{RESET}\n")
    messages = []
    system_prompt = f"Concise coding assistant. cwd: {os.getcwd()}"

    while True:
        try:
            print(separator())
            user_input = input(f"{BOLD}{BLUE}❯{RESET} ").strip()
            print(separator())
            if not user_input:
                continue
            if user_input in ("/q", "exit"):
                break
            if user_input == "/c":
                messages = []
                print(f"{GREEN}⏺ Cleared conversation{RESET}")
                continue


            messages.append({"role": "user", "content": user_input})

            # agentic loop: keep calling API until no more tool calls
            while True:
                response = call_api(messages, system_prompt)
                content_blocks = parse_response(response)
                tool_results = []

                for block in content_blocks:
                    if block["type"] == "text":
                        print(f"\n{CYAN}⏺{RESET} {render_markdown(block['text'])}")

                    if block["type"] == "tool_use":
                        tool_name = block["name"]
                        tool_args = block["input"]
                        arg_preview = str(list(tool_args.values())[0])[:50]
                        print(
                            f"\n{GREEN}⏺ {tool_name.capitalize()}{RESET}({DIM}{arg_preview}{RESET})"
                        )

                        result = run_tool(tool_name, tool_args)
                        result_lines = result.split("\n")
                        preview = result_lines[0][:60]
                        if len(result_lines) > 1:
                            preview += f" ... +{len(result_lines) - 1} lines"
                        elif len(result_lines[0]) > 60:
                            preview += "..."
                        print(f"  {DIM}⎿  {preview}{RESET}")

                        tool_results.append(
                            {
                                "type": "tool_result",
                                "tool_use_id": block["id"],
                                "content": result,
                            }
                        )

                messages.append({"role": "assistant", "content": content_blocks})

                if not tool_results:
                    break
                messages.append({"role": "user", "content": tool_results})

            print()

        except (KeyboardInterrupt, EOFError):
            break
        except Exception as err:
            import traceback
            print(f"{RED}⏺ Error: {err}{RESET}")
            traceback.print_exc()
            exit()


if __name__ == "__main__":
    # 加载环境变量
    load_dotenv()
    # 初始化config
    initConfig()
    main()
