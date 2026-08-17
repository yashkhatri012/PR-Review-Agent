from agents.base import BaseAgent
from models.review import DiffAnalysis, ReviewResult
from services.repository_context import RepositoryContext
from services.llm import LLM


class BugAgent(BaseAgent):
    """Identify correctness issues introduced by a pull request."""

    def __init__(
        self,
        llm: LLM,
        repository: RepositoryContext,
    ) -> None:
        """Initialize the bug review agent.

        Args:
            llm: Shared LLM service used for bug analysis.
            repository: Shared repository context used to retrieve
                repository files and related code.
        """
        super().__init__(llm)
        self.repository = repository

    @property
    def name(self) -> str:
        """Return the unique identifier for the bug review agent.

        Returns:
            The string identifier used by the orchestrator.
        """
        return "bug_agent"

    def review(
        self,
        diff: str,
        diff_analysis: DiffAnalysis,
        # Why pass both diff and diff_analysis? The diff is the raw code changes, while diff_analysis is a structured summary of those changes. 
        # The agent uses both to identify potential bugs.
    ) -> ReviewResult:
        """Analyze a pull request for bugs and behavioral regressions.

        Args:
            diff: Unified diff containing the changes introduced by the PR.
            diff_analysis: Structured analysis produced by the DiffAgent.

        Returns:
            A structured collection of bug findings.
        """
        prompt = f"""
You are the Bug Review Agent in a multi-agent code review system.

Your ONLY responsibility is to identify correctness problems introduced
by the pull request.

Focus on:
- Logic errors
- Incorrect behavior
- Regressions
- Edge cases
- Broken assumptions
- Incorrect state transitions
- Invalid input handling

Do NOT report:
- Security vulnerabilities
- Code style issues
- Maintainability concerns
- Performance issues unless they cause incorrect behavior

You have the following analysis from the Diff Agent:

{diff_analysis.model_dump_json(indent=2)}

Use this analysis to understand what changed, but inspect the actual diff
carefully before reporting a finding.

Only report issues that are reasonably supported by the supplied code.
Do not invent behavior or assumptions.

If there are no clear bugs, return an empty findings list.

PR diff:

{diff}
"""

        return self.llm.generate_structured(
        prompt=prompt,
        response_model=ReviewResult,
    )