from core.state import Task, Jasperstate, ConfidenceBreakdown


# --- Confidence Calculation ---
# Computes a detailed confidence breakdown based on task results and errors
def compute_confidence(state: Jasperstate) -> ConfidenceBreakdown:
    if not state.plan:
        return ConfidenceBreakdown(data_coverage=0, data_quality=0, inference_strength=0, overall=0)
        
    coverage = len(state.task_results) / len(state.plan)

    quality = 1.0
    for task in state.plan:
        if task.error:
            quality -= 0.2
    quality = max(0, quality)

    inference = 0.8 if coverage > 0.8 else 0.5

    overall = round((coverage + quality + inference) / 3, 2)

    return ConfidenceBreakdown(
        data_coverage=round(coverage, 2),
        data_quality=round(quality, 2),
        inference_strength=inference,
        overall=overall,
    )


# --- Synthesizer ---
# Combines task results into a final answer with confidence breakdown
class Synthesizer:
  def synthesize(self, state: Jasperstate) -> str:
    lines=[]
    lines.append("Validated Financial Research Results:\n")
    lines.append(f"Question:{state.query}\n")

    lines.append("Facts:")
    for k,v in state.task_results.items():
      lines.append(f"- {k}: {v}")

    confidence = compute_confidence(state)
    lines.append(f"\nConfidence Breakdown:")
    lines.append(f"- Data coverage: {confidence.data_coverage:.2f}")
    lines.append(f"- Data quality: {confidence.data_quality:.2f}")
    lines.append(f"- Inference strength: {confidence.inference_strength:.2f}")
    lines.append(f"- Overall confidence: {confidence.overall:.2f}")

    return "\n".join(lines)
