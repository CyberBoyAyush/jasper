from ..agent.planner import Planner
from ..agent.executor import Executor
from ..agent.validator import validator
from ..agent.synthesizer import Synthesizer
from .state import Jasperstate, FinalReport
from ..observability.logger import SessionLogger


# --- Jasper Controller ---
# Orchestrates the flow between Planner, Executor, Validator, and Synthesizer
class JasperController:
    def __init__(self, planner: Planner, executor: Executor, validator: validator, synthesizer: Synthesizer, logger: SessionLogger | None = None):
        self.planner = planner
        self.executor = executor
        self.validator = validator
        self.synthesizer = synthesizer
        # Use provided logger to keep session_id consistent across components
        self.logger = logger or SessionLogger()

    async def run(self, query: str) -> Jasperstate:
        """Step through the entire workflow: plan → execute → validate → synthesize."""
        state = Jasperstate(query=query)
        state.status = "Planning"
        try:
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
            self.logger.log("VALIDATION_STARTED", {})
            try:
                state.validation = self.validator.validate(state)
            except Exception as e:
                self.logger.log("VALIDATION_ERROR", {"error": str(e)})
                state.status = "Failed"
                state.error = f"Validation error: {str(e)}"
                return state

            if not state.validation.is_valid:
                self.logger.log("VALIDATION_FAILED", {"issues": state.validation.issues})
                state.status = "Failed"
                return state

            # Synthesis phase
            state.status = "Synthesizing"
            self.logger.log("SYNTHESIS_STARTED", {})
            try:
                state.final_answer = await self.synthesizer.synthesize(state)
                self.logger.log("FINAL_ANSWER", {"answer": state.final_answer})
                state.status = "Completed"
                
                # Construct FinalReport for audit-ready export
                state.report = self._build_final_report(state)
                self.logger.log("REPORT_CREATED", {"report_valid": state.report.is_valid})
                
            except Exception as e:
                # Distinguish LLM errors from other failures
                error_msg = str(e)
                if "524" in error_msg or "provider returned error" in error_msg.lower():
                    state.error = f"LLM service error (code 524): Temporary rate limit. Please try again in a moment."
                    state.error_source = "llm_service"
                elif "401" in error_msg or "unauthorized" in error_msg.lower():
                    state.error = "LLM authentication failed. Check your OpenRouter API key."
                    state.error_source = "llm_auth"
                elif "timeout" in error_msg.lower():
                    state.error = "LLM request timed out. Please try again."
                    state.error_source = "llm_timeout"
                else:
                    state.error = f"Answer synthesis failed: {error_msg}"
                    state.error_source = "llm_unknown"
                self.logger.log("SYNTHESIS_ERROR", {"error": state.error, "source": state.error_source})
                state.status = "Failed"
            return state

        except Exception as e:
            # Surface any unexpected errors as structured failure
            self.logger.log("WORKFLOW_ERROR", {"error": str(e)})
            state.status = "Failed"
            # attach error for CLI visibility
            state.error = str(e)
            return state

    def _build_final_report(self, state: Jasperstate) -> FinalReport:
        """
        Construct a FinalReport object from Jasperstate.
        
        This is the single source of truth for PDF exports.
        """
        # Extract tickers and sources from plan
        tickers = []
        sources = set()
        for task in state.plan:
            if task.tool_args:
                ticker = task.tool_args.get("ticker") or task.tool_args.get("symbol")
                if ticker:
                    tickers.append(ticker.upper())
            if task.tool_name:
                sources.add(task.tool_name.replace("_", " ").title())
        
        # Deduplicate tickers while preserving order
        unique_tickers = []
        for t in tickers:
            if t not in unique_tickers:
                unique_tickers.append(t)
        
        # Fallbacks
        if not unique_tickers:
            unique_tickers = []
        if not sources:
            sources = {"SEC EDGAR", "Financial Data Providers"}
        
        # Construct FinalReport
        report = FinalReport(
            query=state.query,
            data_sources=list(sources),
            tickers=unique_tickers,
            synthesis_text=state.final_answer or "",
            is_valid=state.validation.is_valid if state.validation else False,
            validation_issues=state.validation.issues if state.validation else [],
            confidence_score=state.validation.confidence if state.validation else 0.0,
            confidence_breakdown=state.validation.breakdown if state.validation else None,
            task_count=len(state.plan),
            task_results=state.task_results,
        )
        
        return report
