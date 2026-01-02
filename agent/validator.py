from core.state import Jasperstate, validationresult


# --- Validator ---
# Enforces financial domain logic and task completeness
class validator:
    def validate(self, state: Jasperstate) -> validationresult:
        issues = []

        # 1. Task completion
        for task in state.plan:
            if task.status != "completed":
                issues.append(f"Incomplete task: {task.description}")

        # 2. Data sanity checks
        for task_id, data in state.task_results.items():
            if not data:
                issues.append(f"Empty data for task {task_id}")

        # 3. Financial logic checks
        self._validate_financial_consistency(state, issues)

        is_valid = len(issues) == 0

        return validationresult(
            is_valid=is_valid,
            issues=issues,
            confidence=0.9 if is_valid else 0.3,
        )

    def _validate_financial_consistency(self, state: Jasperstate, issues: list):
        # Example: revenue must be non-negative
        for result in state.task_results.values():
            # Assuming result might be a list of reports or a single report
            reports = result if isinstance(result, list) else [result]
            for report in reports:
                if isinstance(report, dict):
                    revenue = report.get("totalRevenue")
                    if revenue is not None:
                        try:
                            if float(revenue) < 0:
                                issues.append("Negative revenue detected")
                        except (ValueError, TypeError):
                            pass
