import os
import yaml
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from src.prompts.catalog import PromptCatalog

@dataclass
class PromptTemplate:
    namespace: str
    category: str
    name: str
    version: str
    locale: str
    status: str
    alias: str
    compatible_models: List[str]
    tags: List[str]
    author: str
    description: str
    variables: List[str]
    output: str
    content: str = ""

class PromptTemplateLoader:
    @staticmethod
    def load_catalog(templates_root: str) -> PromptCatalog:
        catalog = PromptCatalog()
        for root, dirs, files in os.walk(templates_root):
            for file in files:
                if file.endswith(".yaml") or file.endswith(".yml"):
                    yaml_path = os.path.join(root, file)
                    with open(yaml_path, "r", encoding="utf-8") as f:
                        docs = list(yaml.safe_load_all(f))
                        if not docs:
                            continue
                        meta = docs[0]
                        content = docs[1] if len(docs) > 1 else ""
                        
                        template = PromptTemplate(
                            namespace=meta.get("namespace", "default"),
                            category=meta.get("category", "general"),
                            name=meta.get("name", "prompt"),
                            version=str(meta.get("version", "1.0.0")),
                            locale=meta.get("locale", "ro"),
                            status=meta.get("status", "active"),
                            alias=meta.get("alias", "latest"),
                            compatible_models=meta.get("compatible_models", []),
                            tags=meta.get("tags", []),
                            author=meta.get("author", "NicMar"),
                            description=meta.get("description", ""),
                            variables=meta.get("variables", []),
                            output=meta.get("output", "markdown"),
                            content=content.strip()
                        )
                        catalog.register(template)
        return catalog
