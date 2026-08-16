from models.review import DiffAnalysis
from agents.base import BaseAgent


class DiffAgent(BaseAgent):
    """Analyze a pull-request diff and summarize its impact."""

    @property
    def name(self) -> str:
        """Return the unique identifier for the diff analysis agent.

        Returns:
            The string identifier used by the orchestrator.
        """
        return "diff_agent"

    def review(self, diff: str) -> DiffAnalysis:
        """Analyze the supplied pull-request diff.

        Args:
            diff: Unified diff containing the changes introduced by the PR.

        Returns:
            Structured analysis describing the files, symbols, and nature
            of the changes.
        """
        prompt = f"""
You are the Diff Analysis Agent in a multi-agent code review system.

Your responsibility is ONLY to understand and summarize what changed
in the pull request.

Do not identify bugs.
Do not identify security vulnerabilities.
Do not suggest code-quality improvements.

Analyze the supplied Git diff and determine:

1. A concise summary of the changes.
2. Which files were changed.
3. Which functions, classes, methods, or other symbols are affected.
4. The types of changes introduced.

Possible change types include:
- behavioral
- logic
- API
- database
- configuration
- dependency
- refactoring
- testing
- documentation
- infrastructure

If a piece of information cannot be determined from the diff,
do not invent it.

Git diff:

{diff}
"""

        return self.llm.generate(
            prompt=prompt,
            response_model=DiffAnalysis,
        )