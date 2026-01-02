from core.state import Task, Jasperstate
from tools.financials import FinancialDataRouter, FinancialDataError
import json


# --- Executor ---
# Executes research tasks using available tools and data providers
class Executor:
    def __init__(self, financial_router: FinancialDataRouter):
        self.financial_router = financial_router

    async def execute_task(self, state: Jasperstate, task: Task) -> None:
        task.status = "in_progress"

        try:
            if "income statement" in task.description.lower():
                # Extract ticker from tool_args if available
                ticker = None
                if task.tool_args:
                    ticker = task.tool_args.get("ticker")
                
                if not ticker:
                    # Fallback or error
                    raise ValueError(f"No ticker found for task: {task.description}")

                result = await self.financial_router.fetch_income_statement(ticker)
                state.task_results[task.id] = result
                task.status = "completed"
            else:
                raise ValueError(f"Unknown task description: {task.description}")
          
        except (FinancialDataError, Exception) as e:
            task.status = "failed"
            task.error = str(e)
