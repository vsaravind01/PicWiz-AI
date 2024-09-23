from core.search.templates.base_template import BaseSearchTemplate


class SearchPlugin:
    def __init__(self):
        self.templates: dict[str, BaseSearchTemplate] = {}

    def register_template(self, template: BaseSearchTemplate):
        self.templates[template.name] = template

    def get_templates(self) -> dict[str, BaseSearchTemplate]:
        return self.templates


search_plugin = SearchPlugin()
