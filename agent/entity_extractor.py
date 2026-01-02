from typing import List
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate


# --- Entity Model ---
# Defines the structure for extracted financial entities
class Entity(BaseModel):
    name: str
    type: str  # company, index, sector, macro
    ticker: str | None = None


NER_PROMPT = """
Extract financial entities from the user query.

Rules:
- Identify companies, indices, sectors, macro indicators
- Include ticker if confidently known
- If uncertain, leave ticker null
- Do NOT guess

Return JSON only.

Query:
{query}
"""


# --- Entity Extractor ---
# Handles the interpretation of user queries to identify financial entities
class EntityExtractor:
    def __init__(self, llm: ChatGoogleGenerativeAI):
        self.llm = llm

    async def extract(self, query: str) -> List[Entity]:
        prompt = ChatPromptTemplate.from_template(NER_PROMPT)
        generate_result = await self.llm.agenerate([prompt.format_messages(query=query)])
        raw = generate_result.generations[0][0].text

        data = eval(raw)
        return [Entity(**e) for e in data.get("entities", [])]
        