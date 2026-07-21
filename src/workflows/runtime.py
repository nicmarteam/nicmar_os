from typing import List
from src.workflows.models import WorkflowContext, WorkflowStepResult
from src.workflows.steps import WorkflowStep

class WorkflowRuntime:
    def __init__(self, workflow_id: str, steps: List[WorkflowStep]):
        self.workflow_id = workflow_id
        self.steps = steps

    def run(self, input_data: dict = None) -> WorkflowContext:
        context = WorkflowContext(workflow_id=self.workflow_id, input_data=input_data or {})
        context.status = "running"
        
        for step in self.steps:
            result = step.execute(context)
            context.state[step.name] = result.output
            
            if result.status == "failed":
                context.status = "failed"
                context.logs.append(f"Workflow stopped at step '{step.name}' due to failure.")
                return context

        context.status = "completed"
        context.logs.append("Workflow completed successfully.")
        return context
