from core.state import Jasperstate,validationresult

class validator:
  def validate(self, state: Jasperstate) -> validationresult:
    issues = []


    for task in state.plan:
      if task.status != "completed":
        issues.append(f"Task {task.id} not completed. Current status: {task.status}")

        if not state.task_results:
          issues.append("No task results found.")

    is_valid = len(issues) == 0
    confidence = 0.9 if is_valid else 0.2

    return validationresult(
      is_valid=is_valid,
      issues=issues,
      confidence=confidence
    )