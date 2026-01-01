import uuid
from typing import List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from core.state import Task


PLANNER_PROMPT = """
You are a financial research planner.

Your job:
- Break the user's question into explicit, ordered research tasks.
- Each task must declare what data it requires.
- Do NOT assume data exists.
- Do NOT compute results.
- Do NOT answer the question.

Output JSON ONLY.

User question:
{query}
"""


class Planner:
    def __init__(self, llm: ChatGoogleGenerativeAI):
        self.llm = llm

    async def plan(self, query: str) -> List[Task]:
        prompt = ChatPromptTemplate.from_template(PLANNER_PROMPT)
        generate_result = await self.llm.agenerate([prompt.format_messages(query=query)])
        response = generate_result.generations[0][0].text

        try:
            parsed = eval(response)  # intentionally strict: fail fast
        except Exception as e:
            raise ValueError(f"Planner output not valid JSON: {e}")

        tasks: List[Task] = []
        for t in parsed.get("tasks", []):
            tasks.append(
                Task(
                    id=str(uuid.uuid4()),
                    description=t["description"],
                    tool_name=t.get("tool_name", ""),
                    tool_args=t.get("tool_args", {}),
                    status=t.get("status", "pending"),
                    error=t.get("error", None),
                )
            )

        if not tasks:
            raise ValueError("Planner produced empty task list")

        return tasks
