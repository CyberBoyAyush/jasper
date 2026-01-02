from agent.planner import Planner
from agent.executor import Executor
from agent.validator import validator
from agent.synthesizer import Synthesizer
from core.state import Jasperstate
from observability.logger import SessionLogger


# --- Jasper Controller ---
# Orchestrates the flow between Planner, Executor, Validator, and Synthesizer
class JasperController:
    def __init__(self, planner: Planner, executor: Executor, validator: validator, synthesizer: Synthesizer):
        self.planner = planner
        self.executor = executor
        self.validator = validator
        self.synthesizer = synthesizer
        self.logger = SessionLogger()

    async def run(self, query: str) -> Jasperstate:
        """Step through the entire workflow: plan → execute → validate → synthesize."""
        state = Jasperstate(query=query)
        state.status = "Planning"

        # Planning phase
        state.plan = await self.planner.plan(query)
        self.logger.log("PLAN_CREATED", {"plan": [t.dict() for t in state.plan]})
        state.status = "Executing"

        # Execution phase
        for idx, task in enumerate(state.plan):
            state.current_task_index = idx
            self.logger.log("TASK_STARTED", {"task_id": task.id, "description": task.description})
            await self.executor.execute_task(state, task)
            self.logger.log("TASK_COMPLETED", {"task_id": task.id, "status": task.status})

        # Validation phase
        state.status = "Validating"
        state.validation = self.validator.validate(state)

        if not state.validation.is_valid:
            self.logger.log("VALIDATION_FAILED", {"issues": state.validation.issues})
            state.status = "Failed"
            return state

        # Synthesis phase
        state.final_answer = self.synthesizer.synthesize(state)
        self.logger.log("FINAL_ANSWER", {"answer": state.final_answer})
        state.status = "Completed"
        return state
