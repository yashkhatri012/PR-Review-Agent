from agents.base import BaseAgent
from models.review import DiffAnalysis, ReviewResult
from services.repository_context import RepositoryContext
from services.llm import LLM
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

    def review(
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

Use the analysis to understand the scope of the change, but base every
finding on evidence from the supplied diff.

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