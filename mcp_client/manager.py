#!/usr/bin/env python3
"""
MCP Manager - 管理 MCP 服务器连接和工具调用

支持两种传输协议：
- stdio: 子进程标准输入输出（默认）
- sse: HTTP Server-Sent Events
"""

import asyncio
import json
import os
import threading
from pathlib import Path
from typing import Any


def _get_clean_env(base_env: dict | None = None) -> dict:
    """获取干净的环境变量，移除 VIRTUAL_ENV 避免 uv warning"""
    if base_env is None:
        base_env = os.environ.copy()

    # 移除 VIRTUAL_ENV 相关变量，避免 uv warning
    clean_env = {k: v for k, v in base_env.items()
                 if k not in ('VIRTUAL_ENV', 'PYTHONHOME')}

    # 设置 HOME 如果不存在
    if 'HOME' not in clean_env:
        clean_env['HOME'] = os.path.expanduser('~')

    return clean_env


class MCPClient:
    """单个 MCP 服务器的客户端封装 - 每次调用创建新连接"""

    def __init__(self, name: str, config: dict):
        self.name = name
        self.config = config
        self._lock = threading.Lock()

    def connect(self) -> bool:
        """测试连接，返回是否可用"""
        transport = self.config.get("transport", "stdio")

        if transport == "stdio":
            return self._test_stdio_connection()
        elif transport == "sse":
            return self._test_sse_connection()
        else:
            print(f"[MCP] Unknown transport '{transport}' for {self.name}")
            return False

    def _test_stdio_connection(self) -> bool:
        """测试 stdio 连接"""
        command = self.config.get("command")
        args = self.config.get("args", [])
        env = self.config.get("env")

        if not command:
            return False

        async def test():
            from mcp import ClientSession, StdioServerParameters
            from mcp.client.stdio import stdio_client

            env_to_use = _get_clean_env(env)
            server_params = StdioServerParameters(
                command=command,
                args=args,
                env=env_to_use,
            )
            try:
                async with stdio_client(server_params) as (read, write):
                    async with ClientSession(read, write) as session:
                        await session.initialize()
                        return True
            except Exception as e:
                print(f"[MCP] Connection test failed for {self.name}: {e}")
                return False

        return asyncio.run(test())

    def _test_sse_connection(self) -> bool:
        """测试 SSE 连接"""
        print(f"[MCP] SSE not implemented for {self.name}")
        return False

    def close(self):
        """关闭连接（对于临时连接模式不需要）"""
        pass

    def list_tools(self) -> list[dict]:
        """获取可用工具列表"""
        result = self._execute_with_session(
            lambda session: session.list_tools()
        )
        # 提取 tools 列表
        if hasattr(result, 'tools'):
            return result.tools
        return []

    def call_tool(self, tool_name: str, arguments: dict) -> str:
        """调用工具"""
        return self._execute_with_session(
            lambda session: session.call_tool(tool_name, arguments),
            format_result=True
        )

    def _execute_with_session(self, func, format_result=False):
        """使用临时连接执行操作"""
        command = self.config.get("command")
        args = self.config.get("args", [])
        env = self.config.get("env")

        if not command:
            return f"Error: No command for {self.name}"

        async def execute():
            from mcp import ClientSession, StdioServerParameters
            from mcp.client.stdio import stdio_client

            env_to_use = _get_clean_env(env)
            server_params = StdioServerParameters(
                command=command,
                args=args,
                env=env_to_use,
            )
            try:
                async with stdio_client(server_params) as (read, write):
                    async with ClientSession(read, write) as session:
                        await session.initialize()
                        result = await func(session)

                        if format_result and hasattr(result, 'content') and result.content:
                            parts = []
                            for item in result.content:
                                if hasattr(item, 'text'):
                                    parts.append(item.text)
                                else:
                                    parts.append(str(item))
                            return "\n".join(parts)
                        return result
            except Exception as e:
                return f"Error: {e}"

        return asyncio.run(execute())


class MCPManager:
    """MCP 服务器管理器"""

    def __init__(self, config_path: str | Path | None = None):
        self.clients: dict[str, MCPClient] = {}
        self._config_path = config_path or Path.cwd() / "mcp_servers.json"

    def load_config(self) -> dict:
        """加载配置文件"""
        if not self._config_path.exists():
            print(f"[MCP] Config file not found: {self._config_path}")
            return {}

        try:
            with open(self._config_path) as f:
                config = json.load(f)
                return config.get("mcpServers", {})
        except Exception as e:
            print(f"[MCP] Failed to load config: {e}")
            return {}

    def connect_all(self) -> None:
        """连接所有 MCP 服务器"""
        servers = self.load_config()

        if not servers:
            print("[MCP] No MCP servers configured")
            return

        print(f"[MCP] Connecting to {len(servers)} server(s)...")

        for name, config in servers.items():
            # 检查是否禁用
            if config.get("disabled", False):
                print(f"[MCP] {name} is disabled, skipping")
                continue

            print(f"[MCP] Testing connection to {name}...")
            client = MCPClient(name, config)
            if client.connect():
                self.clients[name] = client
                print(f"[MCP] Connected to {name}")
            else:
                print(f"[MCP] Failed to connect to {name}, skipping")

    def list_all_tools(self) -> list[dict]:
        """获取所有 MCP 服务器的工具列表"""
        all_tools = []

        for name, client in self.clients.items():
            try:
                tools = client.list_tools()
                for tool in tools:
                    # 添加服务器名称作为前缀
                    input_schema = tool.inputSchema
                    if hasattr(input_schema, 'model_dump'):
                        input_schema = input_schema.model_dump()
                    elif hasattr(input_schema, 'dict'):
                        input_schema = input_schema.dict()

                    prefixed_tool = {
                        "name": f"{name}_{tool.name}",
                        "description": f"[MCP: {name}] {tool.description or ''}",
                        "input_schema": input_schema,
                        "_server": name,
                        "_original_name": tool.name,
                    }
                    all_tools.append(prefixed_tool)
            except Exception as e:
                print(f"[MCP] Error getting tools from {name}: {e}")

        return all_tools

    def call_tool(self, prefixed_name: str, arguments: dict) -> str:
        """调用 MCP 工具（使用带前缀的工具名）"""
        # 解析前缀找到服务器和原始工具名
        for name, client in self.clients.items():
            if prefixed_name.startswith(f"{name}_"):
                original_name = prefixed_name[len(name) + 1:]
                return client.call_tool(original_name, arguments)

        return f"Error: Unknown MCP tool '{prefixed_name}'"

    def close_all(self) -> None:
        """关闭所有连接"""
        for client in self.clients.values():
            client.close()
        self.clients.clear()


# 全局实例
_mcp_manager: MCPManager | None = None


def get_mcp_manager() -> MCPManager:
    """获取全局 MCP 管理器实例"""
    global _mcp_manager
    if _mcp_manager is None:
        _mcp_manager = MCPManager()
    return _mcp_manager


def init_mcp() -> None:
    """初始化 MCP 连接"""
    manager = get_mcp_manager()
    manager.connect_all()
