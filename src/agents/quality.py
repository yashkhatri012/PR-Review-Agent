from agents.base import BaseAgent
from models.review import DiffAnalysis, ReviewResult
from services.repository_context import RepositoryContext
from services.llm import LLM

class QualityAgent(BaseAgent):
    """Identify maintainability and code-quality issues in a pull request."""
    def __init__(
        self,
        llm: LLM,
        repository: RepositoryContext,
    ) -> None:
        """Initialize the security review agent.

        Args:
            llm: Shared LLM service used for Quality analysis.
            repository: Shared repository context used to retrieve
                repository files and related code.
        """
        super().__init__(llm)
        self.repository = repository

    @property
    def name(self) -> str:
        """Return the unique identifier for the quality review agent.

        Returns:
            The string identifier used by the orchestrator.
        """
        return "quality_agent"

    def review(
        self,
        diff: str,
        diff_analysis: DiffAnalysis,
    ) -> ReviewResult:
        """Analyze a pull request for maintainability and quality issues.

        Args:
            diff: Unified diff containing the changes introduced by the PR.
            diff_analysis: Structured analysis produced by the DiffAgent.

        Returns:
            A structured collection of quality findings.
        """
        prompt = f"""
You are the Quality Review Agent in a multi-agent code review system.

Your ONLY responsibility is to identify meaningful code-quality and
maintainability problems introduced by the pull request.

Focus on:
- Unnecessary complexity
- Excessive duplication
- Poor abstractions
- Tight coupling
- Poor separation of responsibilities
- Difficult-to-maintain code
- Missing or inappropriate error handling
- Significant readability problems
- Fragile implementations
- Inconsistent design patterns

Do NOT report:
- Security vulnerabilities
- Ordinary bugs
- Minor formatting or style preferences
- Subjective personal preferences
- Issues that do not meaningfully affect maintainability

You have the following analysis from the Diff Agent:

{diff_analysis.model_dump_json(indent=2)}

Use the analysis to understand the scope of the change, but base every
finding on evidence from the supplied diff.

Only report meaningful issues that are reasonably supported by the code.
Do not invent application behavior.

If there are no clear quality issues, return an empty findings list.

PR diff:

{diff}
"""

        return self.llm.generate_structured(
        prompt=prompt,
        response_model=ReviewResult,
    )