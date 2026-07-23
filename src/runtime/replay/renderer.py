from src.runtime.replay.models import ReplayExecution

class ReplayRenderer:
    @staticmethod
    def render_cli(replay: ReplayExecution) -> str:
        lines = [
            f"=== REPLAY EXECUTION: {replay.execution_id} ===",
            f"Session ID: {replay.session_id}",
            f"Timestamp: {replay.timestamp}",
            ""
        ]
        for idx, step in enumerate(replay.steps, 1):
            lines.append(f"▶ Step {idx}: [{step.component.upper()}] ({step.step_id})")
            lines.append(f"  Input:  {step.input_data}")
            lines.append(f"  Output: {step.output_data}")
            if step.metrics:
                lines.append(f"  Metrics: {step.metrics}")
            lines.append("")
        lines.append("=== END OF REPLAY ===")
        return "\n".join(lines)
