# Learn Claude Code 学习记录

> 用于追踪 learn-claude-code 项目的新增内容学习进度
> 相对于 minicode 的差异学习大纲

---

## 基础信息

- **项目**: Learn Claude Code - AI 编程代理教学项目
- **项目类型**: 教学参考项目（12 个渐进式会话）
- **对比项目**: minicode（需先掌握的基础项目）
- **生成日期**: 2026-03-04
- **更新日期**: 2026-03-04

---

## 项目概述

Learn Claude Code 是一个纳米级 AI 代理系统的完整参考实现，通过 12 个渐进式会话（s01-s12）教学如何从零构建类似 Claude Code 的 AI 编程代理。

**核心理念**: "模型就是代理，我们的任务是给它工具并放手"

**技术栈**:
- Python 3.x + Anthropic SDK
- Next.js 16 + TypeScript + React 19（Web 平台）
- Tailwind CSS + Framer Motion

---

## 相对于 minicode 的新增内容总览

| 会话 | 主题 | 代码行数 | 相对于 minicode 的新增 |
|------|------|----------|------------------------|
| s01 | 代理循环 | ~107 | 基础相同，learn 使用官方 SDK |
| s02 | 工具使用 | ~149 | 基础相同 |
| **s03** | **待办事项** | **~210** | **minicode 无** |
| **s04** | **子代理** | **~184** | **minicode 无** |
| **s05** | **技能加载** | **~226** | **minicode 无** |
| **s06** | **上下文压缩** | **~248** | **minicode 只有 TODO，完整实现** |
| **s07** | **任务系统** | **~248** | **minicode 无** |
| **s08** | **后台任务** | **~234** | **minicode 无** |
| **s09** | **代理团队** | **~406** | **minicode 无** |
| **s10** | **团队协议** | **~487** | **minicode 无** |
| **s11** | **自主代理** | **~579** | **minicode 无** |
| **s12** | **工作树隔离** | **~781** | **minicode 无** |

---

## 详细学习大纲

### S01: Agent Loop 代理循环

**文件**: `agents/s01_agent_loop.py` (~107 行)

#### 核心类/函数
- `run_bash(command: str)` - 安全执行 shell 命令，阻止危险操作
- `agent_loop(messages: list)` - 核心代理循环函数

#### 关键实现逻辑
```
1. while True:
2.     调用 LLM 生成响应 (client.messages.create)
3.     检查 stop_reason:
       - "tool_use" → 执行工具，追加结果到 messages（继续循环）
       - "end_turn" → 任务完成，返回最终响应
       - "max_tokens" → 达到 token 上限
       - "stop_sequence" → 遇到停止序列
```

**stop_reason 枚举值**:
| 值 | 含义 | 行为 |
|---|------|------|
| `tool_use` | 模型调用了工具 | 继续循环 |
| `end_turn` | 模型认为任务已完成 | 返回响应 |
| `max_tokens` | 达到最大 token 限制 | 返回响应 |
| `stop_sequence` | 遇到停止序列 | 返回响应 |

**核心理解**: 只有 `tool_use` 才会继续循环，其他都是"结束信号"

#### 设计模式
- **Agent Loop Pattern**: 循环调用 LLM → 工具执行 → 结果反馈
- **消息状态累积**: 持续累积对话历史

#### 面试问答
- Q: Agent Loop 的核心流程是什么？
- Q: stop_reason 有哪些枚举值？
- Q: 为什么只有 tool_use 才会继续循环？
- Q: 如何处理工具执行失败的情况？

#### 学习建议
- 理解最基础的 ReAct 循环模式
- 对比 minicode.py 的实现差异（urllib vs SDK）

---

### S02: Tool Use 工具使用

**文件**: `agents/s02_tool_use.py` (~149 行)

#### 核心类/函数
- `safe_path(p: str)` - 路径安全验证，防止目录穿越攻击
- `run_bash(command: str)` - 执行 shell 命令
- `run_read(path: str)` - 读取文件
- `run_write(path: str, content: str)` - 写入文件
- `run_edit(path: str, old: str, new: str)` - 编辑文件
- `TOOL_HANDLERS` - 工具处理器字典（核心调度）

#### 关键实现逻辑
- **工具调度**: 通过 `TOOL_HANDLERS[name](args)` 映射调用
- **Schema 定义**: 每个工具的 `input_schema` 规范
- **路径安全**: `safe_path` 确保文件操作在工作目录内

**4 个工具定义**:
| 工具 | 参数 | 说明 |
|-----|------|------|
| `bash` | command: string | 执行 shell 命令 |
| `read_file` | path: string, limit?: integer | 读取文件（可选行数限制） |
| `write_file` | path: string, content: string | 写入文件 |
| `edit_file` | path: string, old_text: string, new_text: string | 精确替换文本 |

**input_schema 的作用**:
1. 告诉 LLM 工具需要什么参数（参数名、类型、必填/可选）
2. SDK 自动进行类型校验
3. 生成 API 文档和调用界面

**为什么有了 bash 还要专用工具**:
1. **Token 效率**: bash 需要模型生成命令字符串，专用工具直接传参更紧凑
2. **语义明确**: 工具名本身就是意图，模型更容易理解
3. **安全控制**: 可以细粒度控制"只能读不能写"
4. **输出格式**: 专用工具返回格式一致，模型更容易解析

#### 设计模式
- **Dispatch Map Pattern**: 工具名称 → 处理函数映射
- **Schema Validation**: JSON Schema 定义工具输入规范

#### 面试问答
- Q: 如何添加新的工具？
- Q: 工具的 input_schema 有什么作用？（重点）
- Q: safe_path 防止的是什么安全问题？
- Q: 为什么有了 bash 还要专用工具？（重点）

#### 学习建议
- 理解工具注册和调度的机制
- 掌握 Schema 定义规范
- 思考专用工具 vs bash 的设计权衡

---

### S03: TodoWrite 待办事项系统 ⭐ 新增

**文件**: `agents/s03_todo_write.py` (~210 行)

> **核心理念**: "The agent can track its own progress -- and I can see it."
>
> 让代理能够自我追踪任务进度，引入内部状态管理。

#### 1. 架构流程图

```
                    +------------------+
                    |   User Prompt    |
                    +--------+---------+
                             |
                             v
                    +------------------+
                    |       LLM        |
                    +--------+---------+
                             |
              +--------------+--------------+
              |                             |
              v                             v
    +---------------------+     +------------------+
    |   Tool: bash        |     |   Tool: todo     |
    |   read_file        |     | (新增)           |
    |   write_file       |     +--------+---------+
    |   edit_file        |              |
    +--------+------------              v
             |                  +------------------+
             |                  |  TodoManager     |
             |                  |  state           |
             |                  |  [ ] task A     |
             |                  |  [>] task B     |
             |                  |  [x] task C     |
             |                  +--------+---------+
             |                           |
             |           +---------------+---------------+
             |           |                               |
             |           v                               v
             |   +----------------+          +-------------------+
             |   | rounds_since   |          |  tool_result      |
             |   | _todo < 3      |          |  返回给 LLM       |
             |   | 正常继续循环    |          +-------------------+
             |   +----------------+                      |
             |                                              v
             |           +----------------+    +-------------------+
             |           | rounds_since   |    | 注入 <reminder>   |
             |           | _todo >= 3     |    | 提醒更新 todo     |
             |           +----------------+    +-------------------+
             |                      |                      |
             +----------------------+----------------------+
                                    |
                                    v
                           +------------------+
                           |  messages.append |
                           |  (继续循环)       |
                           +------------------+
```

#### 2. 核心类/函数详解

##### TodoManager 类（第 51-86 行）

```python
class TodoManager:
    def __init__(self):
        self.items = []  # 内存中的待办列表

    def update(self, items: list) -> str:
        """验证并更新待办列表"""
        # ... 验证逻辑
        self.items = validated
        return self.render()

    def render(self) -> str:
        """渲染待办为可读字符串"""
        # 格式: [ ] #1 task A / [>] #2 task B / [x] #3 task C
```

**全局实例**: `TODO = TodoManager()` (第 88 行)

##### agent_loop 函数（第 163-190 行）

相比 s02，新增了 `rounds_since_todo` 计数器：

```python
def agent_loop(messages: list):
    rounds_since_todo = 0  # 初始化计数器
    while True:
        response = client.messages.create(...)  # 调用 LLM

        # 执行工具，收集结果
        results = []
        used_todo = False
        for block in response.content:
            if block.type == "tool_use":
                output = handler(**block.input)
                results.append({...})
                if block.name == "todo":
                    used_todo = True

        # Nag Reminder 逻辑
        rounds_since_todo = 0 if used_todo else rounds_since_todo + 1
        if rounds_since_todo >= 3:
            results.insert(0, {"type": "text", "text": "<reminder>Update your todos.</reminder>"})

        messages.append({"role": "user", "content": results})
```

#### 3. 新增工具：todo（第 157-158 行）

```python
{"name": "todo",
 "description": "Update task list. Track progress on multi-step tasks.",
 "input_schema": {
     "type": "object",
     "properties": {
         "items": {
             "type": "array",
             "items": {
                 "type": "object",
                 "properties": {
                     "id": {"type": "string"},
                     "text": {"type": "string"},
                     "status": {
                         "type": "string",
                         "enum": ["pending", "in_progress", "completed"]
                     }
                 },
                 "required": ["id", "text", "status"]
             }
         }
     },
     "required": ["items"]
 }}
```

