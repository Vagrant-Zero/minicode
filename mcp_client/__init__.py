#!/usr/bin/env python3
"""
MCP Client Package - MCP 服务器客户端封装
"""

from mcp_client.manager import MCPManager, get_mcp_manager, init_mcp

__all__ = ["MCPManager", "get_mcp_manager", "init_mcp"]
