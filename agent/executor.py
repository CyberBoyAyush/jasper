from core.state import Task, Jasperstate
from tools.financials import FinancialClient, FinancialDataError

class Executor:
  def __init__(self, financial: FinancialClient):
    self.financial = financial

  async def execute_task(self, state: Jasperstate, task: Task) -> None:
    task.status = "in_progress"

    try:
      if "income statement" in task.description.lower():
        entity = self._extract_entity(task.description)  
        result = await self.financial.fetch_financial_statement(entity)
        state.task_results[task.id] = result
        task.status = "completed"
      else:
        raise ValueError(f"Unknown task description: {task.description}")
      
    except (FinancialDataError, Exception) as e:
      task.status = "failed"
      task.error = str(e)

  def _extract_entity(self, text: str) -> str:
    # intentionally simple, improve later 
    tokens = text.split()
    return tokens[-1]  # assume last token is entity name