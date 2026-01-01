import typer
import asyncio
from rich.console import Console
from rich.panel import Panel

from core.controller import JasperController
from agent.planner import Planner
from agent.executor import Executor
from agent.validator import validator
from agent.synthesizer import Synthesizer
from tools.financials import FinancialClient
from langchain_google_genai import ChatGoogleGenerativeAI


app = typer.Typer()
console = Console()


@app.command()
def ask(query: str):
    async def run():
        llm = ChatGoogleGenerativeAI(temperature=0)
        controller = JasperController(
            Planner(llm),
            Executor(FinancialClient()),
            validator(),
            Synthesizer(),
        )

        console.print(Panel("Planning research...", title="Jasper"))
        state = await controller.run(query)

        if state.status == "Failed":
            console.print("[red]Research failed[/red]")
            if state.validation:
                for issue in state.validation.issues:
                    console.print(f"- {issue}")
        else:
            answer = state.final_answer or "No answer generated."
            console.print(Panel(answer, title="Validated Answer"))

    asyncio.run(run())


if __name__ == "__main__":
    app()