**调用示例**:
```python
todo(items=[
    {"id": "1", "text": "Read requirements", "status": "completed"},
    {"id": "2", "text": "Write code", "status": "in_progress"},
    {"id": "3", "text": "Test", "status": "pending"}
])
```

#### 4. 验证规则详解

| 规则 | 代码位置 | 说明 |
|-----|---------|------|
| 最多 20 项 | 第 56-57 行 | `if len(items) > 20: raise ValueError` |
| 每项必须有 text | 第 64-65 行 | `if not text: raise ValueError` |
| status 只能是有效值 | 第 66-67 行 | 必须是 pending/in_progress/completed |
| in_progress 只能 1 个 | 第 71-72 行 | 强制串行化，防止并行失控 |

#### 5. Nag Reminder 机制详解

**工作流程**:

```
第 1 轮: LLM 调用 todo → used_todo=True → rounds_since_todo = 0
第 2 轮: LLM 调用 bash → used_todo=False → rounds_since_todo = 1
第 3 轮: LLM 调用 read → used_todo=False → rounds_since_todo = 2
第 4 轮: LLM 调用 write → used_todo=False → rounds_since_todo = 3
         → 触发 reminder → 注入 "<reminder>Update your todos.</reminder>"
```

**关键点**:
- reminder 插入到 `results[0]`（最前面）
- 作为 user 消息的一部分，下一轮 LLM 会看到
- **软约束**：LLM 可以选择忽略

#### 6. System Prompt 变化

**s02**:
```
You are a coding agent at {WORKDIR}. Use tools to solve tasks. Act, don't explain.
```

**s03** (新增内容):
```
You are a coding agent at {WORKDIR}.
Use the todo tool to plan multi-step tasks.
Mark in_progress before starting, completed when done.
Prefer tools over prose.
```

#### 7. 设计模式深入

##### Stateful Agent（状态化代理）
- s01-s02: 无状态，每次调用独立
- s03: 引入 `TodoManager` 维护内部状态
- LLM 可以"记住"任务进度

##### Reminder Injection（提醒注入）
- 在 agent_loop 运行时动态注入
- 不修改 System Prompt（运行时注入更灵活）
- 类似"操作系统中断"机制

##### Task Gating（任务门控）
- 通过 `in_progress_count > 1` 强制拒绝
- 防止 LLM "同时做多件事"
- 本质是有限状态机 (FSM)

#### 8. 为什么需要这些机制？

**LLM 本质问题**:
1. **无状态**: 每次 API 调用是独立的，不记得上一步
2. **自由发挥**: 没有约束时，可能跳过步骤
3. ** Token 限制**: 上下文会累积，需要管理

**解决方案层次**:

| 层次 | 机制 | 约束力 | 示例 |
|-----|------|-------|------|
| L0 | 无约束 | 无 | LLM 自由发挥，可能跳过步骤 |
| L1 | 软约束 | 低 | Nag Reminder，期待响应 |
| L2 | 硬约束 | 中 | in_progress 只能 1 个 |
| L3 | 持久化 | 高 | s07 TaskSystem，外部存储 |

#### 9. 与 s02 的对比

| 特性 | s02 | s03 |
|-----|-----|-----|
| 状态管理 | 无 | TodoManager |
| 任务规划 | 无 | todo 工具 |
| 多步骤任务 | 可能遗漏 | 可追踪 |
| 并行控制 | 无 | 强制串行化 |
| 提醒机制 | 无 | Nag Reminder |

#### 10. 面试问答

- Q: 为什么要限制同时只能有 1 项 in_progress？
  - A: 强制串行化执行，避免并行任务失控。简化设计，适合基础教学（复杂任务系统如 s07 支持并行）。

- Q: Nag Reminder 机制如何与 ReAct 循环配合？
  - A: 正常：LLM 自主调用 todo 更新；异常：连续 3 轮未调用 → 注入提醒到 messages → 期待 LLM 响应。

- Q: TodoWrite 与 s07 Task System 的区别？
  - A: 待补充（s07 对比）

- Q: 如何防止 LLM 忽略待办提醒？
  - A: 当前是软约束。可选方案：强制要求更新 todo 后再继续 agent-loop，或拒绝执行其他工具。

- Q: 为什么需要强制规则来约束 LLM？
  - A: LLM 本质无状态，需要显式状态管理。状态机防止"混沌"，确保步骤不被跳过。

#### 11. 学习建议

- 重点理解状态验证逻辑（每个规则的目的）
- 对比有/无 TodoManager 的区别
- 思考 Nag Reminder 的触发条件
- 理解"软约束" vs "硬约束"的权衡

---

### S04: Subagent 子代理模式 ⭐ 新增

**文件**: `agents/s04_subagent.py` (~184 行)

> **核心理念**: "Process isolation gives context isolation for free."
>
> 进程隔离 = 上下文隔离

#### 1. 架构流程图

```
┌─────────────────────────────────────────────────────┐
│                   Parent Agent                       │
│  messages=[user: "分析项目", assistant: ...]       │
│                                                     │
│    tool: task                                      │
│    prompt="探索 src 目录结构"                        │
└──────────────────────┬──────────────────────────────┘
                       │
                       │ 调用 run_subagent()
                       v
┌─────────────────────────────────────────────────────┐
│                   Subagent                          │
│  messages=[user: "探索 src 目录结构"]  ← fresh     │
│                                                     │
│  [探索文件，执行 bash/read 操作...]                  │
│  (最多 30 轮循环)                                   │
│                                                     │
│  return "src 包含: main.py, utils/"  ← summary    │
└──────────────────────┬──────────────────────────────┘
                       │
                       │ 返回摘要
                       v
        Parent 继续，messages 不包含子代理细节
```

#### 2. 核心函数详解

##### run_subagent 函数（第 115-133 行）

```python
def run_subagent(prompt: str) -> str:
    # 1. 创建独立上下文
    sub_messages = [{"role": "user", "content": prompt}]  # fresh context

    # 2. 子代理循环（最多 30 轮）
    for _ in range(30):  # safety limit
        response = client.messages.create(
            model=MODEL, system=SUBAGENT_SYSTEM,
            messages=sub_messages,  # 独立消息列表
            tools=CHILD_TOOLS,       # 子代理工具集
            max_tokens=8000,
        )
        sub_messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason != "tool_use":
            break

        # 执行工具...
        results = []
        for block in response.content:
            if block.type == "tool_use":
                output = handler(**block.input)
                results.append({...})
        sub_messages.append({"role": "user", "content": results})

    # 3. 只返回最终文本摘要
    return "".join(b.text for b in response.content if hasattr(b, "text"))
```

**关键点**:
- 独立消息列表 (`sub_messages = []`)
- 工具子集 (`CHILD_TOOLS`，没有 task 工具)
- 摘要返回（不包含中间工具调用）
- 最多 30 轮限制

#### 3. 工具定义

##### task 工具（第 137-140 行）

```python
{"name": "task",
 "description": "Spawn a subagent with fresh context. It shares the filesystem but not conversation history.",
 "input_schema": {
     "type": "object",
     "properties": {
         "prompt": {"type": "string"},        # 任务描述
         "description": {"type": "string"}    # 简短描述
     },
     "required": ["prompt"]
 }}
```

##### CHILD_TOOLS（第 102-111 行）

子代理拥有基础工具（无 task，防止递归）：
- bash
- read_file
- write_file
- edit_file

#### 4. 为什么 task 工具不用 TOOL_HANDLERS 处理？

| 工具类型 | 处理方式 | 原因 |
|---------|---------|------|
| bash/read/write/edit | TOOL_HANDLERS | 单次执行，调用→返回 |
| task | agent_loop 特殊处理 | 需要启动新的对话循环 |

```python
# TOOL_HANDLERS 适合简单工具
TOOL_HANDLERS = {
    "bash": lambda **kw: run_bash(kw["command"]),
    # ...
}

# task 需要独立循环，在 agent_loop 中特殊处理
for block in response.content:
    if block.name == "task":
        output = run_subagent(block.input["prompt"])  # 这里是独立循环！
```

#### 5. System Prompt 对比

| 角色 | System Prompt |
|-----|--------------|
| 父代理 | "Use the task tool to delegate exploration or subtasks." |
| 子代理 | "Complete the given task, then summarize your findings." |

#### 6. 串行执行特性

```python
# agent_loop 中
for block in response.content:
    if block.name == "task":
        output = run_subagent(...)  # 阻塞等待完成
```

- 子代理是**串行执行**的（一次一个）
- 不需要限制子代理数量（不存在并行）
- 如果需要并行，要到 s09 代理团队

#### 7. 为什么需要子代理？

| 场景 | 不用子代理 | 用子代理 |
|-----|----------|---------|
| 探索代码库 | 主代理上下文爆炸 | 子代理独立探索 |
| 多任务并行 | 串行执行 | 可生成多个子代理并行 |
| 复杂任务 | 主代理记不住细节 | 子代理专注单一任务 |
| Token 限制 | 上下文太长 | 只返回摘要，省 Token |

#### 8. 与 MCP 工具的整合

MCP 工具也是类似的整合方式：

