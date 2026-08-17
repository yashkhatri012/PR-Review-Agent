from services.mcp_client import MCPClient

class RepositoryContext:
    """Its job is to provide agents with a convenient, shared way to obtain repository information while handling things like caching."""

    def __init__(self, mcp_client: MCPClient) -> None:
        """Initialize repository context.

        Args:
            mcp_client: Connected MCP client used for repository access.
        """
        self.mcp_client = mcp_client
        self._file_cache: dict[str, str] = {}

    async def get_file(self, file_path: str) -> str:
        """Return a repository file, using the cache when available.

        Args:
            file_path: Path to the repository file.

        Returns:
            Contents of the requested file.

        Raises:
            Exception: If the MCP server fails to read the file.
        """
        if file_path in self._file_cache:
            return self._file_cache[file_path]

        result = await self.mcp_client.call_tool(
            "read_file",
            {"file_path": file_path},
        )

        content = result.structuredContent["result"]

        self._file_cache[file_path] = content

        return content