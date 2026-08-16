from pydantic import BaseModel, Field

from models.review import DiffAnalysis, ReviewFinding


class ReviewState(BaseModel):
    """Store the shared state passed between PR review agents."""

    diff: str

    diff_analysis: DiffAnalysis | None = None

    bug_findings: list[ReviewFinding] = Field(default_factory=list)
    security_findings: list[ReviewFinding] = Field(default_factory=list)
    quality_findings: list[ReviewFinding] = Field(default_factory=list)

    verified_findings: list[ReviewFinding] = Field(default_factory=list)