```python
# MCP 工具发现 → 格式转换 → 合并到工具列表
PARENT_TOOLS = CHILD_TOOLS + [{"name": "task", ...}] + mcp_tools
```

#### 9. 工具多了如何优化？

**问题**：工具太多，LLM 选错工具

**方案**:
1. **区分工具描述**：避免近似描述
2. **多级路由**：先选类别，再选具体工具
3. **动态注入**：根据任务类型注入相关工具
4. **Few-shot 示例**：在 System Prompt 中给示例

**选错工具如何兜底**:
- Schema 校验：类型错误会被 SDK 拦截
- Handler 错误处理：try-catch 返回错误
- LLM 重试：收到错误后选择其他工具
- 强制重置：连续多次失败，强制干预

#### 10. 面试问答

- Q: 子代理与主代理的区别是什么？
  - A: 子代理有独立 messages[]，不继承父代理历史，专注于单一任务后返回摘要。

- Q: 为什么子代理的对话历史是独立的？
  - A: 避免父代理上下文爆炸，子代理的中间过程不需要保留在主对话中。

- Q: 什么时候应该使用子代理？
  - A: 探索代码库、多步骤复杂任务、长时间运行的任务。

- Q: 子代理返回摘要 vs 返回完整对话的权衡？
  - A: 摘要省 Token，但可能丢失细节；完整对话保留信息，但上下文爆炸。

#### 11. 学习建议

- 理解独立上下文的实现方式
- 理解 task 工具的特殊处理方式（不是简单 TOOL_HANDLERS）
- 理解串行执行特性
- 思考 MCP 工具整合方式

---

### S05: Skill Loading 动态技能加载 ⭐ 新增

**文件**: `agents/s05_skill_loading.py` (~226 行)

> **核心理念**: "Don't put everything in the system prompt. Load on demand."

#### 1. 架构流程图

```
┌─────────────────────────────────────────────────────┐
│              Layer 1: System Prompt                 │
│  (技能名称 + 描述，~100 tokens/技能)                 │
├─────────────────────────────────────────────────────┤
│  Skills available:                                   │
│    - pdf: Process PDF files...                    │
│    - code-review: Review code...                  │
│    - agent-builder: Build agents...                │
└─────────────────────────────────────────────────────┘
                       │
                       │ LLM 调用 load_skill("pdf")
                       ▼
┌─────────────────────────────────────────────────────┐
│              Layer 2: tool_result                   │
│  (完整技能内容，按需加载)                            │
├─────────────────────────────────────────────────────┤
│  <skill name="pdf">                                 │
│    # PDF Processing Skill                          │
│    ...完整内容...                                   │
│  </skill>                                           │
└─────────────────────────────────────────────────────┘
```

#### 2. 核心类详解

##### SkillLoader 类（第 57-103 行）

```python
class SkillLoader:
    def __init__(self, skills_dir: Path):
        self.skills_dir = skills_dir
        self.skills = {}
        self._load_all()  # 启动时扫描所有技能

    def _load_all(self):
        """扫描 skills/*/SKILL.md"""
        for f in sorted(self.skills_dir.rglob("SKILL.md")):
            text = f.read_text()
            meta, body = self._parse_frontmatter(text)
            name = meta.get("name", f.parent.name)
            self.skills[name] = {"meta": meta, "body": body}

    def get_descriptions(self) -> str:
        """Layer 1: 返回技能名称和描述"""
        # 格式: "  - pdf: Process PDF files..."

    def get_content(self, name: str) -> str:
        """Layer 2: 返回完整技能内容"""
        return f"<skill name=\"{name}\">\n{skill['body']}\n</skill>"
```

#### 3. 技能目录结构

```
skills/
├── pdf/
│   ├── SKILL.md           ← frontmatter + 内容
│   └── references/
├── code-review/
│   └── SKILL.md
├── agent-builder/
│   ├── SKILL.md
│   └── references/
└── mcp-builder/
    └── SKILL.md
```

#### 4. SKILL.md 格式

```yaml
---
name: pdf
description: Process PDF files - extract text, create PDFs, merge documents.
---

# PDF Processing Skill

## Reading PDFs
...详细步骤...

## Creating PDFs
...详细步骤...
```

**Frontmatter 字段**:
| 字段 | 作用 |
|-----|------|
| `name` | 技能唯一标识 |
| `description` | 告诉 LLM 什么时候使用（Use when user asks to...） |
| `tags` | 额外分类标签（可选） |

#### 5. 两层注入策略

| 层级 | 位置 | Token 消耗 | 作用 |
|-----|------|-----------|------|
| Layer 1 | System Prompt | ~100/skill | 知道有哪些技能可用 |
| Layer 2 | tool_result | 按需 | 需要时加载完整内容 |

**为什么分层**：避免 System Prompt 爆炸，按需加载。

#### 6. Skill vs Tool 的区别

| 类型 | 作用 | 执行方式 |
|-----|------|---------|
| **Tool** | 直接执行操作 | LLM 调用 → 立即执行 |
| **Skill** | 提供知识/指导 | LLM 理解后 → 自己调用工具执行 |

**比喻**：
- Tool：厨房里的厨具，可以直接用
- Skill：菜谱，告诉你怎么做饭，需要自己拿厨具来做

#### 7. Skill 的两种写法

| Skill 类型 | 需要预定义 Tool | 示例 |
|-----------|----------------|------|
| "写代码"类型 | ❌ 不需要 | mcp-builder, pdf |
| "调用工具"类型 | ✅ 需要 | database-debugger |

**区别**：
- mcp-builder：告诉 LLM"如何写代码"，LLM 用现有工具实现
- database-debugger：告诉 LLM"调用 check_db"，需要预定义工具

#### 8. 本地 vs 云端部署

| 部署 | 加载代码 | Skill 写法 |
|-----|---------|-----------|
| **本地** | 可以动态写代码执行 | 写完整代码 |
| **云端** | 不应该动态加载 | 只写调用序列，用 MCP 预定义工具 |

**云端最佳实践**：
- Tool 用 MCP 预定义
- Skill 只提供流程 + 判断规则
- 不动态执行用户代码

#### 9. OnCall Agent 场景

```
用户问题 → LLM 判断类型 → 匹配 skill → 执行 RPC 序列 → LLM 分析结果 → 返回方案
```

**架构**：
```
┌─────────────────────────────────────┐
│           云端 Agent                  │
├─────────────────────────────────────┤
│  预定义工具（MCP / Function）        │
│  - check_db                         │
│  - check_slow_queries              │
│  - restart_service                 │
├─────────────────────────────────────┤
│  Skill:                            │
│  - 什么时候用什么工具                │
│  - 判断规则                          │
└─────────────────────────────────────┘
```

#### 10. 部署路径问题

**问题**：`SKILLS_DIR = WORKDIR / "skills"`，如果从 `agents/` 目录运行会找不到

**解决**：从项目根目录运行
```bash
cd /Users/vagrant/dev/code/python/learn-claude-code
python agents/s05_skill_loading.py
```

#### 11. 安全考虑：Prompt/Skill 注入

| 攻击类型 | 说明 | 防护方案 |
|---------|------|---------|
| **Prompt 注入** | 用户输入恶意指令 | 输入过滤、System Prompt 防御 |
| **Skill 注入** | 篡改 skill 内容 | 签名验证、分级信任 |
| **工具注入** | 伪装成合法工具 | 输出审查 |

**防护层次**：
1. 输入层：注入模式过滤
2. Skill 层：签名验证、分级信任
3. LLM 层：System Prompt 防御
4. 输出层：敏感信息过滤

#### 12. 面试问答

- Q: 为什么采用两层注入策略？
  - A: 避免 System Prompt 爆炸，Layer 1 知道有哪些技能，Layer 2 按需加载。

- Q: Skill 和 Tool 的区别？
  - A: Tool 直接执行，Skill 提供知识让 LLM 理解后自己执行。

- Q: 云端部署需要注意什么？
  - A: 不动态加载代码，用 MCP 预定义工具，Skill 只写调用序列。

- Q: 如何防止 Prompt 注入？
  - A: 多层防护：输入过滤、签名验证、System Prompt 防御、输出审查。

#### 13. 学习建议

- 查看 `skills/` 目录下的实际技能定义
- 对比 Layer 1 和 Layer 2 的内容差异
- 理解 Skill "写代码" vs "调用工具" 两种写法的区别

---

### S06: Context Compact 上下文压缩 ⭐ 完整实现

**文件**: `agents/s06_context_compact.py` (~248 行)

> **核心理念**: "The agent can forget strategically and keep working forever."
>
> 策略性遗忘，让 agent 可以永久工作

#### 1. 架构流程图

```
┌─────────────────────────────────────────────────────────────┐
│                   Tool Call Result                         │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
        ┌─────────────────────────────────┐
        │   Layer 1: micro_compact        │  ← 每轮执行（静默）
        │   保留最近 3 个 tool_result     │
        │   旧的替换为 [Previous: used X] │
        └─────────────────┬───────────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │  Check: tokens > 50000?  │
              └───────────┬───────────┘
                    │             │
                   no            yes
                    │             │
                    ▼             ▼
              continue    ┌─────────────────────┐
                           │   Layer 2:         │  ← 自动触发
                           │   auto_compact     │
                           │   1. 保存到文件    │
                           │   2. LLM 总结      │
                           │   3. 替换消息      │
                           └─────────┬───────────┘
                                     │
                                     ▼
                           ┌─────────────────────┐
                           │   Layer 3:          │  ← 手动触发
                           │   compact 工具      │
                           │   (同 auto_compact)│
                           └─────────────────────┘
```

