from collections.abc import Callable

from google.genai import types


class ToolRegistry:
    """Register, describe, and execute tools available to review agents."""

    def __init__(self) -> None:
        """Initialize an empty tool registry."""
        self._tools: dict[str, Callable] = {}
        self._declarations: dict[str, types.FunctionDeclaration] = {}

    def register(
        self,
        name: str,
        function: Callable,
        declaration: types.FunctionDeclaration,
    ) -> None:
        """Register a callable and its Gemini function declaration.

        Args:
            name: Unique name used by the model to request the tool.
            function: Python callable that executes the tool.
            declaration: Gemini function declaration describing the tool.
        """
        self._tools[name] = function
        self._declarations[name] = declaration

    def get_declarations(self) -> list[types.FunctionDeclaration]:
        """Return all registered tool declarations.

        Returns:
            Function declarations that can be supplied to Gemini.
        """
        return list(self._declarations.values())

    def execute(
        self,
        name: str,
        arguments: dict,
    ) -> object:
        """Execute a registered tool using model-provided arguments.

        Args:
            name: Name of the requested tool.
            arguments: Keyword arguments supplied by the model.

        Returns:
            The result returned by the tool.

        Raises:
            ValueError: If the requested tool is not registered.
        """
        function = self._tools.get(name)

        if function is None:
            raise ValueError(f"Unknown tool requested: {name}")

        return function(**arguments)