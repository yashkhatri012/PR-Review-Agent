from agents.bug import BugAgent
from agents.diff import DiffAgent
from agents.quality import QualityAgent
from agents.security import SecurityAgent
from orchestration.orchestrator import ReviewOrchestrator
from services.llm_provider import LLMProvider


diff = """
diff --git a/users.py b/users.py
index 1234567..abcdefg 100644
--- a/users.py
+++ b/users.py
@@ -10,7 +10,8 @@ def get_user(user_id):
-    return get_user_from_repository(user_id)
+    query = f"SELECT * FROM users WHERE id = {user_id}"
+    return db.execute(query)
"""


llm = LLMProvider()

orchestrator = ReviewOrchestrator(
    diff_agent=DiffAgent(llm),
    bug_agent=BugAgent(llm),
    security_agent=SecurityAgent(llm),
    quality_agent=QualityAgent(llm),
)

state = orchestrator.run(diff)

print(state.model_dump_json(indent=2))