#### 2. 核心函数详解

##### estimate_tokens（第 61-63 行）

```python
def estimate_tokens(messages: list) -> int:
    """Rough token count: ~4 chars per token."""
    return len(str(messages)) // 4
```

##### micro_compact（第 67-93 行）

每轮执行，静默压缩：

```python
KEEP_RECENT = 3  # 保留最近 3 个

def micro_compact(messages: list):
    # 找到所有 tool_result
    tool_results = [...]

    # 保留最近 KEEP_RECENT，旧的替换为占位符
    for result in tool_results[:-KEEP_RECENT]:
        result["content"] = f"[Previous: used {tool_name}]"
```

**示例**:
```
压缩前:
[tool_result: read file a.py - 500行代码]
[tool_result: bash ls]
[tool_result: read file b.py - 300行代码]

压缩后:
[tool_result: [Previous: used read_file]]
[tool_result: [Previous: used bash]]
[tool_result: read file b.py - 300行代码]
```

##### auto_compact（第 97-120 行）

token > 50000 时自动触发：

```python
THRESHOLD = 50000
TRANSCRIPT_DIR = Path(".transcripts/")

def auto_compact(messages: list):
    # 1. 保存完整记录到 .transcripts/
    transcript_path = TRANSCRIPT_DIR / f"transcript_{int(time.time())}.jsonl"

    # 2. 让 LLM 总结
    response = client.messages.create(
        messages=[{"role": "user", "content":
            "Summarize: 1) What was accomplished 2) Current state 3) Key decisions"}]
    )

    # 3. 替换消息
    return [
        {"role": "user", "content": f"[Transcript: {path}] {summary}"},
        {"role": "assistant", "content": "Understood. Continuing."},
    ]
```

#### 3. 三层压缩策略

| 层级 | 触发条件 | 压缩方式 |
|------|----------|----------|
| Layer 1 (Micro) | 每轮执行 | 保留最近 3 个 tool 结果，旧替换为占位符 |
| Layer 2 (Auto) | token > 50000 | 保存完整记录，要求 LLM 总结 |
| Layer 3 (Manual) | 手动触发 | 通过 `compact` 工具触发 |

#### 4. 关键参数

| 参数 | 值 | 说明 |
|-----|---|------|
| `THRESHOLD` | 50000 | 触发自动压缩的 token 阈值 |
| `KEEP_RECENT` | 3 | micro_compact 保留的数量 |
| `TRANSCRIPT_DIR` | `.transcripts/` | 压缩前保存的目录 |

#### 5. 代码问题讨论

**问题 1：compact 工具定义了参数但未使用**

```python
# 定义了参数
{"name": "compact",
 "input_schema": {
     "properties": {
         "focus": {"type": "string", "description": "What to preserve"}
     }
 }}

# 实际未使用
"compact": lambda **kw: "Manual compression requested."
```

**问题**：LLM 以为传参会有特殊处理，实际没有，会造成误解。

**原则**：工具定义要精确，要么用，要么不定义。

**优化方案**：
```python
# 方案 1: 使用参数
"compact": lambda **kw: auto_compact(messages, focus=kw.get("focus"))

# 方案 2: 不定义参数
{"name": "compact", "input_schema": {"type": "object", "properties": {}}}
```

**问题 2：手动压缩流程不合理**

当前：用户要求压缩 → LLM 判断 → 调用 compact → 压缩
问题：多了一层 LLM 判断，浪费 token

**优化方案**：
```python
# 检测用户压缩指令，直接压缩
if "compress" in user_input.lower():
    messages[:] = auto_compact(messages)
    # 结合新输入，重新给 LLM
```

#### 6. 设计模式

- **Strategic Forgetting**: 策略性遗忘
- **Transcript Persistence**: 完整记录持久化
- **Token Budget Management**: token 预算管理

#### 7. 与 s03/s05 的关系

| 会话 | 机制 |
|-----|------|
| s03 | TodoManager 内部状态 |
| s05 | Skill 按需加载 |
| **s06** | **上下文压缩**（让 agent 可以永久工作） |

#### 8. 面试问答

- Q: 三层压缩策略具体是什么？
  - A: Layer 1 每轮微压缩，Layer 2 超阈值自动压缩，Layer 3 手动触发。

- Q: token 阈值如何计算？50000 是如何确定的？
  - A: 简单估算：len(str(messages)) // 4。50000 是经验值，约等于模型上下文窗口的一半。

- Q: 压缩后如何保证信息不丢失？
  - A: 完整记录保存到 .transcripts/ 目录，LLM 总结包含关键信息。

- Q: compact 工具为什么要避免定义未使用的参数？
  - A: 会误导 LLM，工具定义要精确。

#### 9. 学习建议

- 重点理解 micro_compact 的替换逻辑
- 思考信息保留 vs token 节省的权衡
- 注意工具参数定义和使用的一致性

---

### S07: Task System 持久化任务系统 ⭐ 新增

**文件**: `agents/s07_task_system.py` (~248 行)

> **核心理念**: "State that survives compression -- because it's outside the conversation."
>
> 状态存活于压缩之外 — 因为它在对话之外

#### 1. 对比 s03 TodoManager

| 特性 | s03 TodoManager | s07 TaskManager |
|-----|----------------|----------------|
| 存储位置 | 内存 | 文件 (`.tasks/`) |
| 持久化 | ❌ 否 | ✅ 是 |
| 依赖管理 | ❌ 无 | ✅ 有 (blockedBy/blocks) |
| 上下文压缩后 | 丢失 | 保留 |

#### 2. 架构流程

```
.tasks/
├── task_1.json  {"id":1, "subject":"实现登录", "status":"completed", "blockedBy":[], "blocks":[2]}
├── task_2.json  {"id":2, "subject":"实现用户页", "status":"pending", "blockedBy":[1], "blocks":[3]}
└── task_3.json  {"id":3, "subject":"实现订单页", "status":"pending", "blockedBy":[2], "blocks":[]}

依赖链:
task_1 (completed) → task_2 (pending) → task_3 (pending)
```

#### 3. 核心函数详解

##### TaskManager 类（第 46-124 行）

```python
class TaskManager:
    def create(self, subject: str, description: str = "") -> str:
        task = {
            "id": self._next_id,
            "subject": subject,
            "status": "pending",
            "blockedBy": [],   # 阻塞此任务的前置任务
            "blocks": [],      # 此任务阻塞的其他任务
        }

    def update(self, task_id: int, status: str = None,
               add_blocked_by: list = None, add_blocks: list = None):
        # 更新状态或依赖
        if status == "completed":
            self._clear_dependency(task_id)  # 自动解除依赖

    def _clear_dependency(self, completed_id: int):
        # 完成任务后，从所有任务的 blockedBy 中移除
        for task in tasks:
            if completed_id in task["blockedBy"]:
                task["blockedBy"].remove(completed_id)
```

#### 4. 任务工具

| 工具 | 功能 |
|-----|------|
| task_create | 创建单个任务 |
| task_update | 更新状态/依赖 |
| task_list | 列出所有任务 |
| task_get | 获取任务详情 |

**缺失**：任务拆分工具 (task_breakdown)

#### 5. 依赖管理流程

```
1. 创建任务 A (id=1)
2. 创建任务 B (id=2)，设置 addBlockedBy=[1]
   → task_2.blockedBy = [1]
   → task_1.blocks = [2] (双向)
3. 更新 A 为 completed
   → task_1.status = "completed"
   → _clear_dependency(1) → task_2.blockedBy = []
   → task_2 可以开始执行
```

#### 6. LLM 自主决策

agent_loop 不指定要调用什么工具，LLM 根据 System Prompt + 可用工具 + 任务需求自主决策。

```
用户: "帮我实现登录功能"
    ↓
LLM 自主决定: "我应该创建一个任务来跟踪进度"
    ↓
调用 task_create(subject="实现登录")
    ↓
继续循环...
```

#### 7. 上下文压缩后的恢复

```
1. 触发上下文压缩 (s06)
   → messages 被压缩成 summary
   → .tasks/task_1.json 还在！

2. LLM 需要继续工作时
   → 调用 task_list() 或 task_get(1)
   → TaskManager 读取文件，返回完整任务信息
   → LLM 恢复上下文，继续工作
```

**核心**：任务信息保存在文件系统，按需加载，不受压缩影响。

#### 8. 设计讨论：Task 管理应该是 Skill

**当前设计**：任务工具内置在 TOOL_HANDLERS 中

**问题**：
- 缺少任务拆分工具 (task_breakdown)
- 所有 agent 都强制包含任务功能

**更好的设计**：作为 Skill（符合 s05 理念）
```
agent_loop
├── 基础工具 (bash/read/write/edit)
└── task_skill (可选加载)
    ├── task_create
    ├── task_update
    ├── task_breakdown
    └── ...
```

**优势**：
| 方面 | 内置 | Skill |
|-----|------|-------|
| 灵活性 | 必须包含 | 按需加载 |
| 模块化 | 强耦合 | 解耦 |
| 用户选择 | 无 | 可选启用 |

