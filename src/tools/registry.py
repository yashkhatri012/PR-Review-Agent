from collections.abc import Callable


class ToolRegistry:
    """Register and execute tools requested by an LLM."""

    def __init__(self) -> None:
        """Initialize an empty tool registry."""
        self._tools: dict[str, Callable] = {}

    def register(self, name: str, function: Callable) -> None:
        """Register a callable under a tool name.

        Args:
            name: Name by which the LLM identifies the tool.
            function: Python callable that implements the tool.
        """
        self._tools[name] = function

    def execute(self, name: str, arguments: dict) -> object:
        """Execute a registered tool with the provided arguments."""
        
        function = self._tools.get(name)

        if function is None:
            raise ValueError(f"Unknown tool requested: {name}")

        return function(**arguments)