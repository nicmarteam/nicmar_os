from abc import ABC, abstractmethod
from typing import Dict, Any
from src.workflows.models import WorkflowContext, WorkflowStepResult

class WorkflowStep(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def execute(self, context: WorkflowContext) -> WorkflowStepResult:
        pass

class LambdaWorkflowStep(WorkflowStep):
    def __init__(self, name: str, func: callable):
        super().__init__(name)
        self.func = func

    def execute(self, context: WorkflowContext) -> WorkflowStepResult:
        try:
            result = self.func(context)
            context.logs.append(f"Step '{self.name}' executed successfully.")
            return WorkflowStepResult(step_name=self.name, status="success", output=result)
        except Exception as e:
            context.logs.append(f"Step '{self.name}' failed with error: {str(e)}")
            return WorkflowStepResult(step_name=self.name, status="failed", error=str(e))
