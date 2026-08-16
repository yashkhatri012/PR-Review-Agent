from enum import Enum

from pydantic import BaseModel, Field


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ReviewFinding(BaseModel):
    severity: Severity
    category: str
    file: str
    line: int | None = None
    message: str
    suggestion: str | None = None

class ReviewResult(BaseModel):
    findings: list[ReviewFinding]

class DiffAnalysis(BaseModel):
    """Represent the structured understanding of a pull request diff."""

    summary: str
    changed_files: list[str]
    affected_symbols: list[str]
    change_types: list[str]
