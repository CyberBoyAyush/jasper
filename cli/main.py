import typer
import asyncio
from rich.console import Console
from rich.panel import Panel

from core.controller import JasperController
from agent.planner import Planner
from agent.executor import Executor
from agent.validator import validator
from agent.synthesizer import Synthesizer
from tools.financials import FinancialDataRouter
from tools.providers.alpha_vantage import AlphaVantageClient
from langchain_google_genai import ChatGoogleGenerativeAI
import os


app = typer.Typer()
console = Console()


@app.command()
def ask(query: str):
    async def run():
        # Initialize LLM and Providers
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
        av_client = AlphaVantageClient(api_key=os.getenv("ALPHA_VANTAGE_API_KEY", "demo"))
        router = FinancialDataRouter(providers=[av_client])

        controller = JasperController(
            Planner(llm),
            Executor(router),
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
