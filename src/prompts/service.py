from dataclasses import dataclass
from src.prompts.catalog import PromptCatalog

@dataclass
class RenderedPrompt:
    template_id: str
    version: str
    status: str
    content: str

class PromptService:
    def __init__(self, catalog: PromptCatalog):
        self.catalog = catalog

    def render(self, template_id: str, variables: dict, version: str = None, locale: str = "ro") -> RenderedPrompt:
        template = self.catalog.get(template_id, version)
        rendered_content = template.content
        for var in template.variables:
            if var in variables:
                rendered_content = rendered_content.replace(f"{{{{{var}}}}}", str(variables[var]))
        return RenderedPrompt(
            template_id=template_id,
            version=template.version,
            status=template.status,
            content=rendered_content
        )
