from agents.base import BaseAgent
from models.review import DiffAnalysis, ReviewResult
from services.llm import LLM
from services.repository_context import RepositoryContext


class SecurityAgent(BaseAgent):
    """Identify security vulnerabilities introduced by a pull request."""

    def __init__(
        self,
        llm: LLM,
        repository: RepositoryContext,
    ) -> None:
        """Initialize the security review agent.

        Args:
            llm: Shared LLM service used for security analysis.
            repository: Shared repository context used to retrieve
                repository files and related code.
        """
        super().__init__(llm)
        self.repository = repository

    @property
    def name(self) -> str:
        """Return the unique identifier for the security review agent.

        Returns:
            The string identifier used by the orchestrator.
        """
        return "security_agent"

    async def review(
        self,
        diff: str,
        diff_analysis: DiffAnalysis,
    ) -> ReviewResult:
        """Analyze a pull request for security vulnerabilities.

        Args:
            diff: Unified diff containing the changes introduced by the PR.
            diff_analysis: Structured analysis produced by the DiffAgent.

        Returns:
            A structured collection of security findings.
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
You are the Security Review Agent in a multi-agent code review system.

Your ONLY responsibility is to identify genuine security vulnerabilities
introduced or enabled by the pull request.

Focus on:
- SQL injection
- Command injection
- Path traversal
- Authentication flaws
- Authorization flaws
- Secrets or credential exposure
- Unsafe deserialization
- Server-side request forgery
- Cross-site scripting
- Insecure cryptography
- Improper input validation
- Dangerous file or system operations
- Other concrete security vulnerabilities

Do NOT report:
- General bugs
- Code style issues
- Maintainability concerns
- Performance issues
- Hypothetical vulnerabilities without evidence

You have the following analysis from the Diff Agent:

{diff_analysis.model_dump_json(indent=2)}

You also have the contents of the changed repository files:

{repository_context_text}

Use the repository contents together with the PR diff to understand the
actual implementation surrounding the changes.

Only report vulnerabilities that are reasonably supported by the code.
Do not invent application behavior that is not shown.

If there are no clear security vulnerabilities, return an empty findings list.

PR diff:

{diff}
"""

        return self.llm.generate_structured(
            prompt=prompt,
            response_model=ReviewResult,
        )