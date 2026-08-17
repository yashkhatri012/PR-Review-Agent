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

    async def review(
        self,
        diff: str,
        diff_analysis: DiffAnalysis,
    ) -> ReviewResult:
        """Analyze a pull request for bugs and behavioral regressions.

        Args:
            diff: Unified diff containing the changes introduced by the PR.
            diff_analysis: Structured analysis produced by the DiffAgent.

        Returns:
            A structured collection of bug findings.
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

You also have the contents of the changed repository files:

{repository_context_text}

Use the repository contents together with the PR diff to understand the
actual implementation surrounding the changes.

Only report issues that are reasonably supported by the code.
Do not invent application behavior or assumptions.

If there are no clear bugs, return an empty findings list.

PR diff:

{diff}
"""

        return self.llm.generate_structured(
            prompt=prompt,
            response_model=ReviewResult,
        )