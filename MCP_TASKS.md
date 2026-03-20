# MCP 集成任务列表

## 任务列表

| # | 状态 | 任务 | 描述 |
|---|------|------|------|
| 1 | [x] | 创建 mcp_servers.json 配置文件示例 | 在项目目录创建 mcp_servers.json 配置文件示例，包含 stdio 和 sse 两种传输方式的配置格式 |
| 2 | [x] | 实现 MCPManager 核心类 | 实现 MCPManager 类，包含：加载配置文件、stdio 传输支持、sse 传输支持、工具列表获取、工具调用功能 |
| 3 | [x] | 实现 MCP Tool 到 Agent Tool 格式转换 | 实现 MCP Tool 到 Agent Tool 的格式转换，添加服务器名称作为前缀（namespace） |
| 4 | [x] | 集成 MCP 到 minicode_full.py | 在 minicode_full.py 中集成 MCP：启动时初始化 MCP 服务器、合并工具到 TOOLS 列表、添加工具调用处理器 |
| 5 | [x] | 测试 MCP 集成功能 | 使用 weather MCP 服务器测试集成是否正常工作，验证工具调用和响应 |

## 问题排查记录

### MCP SDK stdio_client 挂起问题

**问题描述**：使用 `mcp.client.stdio.stdio_client` 连接 MCP 服务器时会挂起，无法完成初始化。

**错误导入方式**（导致挂起）：
```python
from mcp.client.stdio import StdioServerParameters, stdio_client
from mcp.client.session import ClientSession
```

**正确导入方式**（官方示例）：
```python
from mcp import ClientSession, StdioServerParameters  # 注意：ClientSession 从 mcp 直接导入
from mcp.client.stdio import stdio_client
```

**另一个关键点**：必须使用上下文管理器
```python
# 错误
session = ClientSession(read, write)
await session.initialize()

# 正确
async with ClientSession(read, write) as session:
    await session.initialize()
```

**实现策略**：使用临时连接模式（每次操作创建新连接），避免后台长连接线程问题。

## 技术方案（已验证）

### 工具命名策略

### 配置文件格式 (mcp_servers.json)

```json
{
  "mcpServers": {
    "weather": {
      "command": "uv",
      "args": ["--directory", "/Users/vagrant/dev/code/python/mcp-weather", "run", "weather.py"],
      "transport": "stdio"
    },
    "remote-api": {
      "url": "http://localhost:8080/mcp",
      "transport": "sse"
    }
  }
}
```

### 工具命名策略

```
{mcp_server_name}_{tool_name}

例如：
- weather.get_weather → weather_get_weather
- fetch.fetch_url → fetch_fetch_url
```

### 传输协议支持

| 传输方式 | 配置字段 | 适用场景 |
|----------|----------|----------|
| stdio | command + args | 本地命令/脚本 |
| sse | url | 远程 MCP 服务器 |
