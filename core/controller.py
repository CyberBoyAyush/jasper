from agent.planner import Planner
from agent.executor import Executor
from agent.validator import validator
from agent.synthesizer import Synthesizer
from core.state import Jasperstate


class JasperController:
    def __init__(self, planner: Planner, executor: Executor, validator: validator, synthesizer: Synthesizer):
        self.planner = planner
        self.executor = executor
        self.validator = validator
        self.synthesizer = synthesizer

    async def run(self, query: str) -> Jasperstate:
        """Step through the entire workflow: plan → execute → validate → synthesize."""
        state = Jasperstate(query=query)
        state.status = "Planning"

        # Planning phase
        state.plan = await self.planner.plan(query)
        state.status = "Executing"

        # Execution phase
        for idx, task in enumerate(state.plan):
            state.current_task_index = idx
            await self.executor.execute_task(state, task)

        # Validation phase
        state.status = "Validating"
        state.validation = self.validator.validate(state)

        if not state.validation.is_valid:
            state.status = "Failed"
            return state

        # Synthesis phase
        state.final_answer = self.synthesizer.synthesize(state)
        state.status = "Completed"
        return state
