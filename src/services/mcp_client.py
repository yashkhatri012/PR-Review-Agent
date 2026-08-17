from contextlib import AsyncExitStack

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


class MCPClient:
    """Client side operations for communication with an MCP server."""

    def __init__(self, server_url: str) -> None:
        """Initialize the MCP client.

        Args:
            server_url: URL of the MCP server.
        """
        self.server_url = server_url
        self._exit_stack = AsyncExitStack()
        self._session: ClientSession | None = None

    async def connect(self) -> None:
        """Connect to the MCP server and initialize a session.

        Raises:
            RuntimeError: If the client is already connected.
        """
        if self._session is not None:
            raise RuntimeError("MCP client is already connected.")

        read_stream, write_stream, _ = await self._exit_stack.enter_async_context(
            streamable_http_client(self.server_url)
        )

        self._session = await self._exit_stack.enter_async_context(
            ClientSession(read_stream, write_stream)
        )

        await self._session.initialize()

    async def list_tools(self):
        """List the tools exposed by the MCP server.

        Returns:
            A list of tools available from the MCP server.

        Raises:
            RuntimeError: If the client is not connected.
        """
        session = self._get_session()

        result = await session.list_tools()

        return result.tools

    async def call_tool(self, name: str, arguments: dict):
        """Call a tool exposed by the MCP server.

        Args:
            name: Name of the MCP tool to invoke.
            arguments: Arguments required by the tool.

        Returns:
            The result returned by the MCP server.

        Raises:
            RuntimeError: If the client is not connected.
        """
        session = self._get_session()

        return await session.call_tool(
            name,
            arguments,
        )

    async def close(self) -> None:
        """Close the MCP session and underlying HTTP connection."""
        await self._exit_stack.aclose()
        self._session = None

    def _get_session(self) -> ClientSession:
        """Return the active MCP session.

        Returns:
            The currently connected MCP session.

        Raises:
            RuntimeError: If the client is not connected.
        """
        if self._session is None:
            raise RuntimeError("MCP client is not connected.")

        return self._session