#### 9. 面试问答

- Q: TaskManager 与 TodoManager 的区别？
  - A: s03 内存存储，s07 文件持久化；s03 无依赖，s07 有依赖图。

- Q: 任务依赖如何实现自动解锁？
  - A: 任务完成时调用 _clear_dependency()，从所有任务的 blockedBy 中移除。

- Q: 为什么选择文件持久化而非数据库？
  - A: 简化实现，无需额外依赖，符合纳米级教学项目定位。

- Q: 任务拆分应该放在哪里？
  - A: 作为 Skill 更合理，符合模块化设计。

#### 10. 学习建议

- 理解文件结构和依赖图的实现
- 对比 s03 的内存待办 vs s07 的持久化任务
- 思考任务管理作为 Skill 的设计

---

### S08: Background Tasks 后台任务 ⭐ 新增

**文件**: `agents/s08_background_tasks.py` (~234 行)

> **核心理念**: "Fire and forget -- the agent doesn't block while the command runs."
>
> 触发即返回 — agent 执行命令时不会阻塞

#### 1. 对比 s07

| 特性 | s07 TaskManager | s08 BackgroundManager |
|-----|----------------|---------------------|
| 任务类型 | 持久化任务 | 临时后台命令 |
| 执行方式 | LLM 手动管理 | 自动异步 |
| 状态管理 | 手动更新 | 自动通知 |

#### 2. 架构流程

```
┌─────────────────────────────────────────────────────────────┐
│                        Main Thread                           │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  agent_loop                                          │   │
│  │    1. drain_notifications() → 注入完成通知           │   │
│  │    2. 调用 LLM                                       │   │
│  │    3. 执行工具 (可能启动后台任务)                     │   │
│  └─────────────────────────────────────────────────────┘   │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
   Thread 1      Thread 2      Thread 3
   (npm i)      (pytest)      (git push)
        │              │              │
        └──────────────┼──────────────┘
                       ▼
              Notification Queue
                       │
                       ▼
              下次 LLM 调用时注入
```

#### 3. 核心函数详解

##### BackgroundManager 类（第 49-108 行）

```python
class BackgroundManager:
    def __init__(self):
        self.tasks = {}           # task_id -> {status, result, command}
        self._notification_queue = []  # 完成通知队列
        self._lock = threading.Lock()

    def run(self, command: str) -> str:
        """启动后台线程，立即返回 task_id"""
        task_id = str(uuid.uuid4())[:8]
        thread = threading.Thread(target=self._execute, args=(task_id, command))
        thread.start()
        return f"Background task {task_id} started: {command[:80]}"

    def _execute(self, task_id, command):
        """在线程中执行命令，完成后推送到队列"""
        # 执行命令...
        self._notification_queue.append({task_id, status, result})

    def drain_notifications(self) -> list:
        """抽取并清空通知队列"""
        with self._lock:
            notifs = list(self._notification_queue)
            self._notification_queue.clear()
        return notifs
```

#### 4. 通知注入（第 189-196 行）

```python
def agent_loop(messages: list):
    while True:
        # 1. 抽取后台任务通知
        notifs = BG.drain_notifications()
        if notifs:
            # 2. 注入到消息中
            notif_text = "\n".join(
                f"[bg:{n['task_id']}] {n['status']}: {n['result']}" for n in notifs
            )
            messages.append({
                "role": "user",
                "content": f"<background-results>\n{notif_text}\n</background-results>"
            })
        # 3. 继续调用 LLM
        response = client.messages.create(...)
```

#### 5. 对比 Golang Channel

| Golang | s08 BackgroundManager |
|--------|----------------------|
| `chan` | `_notification_queue` |
| `goroutine` | `threading.Thread` |
| `<-` 接收 | `drain_notifications()` |
| 无阻塞发送 | `run()` 立即返回 |

#### 6. 设计讨论

**问题 1：是否会忘记上下文？**
- 通知存储在内存队列中
- 如果 agent_loop 被重置，队列可能丢失
- 可优化：持久化到文件

**问题 2：线程池管控**
- 当前无限制创建线程
- 大量任务会耗尽资源
- 可优化：使用 ThreadPoolExecutor 限制并发

**最佳实践：结合 s07 任务追踪**
```
.tasks/                     # 任务持久化
├── task_1.json

.background_tasks/           # 后台任务持久化（新增）
├── bg_abc123.json         # {"command": "npm install", "status": "running"}
├── bg_abc123_completed.json  # {"status": "completed", "result": "..."}
```

**流程**：
1. background_run("npm install")
   → 记录到 .background_tasks/ (status: running)
2. 任务完成 → 更新状态 + 结果
3. agent_loop 重启 → 恢复上下文

**优势**：持久化 + 异步 + 可恢复

#### 7. 典型场景

| 场景 | 使用后台任务 |
|-----|-------------|
| npm install | ✅ 后台运行，不阻塞 |
| pytest | ✅ 后台运行，继续其他工作 |
| git push | ✅ 后台运行，等待通知 |
| cat file | ❌ 快速完成，不需要后台 |

#### 8. 面试问答

- Q: 前后台任务如何分离？
  - A: bash 是同步阻塞，background_run 是异步非阻塞。

- Q: 如何通知 Agent 任务已完成？
  - A: drain_notifications() 在每次 LLM 调用前抽取，注入到 messages。

- Q: 典型使用场景有哪些？
  - A: npm install、pytest、git push 等长时间任务。

- Q: 与 s07 Task System 的关系？
  - A: s08 可结合 s07，后台任务执行前后记录到文件，防止丢失上下文。

#### 9. 学习建议

- 理解异步通知机制
- 思考线程池管控
- 结合 s07 设计持久化方案

#### 学习建议
- 理解线程和通知队列的配合
- 思考典型场景：npm install、pytest、git push

---

### S09: Agent Teams 代理团队 ⭐ 新增

**文件**: `agents/s09_agent_teams.py` (~406 行)

> **核心理念**: "Teammates that can talk to each other."
>
> 可以相互通信的持久化代理

#### 1. 对比 s04 子代理

| 特性 | s04 Subagent | s09 Teammate |
|-----|-------------|--------------|
| 生命周期 | 临时 (spawn → execute → return → destroy) | 持久 (spawn → work → idle → work → shutdown) |
| 通信方式 | 返回摘要给父代理 | 通过 inbox 互发消息 |
| 状态 | 无状态 | 有状态 (working/idle) |
| 上下文 | 临时，本轮结束丢弃 | 持久，inbox 文件 |

#### 2. 架构流程

```
.team/
├── config.json                   .team/inbox/
├── {                           ├── alice.jsonl
│   "members": [              ├── bob.jsonl
│     {"name":"alice",       └── lead.jsonl
│      "role":"coder",
│      "status":"working"}
│   ]
│   }

spawn_teammate("alice", "coder", "fix bug")
         │
         ▼
Thread: alice          Thread: bob
┌─────────────┐      ┌─────────────┐
│ agent_loop │      │ agent_loop │
│ status:work│      │ status:idle│
└─────────────┘      └─────────────┘
```

#### 3. 核心类详解

##### MessageBus 类（第 77-117 行）

```python
class MessageBus:
    def send(self, sender, to, content, msg_type="message"):
        """发送消息到收件箱"""
        msg = {"type": msg_type, "from": sender, "content": content, "timestamp": time.time()}
        with open(f"{to}.jsonl", "a") as f:
            f.write(json.dumps(msg) + "\n")

    def read_inbox(self, name):
        """读取并清空收件箱"""
        messages = [json.loads(line) for line in inbox]
        inbox.write_text("")  # 读取后清空
        return messages
```

##### TeammateManager 类（第 123-248 行）

```python
def spawn(self, name, role, prompt):
    """生成持久化的队友"""
    thread = threading.Thread(target=self._teammate_loop, args=(name, role, prompt))
    thread.start()

def _teammate_loop(self, name, role, prompt):
    """队友的 agent_loop"""
    messages = [{"role": "user", "content": prompt}]
    for _ in range(50):
        inbox = BUS.read_inbox(name)  # 检查收件箱
        messages.extend(inbox)
        # 调用 LLM...
```

#### 4. 消息类型

| 类型 | 说明 |
|-----|------|
| `message` | 普通消息 |
| `broadcast` | 广播给所有队友 |
| `shutdown_request` | 关闭请求 (s10) |
| `shutdown_response` | 关闭响应 (s10) |
| `plan_approval_response` | 计划审批响应 (s10) |

#### 5. 设计讨论

**问题 1：多 agent 结果收集容易混乱**

多个 teammate 并行运行时，Lead 需要不断检查 inbox，结果顺序不确定。

**优化方案**：

1. **任务 ID 独立管理**
```
.team/inbox/
├── task_001/
│   ├── alice.jsonl
│   └── charlie.jsonl
├── task_002/
│   └── bob.jsonl
```

2. **冷热数据拆分**（借鉴 s06）
```
hot/
  task_001_recent.jsonl  # 最近 N 轮全量
cold/
  task_001_summary.json  # 早期仅摘要
```

**问题 2：职责错乱**

多个 agent 需要有明确分工，否则会出现职责混乱。

