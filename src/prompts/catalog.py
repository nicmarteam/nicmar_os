class PromptCatalog:
    def __init__(self):
        self.templates_by_base = {}

    def register(self, template):
        base_id = f"{template.namespace}.{template.category}.{template.name}"
        if base_id not in self.templates_by_base:
            self.templates_by_base[base_id] = {}
        self.templates_by_base[base_id][template.version] = template

    def get(self, template_id: str, version: str = None) -> object:
        if template_id not in self.templates_by_base:
            raise KeyError(f"Template-ul {template_id} nu există în catalog.")
        versions = self.templates_by_base[template_id]
        if version:
            if version not in versions:
                raise KeyError(f"Versiunea {version} nu există pentru {template_id}.")
            return versions[version]
        # Returnează cea mai recentă versiune sau alias-ul "latest"
        latest_version = max(versions.keys())
        return versions[latest_version]
