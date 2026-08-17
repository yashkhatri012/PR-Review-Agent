from agents.base import BaseAgent
from models.review import DiffAnalysis, ReviewResult
from services.llm import LLM
from services.repository_context import RepositoryContext


class QualityAgent(BaseAgent):
    """Identify maintainability and code-quality issues in a pull request."""

    def __init__(
        self,
        llm: LLM,
        repository: RepositoryContext,
    ) -> None:
        """Initialize the quality review agent.

        Args:
            llm: Shared LLM service used for quality analysis.
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

    async def review(
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
        repository_context = []

        for file_path in diff_analysis.changed_files:
            content = await self.repository.get_file(file_path)

            repository_context.append(
                f"""
--- {file_path} ---
{content}
"""
            )

        repository_context_text = "\n".join(repository_context)

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

You also have the contents of the changed repository files:

{repository_context_text}

Use the repository contents together with the PR diff to understand the
actual implementation surrounding the changes.

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