from core.state import Task, Jasperstate

class Synthesizer:
  def synthesize(self, state: Jasperstate) -> str:
    lines=[]
    lines.append("Validated Financial Research Results:\n")
    lines.append(f"Question:{state.query}\n")

    lines.append("Facts:")
    for k,v in state.task_results.items():
      lines.append(f"- {k}: {v}")


    lines.append(f"\nConfidence:")
    lines.append(str(state.validation.confidence) if state.validation else "N/A")

    return "\n".join(lines)
