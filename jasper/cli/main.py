import typer
import asyncio
import os
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.prompt import Prompt

# Import core components
from ..core.controller import JasperController
from ..agent.planner import Planner
from ..agent.executor import Executor
from ..agent.validator import validator
from ..agent.synthesizer import Synthesizer
from ..tools.financials import FinancialDataRouter
from ..tools.providers.alpha_vantage import AlphaVantageClient
from ..core.llm import get_llm
from ..observability.logger import SessionLogger

# Import UI components
from .interface import render_banner, render_mission_board, render_final_report
from ..core.config import THEME

console = Console()

class RichLogger(SessionLogger):
    def __init__(self, live: Live):
        super().__init__()
        self.live = live
        self.tasks = [] # List of task dicts for render_mission_board

    def log(self, event_type: str, payload: dict):
        # Override to update UI instead of printing JSON
        
        if event_type == "PLAN_CREATED":
            # Initialize tasks from plan
            self.tasks = [
                {"description": t.get("description", "Unknown Task"), "status": "pending", "detail": ""}
                for t in payload.get("plan", [])
            ]
            self.live.update(render_mission_board(self.tasks))

        elif event_type == "TASK_STARTED":
            # Update task status to running
            desc = payload.get("description")
            for t in self.tasks:
                if t["description"] == desc:
                    t["status"] = "running"
                    t["detail"] = "Executing..."
                    break
            self.live.update(render_mission_board(self.tasks))

        elif event_type == "TASK_COMPLETED":
            # Find the running task and mark completed
            status = payload.get("status")
            for t in self.tasks:
                if t["status"] == "running":
                    t["status"] = "success" if status == "completed" else "failed"
                    t["detail"] = ""
                    break
            self.live.update(render_mission_board(self.tasks))

def main(query: str = typer.Argument(None, help="The financial research question")):
    """Jasper Financial Research Agent"""
    
    # If no query provided via CLI args, ask interactively
    if not query:
        console.clear()
        console.print(render_banner())
        console.print("\n")
        query = Prompt.ask(f"[{THEME['Accent']}]?[/{THEME['Accent']}] Enter Financial Query")
        console.print("\n")
    else:
        console.clear()
        console.print(render_banner())
        console.print(f"\n[{THEME['Accent']}]Researching:[/{THEME['Accent']}] {query}\n")

    async def run():
        # Setup Live display with initial empty board
        with Live(render_mission_board([]), refresh_per_second=10, console=console) as live:
            
            # Initialize Logger with Live reference
            logger = RichLogger(live)
            
            # Initialize Components
            llm = get_llm(temperature=0)
            av_client = AlphaVantageClient(api_key=os.getenv("ALPHA_VANTAGE_API_KEY", "demo"))
            router = FinancialDataRouter(providers=[av_client])

            controller = JasperController(
                Planner(llm, logger=logger),
                Executor(router, logger=logger),
                validator(logger=logger),
                Synthesizer(llm, logger=logger),
                logger=logger,
            )

            # Run Controller
            state = await controller.run(query)
            
        # After Live block, show results
        console.print("\n")
        
        if state.status == "Failed":
            console.print(f"[bold {THEME['Error']}]Research Failed[/bold {THEME['Error']}]")
            if state.error:
                console.print(f"Error: {state.error}")
            if state.validation and state.validation.issues:
                console.print("[yellow]Validation Issues:[/yellow]")
                for issue in state.validation.issues:
                    console.print(f"  - {issue}")
        else:
            # Show Final Report with Confidence Breakdown and Answer
            answer = state.final_answer or "No answer generated."
            
            metrics = []
            if state.validation and state.validation.breakdown:
                b = state.validation.breakdown
                metrics = [
                    {"Metric": "Data Coverage", "Value": f"{b.data_coverage:.2f}", "Source": "Validator"},
                    {"Metric": "Data Quality", "Value": f"{b.data_quality:.2f}", "Source": "Validator"},
                    {"Metric": "Inference Strength", "Value": f"{b.inference_strength:.2f}", "Source": "Validator"},
                    {"Metric": "Overall Confidence", "Value": f"{b.overall:.2f}", "Source": "Validator"},
                ]
            
            console.print(render_final_report(answer, metrics))
            console.print("\n")

    asyncio.run(run())

if __name__ == "__main__":
    typer.run(main)