**解决方案**：
- System Prompt 明确定义角色职责
- 结合 s10 协议机制约束行为
- 多 agent 应该是**可选项**，按需开启

**设计理念**：多 agent 应该是可选项，不是默认开启
```
默认：agent_loop + 基础工具

可选加载：
- todo (s03)
- task_manager (s07)
- team (s09)
- skill (s05)
```

#### 6. 面试问答

- Q: MessageBus 如何实现多代理通信？
  - A: 通过 JSONL 文件作为收件箱，append-only 写入，read 清空。

- Q: 为什么选择 JSONL 格式存储消息？
  - A: 简单、易追加、适合多线程写入。

- Q: 收件箱读取后为什么要清空？
  - A: 避免重复处理，确保消息只被消费一次。

- Q: 点对点消息 vs 广播的区别？
  - A: 点对点发送到特定人，广播发送给所有人。

- Q: 多 agent 结果收集如何避免混乱？
  - A: 任务 ID 隔离、冷热数据拆分。

#### 7. 学习建议

- 理解 JSONL 格式的读写
- 对比单代理 vs 多代理的架构差异
- 思考多 agent 的优化策略

---

### S10: Team Protocols 团队协议 ⭐ 新增

**文件**: `agents/s10_team_protocols.py` (~487 行)

#### 核心类/函数
- `handle_shutdown_request(teammate: str)` - 处理关闭请求
- `handle_plan_review(request_id: str, approve: bool, feedback: str)` - 处理计划审批
- `_check_shutdown_status(request_id: str)` - 检查关闭状态
- 协议工具: `shutdown`, `idle`, `plan`, `approve`, `reject`

#### 关键实现逻辑

**Shutdown 协议 (FSM)**:
```
1. 队友 A 发送 shutdown_request
2. 队友 B 收到 → 检查是否有未完成任务
3. 有 → 拒绝，返回 shutdown_response(rejected)
4. 无 → 批准，返回 shutdown_response(approved)
5. A 收到响应 → 决定是否真正关闭
```

**Plan Approval 协议 (FSM)**:
```
1. 队友 A 提交计划: plan(subject, description)
2. 系统记录请求 → request_id
3. 队友 B 审查 → approve/reject(request_id, feedback)
4. A 收到响应 → 继续执行或重新规划
```

#### 设计模式
- **Finite State Machine**: 有限状态机
- **Request Correlation**: request_id 请求关联
- **Protocol Handshake**: 协议握手机制

#### 面试问答
- Q: shutdown 协议的 request_id 握手机制？
- Q: plan_approval 协议的完整流程？
- Q: 为什么要用 FSM 设计协议？
- Q: 协议如何保证团队协作的一致性？

#### 学习建议
- 理解 FSM 的状态转换
- 掌握 request_id 的追踪机制

---

### S11: Autonomous Agents 自主代理 ⭐ 新增

**文件**: `agents/s11_autonomous_agents.py` (~579 行)

#### 核心类/函数
- `scan_unclaimed_tasks()` - 扫描未认领任务
- `claim_task(task_id: int, owner: str)` - 认领任务
- `make_identity_block(name, role, team_name)` - 身份重注入
- `TeammateManager._loop()` - 带 IDLE 阶段的循环

#### 关键实现逻辑

**工作阶段**:
- 标准 agent 循环（调用 LLM → 执行工具）

**空闲阶段 (IDLE)**:
- 轮询收件箱（5 秒间隔）
- 扫描未认领任务
- 自动认领并恢复工作
- 60 秒超时后自动关闭

#### 自主决策流程
```
while True:
    if has_messages():
        处理消息
    elif has_unclaimed_tasks():
        claim_task()
        进入工作阶段
    else:
        进入空闲阶段 (IDLE)

    if idle_timeout:
        自动关闭
```

#### 设计模式
- **Autonomy Pattern**: 自动查找工作
- **Idle Polling**: 空闲轮询机制
- **Identity Re-injection**: 压缩后身份重注入

#### 面试问答
- Q: 自主代理 vs 受控代理的区别？
- Q: claim 机制如何工作？
- Q: 空闲阶段如何实现？
- Q: 为什么需要 60 秒超时？

#### 学习建议
- 理解 IDLE 轮询的实现
- 对比 s09/s10 的被动响应 vs s11 的主动扫描

---

### S12: Worktree Task Isolation 工作树隔离 ⭐ 新增

**文件**: `agents/s12_worktree_task_isolation.py` (~781 行)

#### 核心类/函数
- `EventBus` 类
  - `emit(event, task, worktree, error)` - 发射事件
  - `list_recent(limit)` - 列出最近事件
- `TaskManager` - 增强版任务管理器（带 worktree 绑定）
- `WorktreeManager` 类
  - `create(name, task_id, base_ref)` - 创建 worktree
  - `run(name, command)` - 在 worktree 中运行命令
  - `remove(name, force, complete_task)` - 移除 worktree
  - `keep(name)` - 保留 worktree
- 工作树工具: `spawn_tm`, `task_crt`, `task_upd`, `tm_run`, `tm_done`, `tm_rm`

#### 关键实现逻辑
- **Git Worktree**: 使用 `git worktree add` 创建隔离目录
- **任务绑定**: 每个任务关联一个 worktree
- **事件驱动**: EventBus 追踪任务生命周期

#### Worktree 操作流程
```
1. 创建任务 → task_crt(subject)
2. 创建隔离环境 → spawn_tm(task_id)
   → git worktree add .worktrees/{task_id} main
3. 在隔离环境工作 → tm_run(task_id, command)
4. 完成任务 → tm_done(task_id)
   → git worktree remove {task_id}
   → 更新任务状态为 completed
```

#### 设计模式
- **Directory Isolation**: 目录级隔离
- **Worktree Pattern**: Git Worktree 并行执行
- **Event Sourcing**: 事件溯源

#### 面试问答
- Q: Git worktree 如何实现隔离？
- Q: 任务完成后如何合并？
- Q: 为什么要用事件驱动设计？
- Q: 与 s07 Task System 的区别？

#### 学习建议
- 理解 Git worktree 命令
- 思考隔离环境的实际应用场景

---

### S_Full: 完整 Capstone 实现

**文件**: `agents/s_full.py` (~1000+ 行)

#### 已包含的所有机制
- ✅ TodoManager (s03)
- ✅ Subagent (s04)
- ✅ SkillLoader (s05)
- ✅ Compression (s06)
- ✅ TaskManager (s07)
- ✅ BackgroundManager (s08)
- ✅ MessageBus + TeammateManager (s09)
- ✅ Team Protocols (s10)
- ✅ Autonomous Agents (s11)

#### REPL 命令
- `/compact` - 手动触发压缩
- `/tasks` - 查看任务列表
- `/team` - 查看团队状态
- `/inbox` - 查看收件箱

#### 学习建议
- 在学完所有 s01-s11 后再学习
- 理解各机制如何协同工作

---

## 学习进度追踪

### 阶段一：基础回顾（s01-s02）

- [x] s01_agent_loop.py - 基础代理循环
- [x] s02_tool_use.py - 工具使用

### 阶段二：单代理增强（s03-s06）

- [x] s03_todo_write.py - 待办事项系统
- [x] s04_subagent.py - 子代理模式
- [x] s05_skill_loading.py - 动态技能加载
- [x] s06_context_compact.py - 上下文压缩

### 阶段三：任务管理（s07-s08）

- [x] s07_task_system.py - 持久化任务系统
- [x] s08_background_tasks.py - 后台任务

### 阶段四：多代理协作（s09-s12）

- [x] s09_agent_teams.py - 代理团队
- [x] s10_team_protocols.py - 团队协议 (含 Bug 修复)
- [x] s11_autonomous_agents.py - 自主代理 (含设计缺陷分析)
- [x] s12_worktree_task_isolation.py - 工作树隔离

### 阶段五：完整集成

- [x] s_full.py - 完整 capstone 实现

### 附加资源

- [ ] Web 平台交互式学习 (web/)
- [ ] 技能定义 (skills/)
- [ ] 多语言文档 (docs/)

---

## 关键技术差异总结

| 特性 | minicode | learn-claude-code |
|------|----------|-------------------|
| API 调用 | urllib（TODO 换 SDK） | 官方 anthropic-python SDK |
| 上下文压缩 | TODO 注释 | 完整三层实现 |
| 待办事项 | 无 | TodoManager |
| 子代理 | 无 | 完整子代理模式 |
| 技能系统 | 无 | SkillLoader |
| 任务持久化 | 无 | TaskManager + .tasks/ |
| 后台任务 | 无 | BackgroundManager |
| 多代理 | 无 | MessageBus + 协议 |
| 工作树隔离 | 无 | Git worktree |

---

## 12 个核心设计模式总结

| 模式 | 会话 | 描述 |
|------|------|------|
| Agent Loop | s01 | 基础循环架构 |
| Tool Dispatch | s02 | 工具调度映射 |
| State Management | s03 | 代理内部状态 |
| Subagent | s04 | 子代理隔离 |
| Lazy Loading | s05 | 技能按需加载 |
| Context Compression | s06 | 策略性压缩 |
| Task Board | s07 | 外部任务持久化 |
| Background Tasks | s08 | 异步并行执行 |
| Team Messaging | s09 | 团队通信总线 |
| Protocols | s10 | 团队协议 FSM |
| Autonomy | s11 | 自主任务发现 |
| Worktree Isolation | s12 | 目录级任务隔离 |

