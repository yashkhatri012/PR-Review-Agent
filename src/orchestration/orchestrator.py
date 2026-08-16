from agents.bug import BugAgent
from agents.diff import DiffAgent
from agents.quality import QualityAgent
from agents.security import SecurityAgent
from models.state import ReviewState


class ReviewOrchestrator:
    """Coordinate the execution of specialized PR review agents."""

    def __init__(
        self,
        diff_agent: DiffAgent,
        bug_agent: BugAgent,
        security_agent: SecurityAgent,
        quality_agent: QualityAgent,
    ) -> None:
        """Initialize the review orchestrator.

        Args:
            diff_agent: Agent responsible for analyzing the PR diff.
            bug_agent: Agent responsible for identifying correctness issues.
            security_agent: Agent responsible for identifying security issues.
            quality_agent: Agent responsible for identifying quality issues.
        """
        self.diff_agent = diff_agent
        self.bug_agent = bug_agent
        self.security_agent = security_agent
        self.quality_agent = quality_agent

    def run(self, diff: str) -> ReviewState:
        """Execute the PR review workflow.

        Args:
            diff: Unified diff containing the pull-request changes.

        Returns:
            Review state containing the analysis and findings produced by
            the specialized review agents.
        """
        state = ReviewState(diff=diff)

        state.diff_analysis = self.diff_agent.review(diff)

        bug_result = self.bug_agent.review(
            diff=diff,
            diff_analysis=state.diff_analysis,
        )

        security_result = self.security_agent.review(
            diff=diff,
            diff_analysis=state.diff_analysis,
        )

        quality_result = self.quality_agent.review(
            diff=diff,
            diff_analysis=state.diff_analysis,
        )

        state.bug_findings = bug_result.findings
        state.security_findings = security_result.findings
        state.quality_findings = quality_result.findings

        return state