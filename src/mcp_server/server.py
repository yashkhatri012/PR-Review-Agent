from pathlib import Path

from mcp.server.fastmcp import FastMCP


mcp = FastMCP(
    "pr-review-repository",
    host="127.0.0.1",
    port=8000,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[2] / "sample-repo"


@mcp.tool()
def read_file(file_path: str) -> str:
    """Read a source file from the sample repository.

    Args:
        file_path: Path to the file relative to the repository root.

    Returns:
        The complete contents of the requested file.

    Raises:
        ValueError: If the requested path escapes the repository root.
        FileNotFoundError: If the requested file does not exist.
    """
    requested_path = (REPOSITORY_ROOT / file_path).resolve()

    try:
        requested_path.relative_to(REPOSITORY_ROOT)
    except ValueError as exc:
        raise ValueError(
            "File path is outside the repository"
        ) from exc

    if not requested_path.is_file():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    return requested_path.read_text(encoding="utf-8")



if __name__ == "__main__":
    mcp.run(transport="streamable-http")