---

## 推荐学习路径

```
Step 1: 对比 minicode.py 与 s01_agent_loop.py
        ↓
Step 2: 学习 s01-s02（基础）
        ↓
Step 3: 学习 s03-s06（单代理增强）
        - 重点：s06 上下文压缩是 minicode 的 TODO 项
        ↓
Step 4: 学习 s07-s08（任务管理）
        - 重点：理解持久化 vs 内存的区别
        ↓
Step 5: 学习 s09-s12（多代理协作）
        - 重点：这是 minicode 完全未涉及的领域
        ↓
Step 6: 深入 s_full.py
        - 理解所有机制如何组合
        ↓
Step 7: 启动 Web 平台交互式学习
        cd web && npm run dev
```

---

### 2026-03-08: 上下文管理方案对比研究 (LangGraph vs OpenViking)

## 研究背景

在完成 learn-claude-code 项目学习后，对比研究了业界两种主流的上下文管理方案：LangGraph 和 OpenViking。

## 三者架构对比

| 特性 | learn-claude-code | LangGraph | OpenViking |
|------|------------------|-----------|------------|
| **定位** | 教学 (0→1) | 编排框架 | Context Database |
| **架构模式** | 纯 Python 代码 | 图编排框架 | 独立服务 |
| **短期记忆** | `messages[]` + 三层压缩 | Checkpointer (snapshot) | L0/L1 抽象层 |
| **长期记忆** | 文件系统 (`.tasks/`, `.team/`) | Store (语义搜索) | 文件系统 + 向量索引 |
| **存储后端** | JSONL 文件 | PostgreSQL/Redis/Cassandra | 自研 (LanceDB 向量) |
| **检索方式** | 无 | 纯语义搜索 | 目录递归检索 (定位+精修) |
| **索引漂移问题** | 无索引 | 有漂移风险 | **解决**: 目录优先定位 |
| **可观测性** | 低 | 中 | 高 (检索轨迹可视化) |
| **依赖复杂度** | 无 (轻量) | 中等 | 重 (Go + C++ + Python) |

---

## learn-claude-code 实现方案

### 核心机制 (s06 上下文压缩)

```
三层压缩策略:
Layer 1: micro_compact (每轮执行)
  - 保留最近 3 个 tool_result
  - 旧的替换为 "[Previous: used X]"

Layer 2: auto_compact (token > 50000)
  - 保存完整记录到 .transcripts/
  - LLM 总结，替换所有消息

Layer 3: manual compact (手动触发)
  - 通过 compact 工具触发
```

### 长期记忆方案

| 机制 | 存储位置 | 用途 |
|------|---------|------|
| 任务系统 | `.tasks/` | 任务持久化 + 依赖图 |
| 代理团队 | `.team/` | 消息通信 |
| 工作树 | `.worktrees/` | 目录隔离 |
| 转录文件 | `.transcripts/` | 压缩前备份 |

### 优点
- 零依赖，轻量实现
- 机制清晰，适合教学
- 所有数据可读 JSONL
- 完全可控，无黑盒

### 缺点
- 无语义搜索能力
- 无标准化 API
- 检索依赖 LLM 理解

---

## LangGraph 方案

### 核心组件

**1. Checkpointer (短期记忆)**
- 作用：保存图状态快照，支持 `thread_id` 恢复
- 后端：`InMemorySaver`, `PostgresSaver`, `RedisSaver`, `CassSaver`
- 操作：`graph.get_state(config)`, `graph.get_state(config, checkpoint_id)`

**2. Store (长期记忆)**
- 作用：跨会话持久化，支持语义搜索
- 命名空间：`namespace = (user_id, "memories")`
- 操作：
  - `store.put(namespace, key, value)` - 存储
  - `store.search(namespace, query, limit)` - 语义搜索

**3. 消息压缩 (langmem)**
```python
from langmem.short_term import SummarizationNode

summarization_node = SummarizationNode(
    token_counter=count_tokens_approximately,
    model=summarization_model,
    max_tokens=256,
    max_tokens_before_summary=256,
    max_summary_tokens=128,
)
```

### 优点
- 标准化 API，多后端支持
- 生态成熟 (LangChain 生态)
- 状态可恢复 (thread_id)
- 支持语义搜索

### 缺点
- 向量检索存在索引漂移问题
- 分层加载需要自己实现
- 无文件系统范式
- 架构相对复杂

### 适合场景
- 需要复杂图编排的工作流
- 多轮对话状态恢复
- 已有 LangChain 生态依赖
- 需要多后端持久化

---

## OpenViking 方案

### 核心概念 (五大机制)

**1. 文件系统范式 → 解决碎片化**
```
viking://
├── resources/     # 资源: 项目文档、代码库
├── user/          # 用户: 偏好、习惯
└── agent/         # 代理: 技能、指令、任务记忆
```

**2. 分层上下文加载 (L0/L1/L2) → 减少 Token**
```
viking://resources/my_project/
├── .abstract    # L0: 一句话摘要 (~100 tokens)
├── .overview    # L1: 核心信息 (~2k tokens)
└── docs/
    ├── .abstract
    ├── .overview
    └── auth.md  # L2: 完整内容 (按需加载)
```

**3. 目录递归检索 → 改善检索效果**
```
意图分析 → 初始定位(向量) → 精修探索 → 递归钻取 → 结果聚合
```

**4. 可观测检索轨迹 → 解决黑盒问题**
- 每个操作都有 URI 对应
- 检索路径完全保留

**5. 自动会话管理 → 上下文自迭代**
- 会话结束自动提取长期记忆
- 用户偏好自动更新

### 实验数据 (OpenClaw 测试)

| 实验组 | 任务完成率 | Input Tokens |
|--------|-----------|--------------|
| OpenClaw (memory-core) | 35.65% | 24,611,530 |
| OpenClaw + LanceDB | 44.55% | 51,574,530 |
| OpenClaw + OpenViking | 52.08% | 4,264,396 |

**结论**:
- vs OpenClaw: +43% 完成任务率, -91% token
- vs LanceDB: +15% 完成任务率, -96% token

### 优点
- **解决索引漂移**: 目录优先定位，再精修内容
- **分层加载**: L0/L1/L2 按需加载，显著节省 token
- **可观测**: 检索轨迹完全透明
- **自动迭代**: 会话结束自动提取长期记忆
- 实验数据验证效果好

### 缺点
- 依赖重 (Go + C++ 编译)
- 架构重，不适合轻量场景
- 2026-01 新发布，生态待验证
- 主要解决 RAG 场景，非纯 Agent

### 适合场景
- 大型代码库检索
- 需要精确上下文定位
- 长对话 + 上下文复用
- 企业级多 Agent 协作

---

## 选型建议

| 场景 | 推荐方案 |
|------|---------|
| 学习/教学 | learn-claude-code |
| 轻量 Agent | learn-claude-code + 简单扩展 |
| LangChain 生态 | LangGraph |
| 复杂图编排 | LangGraph |
| 大型代码库 | OpenViking |
| 需要精确检索 | OpenViking |
| 上下文自迭代 | OpenViking |

## 总结

| 维度 | learn-claude-code | LangGraph | OpenViking |
|------|------------------|-----------|------------|
| **记忆方式** | 消息压缩 | 状态快照 + Store | 分层抽象文件 |
| **检索** | 无 | 纯语义 | 目录+语义混合 |
| **迭代** | 手动 | 手动 | **自动** |
| **复杂度** | 低 | 中 | 高 |

**核心洞察**:
1. **索引漂移**是 RAG 痛点，OpenViking 的目录优先策略值得借鉴
2. **分层抽象**是省 Token 的关键，L0/L1/L2 机制清晰
3. **文件系统范式**统一了 memory/resources/skills，值得参考
4. learn-claude-code 作为教学项目，核心机制与工业方案一致，只是实现简化

---

## 参考链接

