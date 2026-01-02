import uuid
from typing import List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from core.state import Task
from agent.entity_extractor import EntityExtractor


PLANNER_PROMPT = """
You are a financial research planner.

Extracted Entities:
{entities}

Your job:
- Break the user's question into explicit, ordered research tasks.
- Each task must declare what data it requires.
- Use the extracted entities (tickers, names) in the task arguments.
- Do NOT assume data exists.
- Do NOT compute results.
- Do NOT answer the question.

Output JSON ONLY.

User question:
{query}
"""


# --- Planner ---
# Orchestrates the research process by breaking down queries into tasks
class Planner:
    def __init__(self, llm: ChatGoogleGenerativeAI):
        self.llm = llm
        self.extractor = EntityExtractor(llm)

    async def plan(self, query: str) -> List[Task]:
        # Preprocessing: Extract entities
        entities = await self.extractor.extract(query)
        entities_str = "\n".join([f"- {e.name} ({e.type}): {e.ticker or 'N/A'}" for e in entities])
        
        prompt = ChatPromptTemplate.from_template(PLANNER_PROMPT)
        generate_result = await self.llm.agenerate([prompt.format_messages(query=query, entities=entities_str)])
        response = generate_result.generations[0][0].text

        try:
            import json
            parsed = json.loads(response)
        except:
            parsed = eval(response)  # intentionally strict: fail fast

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
