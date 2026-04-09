import sys
import asyncio
from contextlib import AsyncExitStack
from mcp import StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.session import ClientSession
from langchain_mcp_adapters.tools import load_mcp_tools


class DeLabsMCPGateway():
    """
    Manages the connections to our isolated micro-MCP Servers.
    """
    def __init__(self):
        self.server_configs = {
            "literature" : StdioServerParameters(
                command = sys.executable,
                args = ["MCPServers/literature/server.py"]
            ),
            "workspace" : StdioServerParameters(
                command = sys.executable,
                args = ["MCPServers/workspace/server.py"]
            ),
            "sysadmin" : StdioServerParameters(
                command = sys.executable,
                args = ["MCPServers/sysadmin/server.py"]
            )
        }

        self.loaded_tools = {
            "literature" : [],
            "workspace" : [],
            "sysadmin" : []
        }
        self.sessions = {}
        # This keeps the background processes alive until we explicitly close them
        self.stack = AsyncExitStack()

    async def initialize(self):
        """Boots up the servers, keeps them open, and extracts their tools."""
        print("🔌 [Gateway] Booting up MCP Microservices...")
        
        for server_name, config in self.server_configs.items():
            try:
                # 1. Open the Stdio transport pipe
                transport = await self.stack.enter_async_context(stdio_client(config))
                read, write = transport[0], transport[1]

                # 2. Open the Client Session over the pipe
                session = await self.stack.enter_async_context(ClientSession(read, write))
                
                # 3. Initialize the handshake with the FastMCP server
                await session.initialize()
                self.sessions[server_name] = session

                # 4. Load the tools dynamically into LangChain format
                tools = await load_mcp_tools(session)
                self.loaded_tools[server_name] = tools
                
                print(f"   ✅ {server_name.capitalize()} Server connected. ({len(tools)} tools loaded)")
            except Exception as e:
                print(f"   ❌ Failed to connect to {server_name}: {e}")

    async def cleanup(self):
        """Gracefully shuts down all background MCP servers."""
        print("\n🔌 [Gateway] Shutting down MCP Microservices...")
        await self.stack.aclose()

    def get_tools(self, server_name: str):
        """Returns the LangChain tools for a specific server."""
        return self.loaded_tools.get(server_name, [])

# Singleton instance
mcp_gateway = DeLabsMCPGateway()