- [LangGraph Persistence](https://python.langchain.com/docs/langgraph/persistence/)
- [LangGraph Memory](https://docs.langchain.com/oss/python/langgraph/memory)
- [OpenViking GitHub](https://github.com/volcengine/OpenViking)
- [OpenViking 文档](https://www.openviking.ai/docs)

---

## 学习记录

### 2026-03-06: S03-S08 深入学习

**S03 核心理解**:
- TodoManager 引入内部状态管理
- Nag Reminder 机制：连续 3 轮未调用 todo → 注入 `<reminder>` 提醒
- 软约束 vs 硬约束：reminder 是软约束，in_progress 只能是 1 个是硬约束
- 强制规则的意义：LLM 本质无状态，需要状态机防止"混沌"
- 约束层次：软约束 → 硬约束 → 外部持久化

**S04 核心理解**:
- run_subagent() 创建独立上下文 (messages=[])
- 工具子集：子代理没有 task 工具，防止递归
- 串行执行：子代理一次只运行一个，不需要限制数量
- task 工具的特殊性：不是简单 TOOL_HANDLERS，需要独立循环
- MCP 工具整合：工具发现 → 格式转换 → 合并到工具列表
- 工具选择优化：描述区分、多级路由、动态注入、Few-shot 示例
- 选错工具兜底：Schema 校验、错误处理、LLM 重试、强制重置

**S05 核心理解**:
- Skill 提供"知识/指导"，Tool 提供"执行能力"
- 两层注入：Layer 1 告诉有哪些技能，Layer 2 按需加载完整内容
- Skill 两种写法："写代码型"(不需要预定义工具) vs "调用工具型"(需要预定义)
- 本地部署：Skill 可以写完整代码让 LLM 执行
- 云端部署：用 MCP 预定义工具，Skill 只写调用序列+判断规则
- OnCall Agent 场景：Skill + RPC 调用 + LLM 判断
- 安全考虑：Prompt 注入、Skill 注入的防护方案

**S06 核心理解**:
- 三层压缩策略：Layer 1 微压缩、Layer 2 自动压缩、Layer 3 手动压缩
- micro_compact：每轮保留最近 3 个 tool_result，旧替换为占位符
- auto_compact：token > 50000 时触发，保存完整记录到 .transcripts/，LLM 总结
- compact 工具参数问题：定义了 focus 参数但未使用，会误导 LLM
- 手动压缩优化：检测用户压缩指令后直接压缩，跳过 LLM 判断

**S07 核心理解**:
- TaskManager 文件持久化，任务不受上下文压缩影响
- 依赖图管理：blockedBy + blocks，双向关联
- LLM 自主决策：根据 System Prompt 和可用工具决定调用
- 压缩后恢复：LLM 调用 task_get/task_list 重新加载任务信息
- 任务状态流转：创建任务 → 更新状态(in_progress) → 完成任务(completed) → 解除依赖(自动清理 blockedBy)
- 设计讨论：任务管理更适合作为 Skill（可选加载），而非内置

**S08 核心理解**:
- 后台任务：Fire and Forget，触发即返回
- 异步通知：类比 Golang Channel，任务完成推送到队列
- drain_notifications：在每次 LLM 调用前抽取，注入到 messages
- 设计问题：内存队列可能丢失上下文、无限创建线程
- 最佳实践：结合 s07，后台任务执行前后记录到文件，避免进程重启丢失

**S09 核心理解**:
- 多 agent 通信：MessageBus + JSONL 收件箱
- 持久化：Teammate 独立上下文，不会丢失
- 主从结构：Lead 派发任务，Teammate 执行
- 设计问题：多任务结果收集容易混乱
- 优化方案：任务 ID 隔离、冷热数据拆分（借鉴 s06）
- 设计理念：多 agent 应该是可选项，按需开启

**S10 核心理解**:
- 团队协议：Shutdown Protocol + Plan Approval Protocol
- Request ID 关联模式：FSM 状态机 (pending -> approved/rejected)
- Plan Approval 不是 Plan-Execute：
  - Plan-Execute：LLM 自己决定规划+执行，不需要外部批准
  - Plan Approval：主动提交计划，需要外部审批后才能执行
  - 适用场景：企业审批流程、风险控制、资源/成本控制、多方对齐
- Human-in-the-Loop 模式对比：
  - 直接模式：用户全程参与，每一步都等待确认
  - 协议模式：只在关键节点升级，大部分流程自动化
  - 当前实现是 Agent-to-Agent，需要扩展才能支持真正的人类介入
- 真正人类介入实现方案：
  - 轮询模式：每隔一段时间检查状态
  - 回调/Future 模式：阻塞等待外部调用 set_result
  - WebSocket 推送模式：实时通知
  - 都需要配合 checkpoint 保存状态，避免进程崩溃丢失
- Checkpoint 机制：
  - 作用：保存 Agent 状态到磁盘，防止等待期间进程崩溃
  - LangChain 实现：interrupt() + checkpoint + resume
- Bug 发现与修复：
  - 问题：plan_approval 提交后，Teammate 立即进入下一轮 LLM 调用
  - 原因：原代码只是返回 "Waiting for lead approval"，没有阻塞
  - 后果：Lead 还没审批，Teammate 可能已经开始执行未经批准的计划
  - 修复：在 plan_approval 工具执行后，强制轮询等待批准状态，最多 5 分钟

**S11 核心理解**:
- 自主代理 (Autonomous Agents)：Teammate 自己找活干，不再等 Lead 派发
- 生命周期：WORK -> IDLE -> 轮询(检查 inbox/任务) -> 继续 WORK 或 shutdown
- 新增工具：idle (主动进入空闲), claim_task (认领任务), scan_unclaimed_tasks()
- Identity Re-injection：上下文压缩后重新注入身份块，防止忘记自己是谁
- 发现的问题：
  - 独立 inbox 不共享（各 agent 独立消息文件）
  - 任务重复认领（小概率竞态，已有 _claim_lock 保护）
  - 上下文污染：所有消息混在一起，没有分类
  - **严重设计缺陷**：任务切换后上下文丢失
    - Alice 做 Task #1 -> idle -> Bob 认领 Task #1 -> Bob 不知道 Alice 做了什么
    - 任务的执行上下文没有持久化
  - claim_task 全局锁性能问题：所有 agent 竞争同一把锁
  - make_identity_block 冗余问题：system prompt 已包含身份，messages 中的 identity block 其实是冗余的
- 优化方案（借鉴 Redis AOF + RDB）：
  - AOF: 增量保存每轮执行记录 (round_*.json)
  - RDB: 压缩快照 (task_*_context.json)
  - 崩溃恢复：加载 RDB + 重放 AOF
- 结合 Agent Team + Task Track：
  - Lead 拆分任务 -> Teammate 执行 -> 各自维护独立上下文
  - 任务持久化 (.tasks/) + 上下文持久化 (AOF+RDB)
- 设计理念：工具能力可选，用户自己组合使用

**S12 核心理解**:
- Worktree 隔离：使用 Git Worktree 实现目录级隔离
- 架构：
  - .tasks/ 任务元数据 (可绑定 worktree)
  - .worktrees/ 工作树目录 (独立目录 + 独立分支)
- 核心价值：不同 worktree 独立目录，避免文件冲突
- 限制：
  - Git 历史共享（git log 能看到所有分支提交）
  - 资源不隔离（同一机器，CPU/内存共享）
  - 单机多 Agent 场景价值有限（s11 也能满足）
- 更适合：多个人同时开发、CI 并行测试

**拓展设计 - 会话级上下文隔离**:
- s12 目录级隔离的思路可扩展到会话级别
- 场景：OnCall Agent 服务多个用户，每个用户是独立会话
- 实现方案 (MySQL + Redis):
  - Redis 短期记忆：当前对话上下文，AOF+RDB 持久化
  - MySQL 长期记忆：历史会话、用户偏好、知识库
  - Session ID 隔离：每个用户/会话独立存储
- 设计原则：不同会话强制隔离，避免上下文污染

**下一步**: s_full 完整实现

**S_full 核心理解**:
- 完整 Capstone 实现：组合 s01-s11 所有机制
- 架构：
  - System prompt (s05 skills + task-first + todo nag)
  - Before each LLM call: microcompact → auto_compact → drain_bg → check_inbox
  - Tool dispatch: 20+ tools 统一管理
- Pipeline 执行顺序：
  1. microcompact (s06) - 微压缩
  2. auto_compact (s06) - 自动压缩（> 100k tokens）
  3. BG.drain() (s08) - 抽取后台通知
  4. BUS.read_inbox() (s09) - 检查收件箱
  5. LLM call
  6. Nag reminder (s03) - 检查是否需要提醒更新 todo
  7. manual compress - 手动压缩
- 组合的机制：
  - s01: agent_loop
  - s02: TOOL_HANDLERS 工具分发
  - s03: TodoManager + Nag Reminder
  - s04: run_subagent
  - s05: SkillLoader
  - s06: microcompact + auto_compact
  - s07: TaskManager 文件持久化
  - s08: BackgroundManager 后台任务
  - s09: MessageBus 消息总线
  - s10: shutdown/plan_approval 协议
  - s11: TeammateManager idle/claim
- REPL 命令：/compact, /tasks, /team, /inbox
- Bug 修复：输出流缺失（已修复打印 LLM 回答）
- 简化说明：
  - Teammate 比 s10/s11 简化（没有 plan_approval/shutdown_response 工具）
  - 继承的潜在问题：plan_approval 在 s10 发现的 bug 依然存在

**学习完成**:
- ✅ s01-s12 全部完成
- ✅ s_full 完整实现

---

### 2026-03-04: S01-S02 基础学习

**S01 核心理解**:
- Agent Loop 模式：while True → LLM → 工具执行 → 反馈结果
- stop_reason 枚举：`tool_use`(继续), `end_turn`(完成), `max_tokens`, `stop_sequence`
- 只有 `tool_use` 才继续循环，其他直接返回

**S02 核心理解**:
- 4 个工具：bash, read_file, write_file, edit_file
- Dispatch Map 模式：TOOL_HANDLERS 字典映射工具名到处理函数
- safe_path 防止目录穿越攻击
- 专用工具 vs bash 的权衡：
  - Token 效率更高
  - 语义更明确
  - 安全控制更细粒度
  - 输出格式更可控

**下一步**: 进入阶段二，学习 s03-s06 单代理增强内容

---

## 待处理

- [x] 开始 s01-s02 基础学习
- [x] 深入理解 s03-s09 机制
- [ ] 运行代码验证实现
- [ ] 对比 Web 平台的可视化内容
- [ ] 整理面试问答要点