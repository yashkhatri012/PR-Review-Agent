from agents.diff import DiffAgent
from services.llm import LLM


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


llm = LLM()

agent = DiffAgent(llm)

result = agent.review(diff)

print("Current model:")
print(llm.current_model)

print("\nDiff analysis:")
print(result.model_dump_json(indent=2))