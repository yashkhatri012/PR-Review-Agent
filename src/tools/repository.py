from pathlib import Path


class RepositoryTool:
    def __init__(self, repository_root: str) -> None:
        self.repository_root = Path(repository_root).resolve()

    def read_file(self, file_path: str) -> str:
        """Read a source file from within the repository.

    Args:
        file_path: Path to the file relative to the repository root.

    Returns:
        The contents of the requested file as a UTF-8 string.
    """
        requested_path = (self.repository_root / file_path).resolve()

        try:
            requested_path.relative_to(self.repository_root)
        except ValueError:
            raise ValueError("File path is outside the repository")

        if not requested_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if not requested_path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")

        return requested_path.read_text(encoding="utf-8")


    def get_tool_definition(self) -> dict:
        """Return the function declaration exposed to the LLM.

        Returns:
        A dictionary describing the read_file tool, including its name,
        purpose, accepted arguments, and required parameters.
        """
        return {
            "name": "read_file",
            "description": (
                "Read a source code file from the repository. "
                "Use this when you need additional context that is not "
                "included in the PR diff."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": (
                            "Path to the file relative to the repository root."
                        ),
                    }
                },
                "required": ["file_path"],
            },
        }


