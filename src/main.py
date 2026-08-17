import asyncio

from agents.bug import BugAgent
from agents.diff import DiffAgent
from agents.quality import QualityAgent
from agents.security import SecurityAgent
from orchestration.orchestrator import ReviewOrchestrator
from services.llm import LLM
from services.mcp_client import MCPClient
from services.repository_context import RepositoryContext


MCP_SERVER_URL = "http://127.0.0.1:8000/mcp"


async def main() -> None:
    """Run a pull-request review with shared review infrastructure."""
    llm = LLM()

    mcp_client = MCPClient(MCP_SERVER_URL)

    await mcp_client.connect()

    try:
        repository = RepositoryContext(mcp_client)

        diff_agent = DiffAgent(llm)
        bug_agent = BugAgent(llm, repository)
        security_agent = SecurityAgent(llm, repository)
        quality_agent = QualityAgent(llm, repository)

        orchestrator = ReviewOrchestrator(
            diff_agent=diff_agent,
            bug_agent=bug_agent,
            security_agent=security_agent,
            quality_agent=quality_agent,
        )

        # Temporary diff for testing the complete runtime.
        diff = """
diff --git a/calculator.py b/calculator.py
index 1234567..abcdefg 100644
--- a/calculator.py
+++ b/calculator.py
@@ -1,2 +1,2 @@
 def calculate_total(items):
-    return sum(item.price for item in items)
+    return sum(item.price for item in items) / len(items)
"""

        state = await orchestrator.run(diff)

        print(state.model_dump_json(indent=2))

    finally:
        await mcp_client.close()


if __name__ == "__main__":
    asyncio.run(main())