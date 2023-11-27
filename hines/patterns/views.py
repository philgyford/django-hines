from django.http import Http404
from django.views.generic import TemplateView


class PatternsView(TemplateView):
    template_name = "patterns/home.html"

    valid_slugs = [
        "cards",
        "embeds",
        "forms",
        "galleries",
        "grid",
        "images",
        "lists",
        "media",
        "meta",
        "nav",
        "tables",
        "type",
        "utilities",
    ]

    def get_template_names(self):
        slug = self.kwargs.get("slug", None)

        if slug is None:
            return [self.template_name]
        elif slug in self.valid_slugs:
            return [f"patterns/{slug}.html"]
        else:
            msg = f"'{slug}' is not a valid slug."
            raise Http404(msg)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pages"] = self.valid_slugs
        context["current_page"] = self.kwargs.get("slug", None)
        return context
