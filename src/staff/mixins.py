class PageTitleMixin:
    page_title = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.page_title
        return context


class ModelPermissionMixin:
    """Automatically calculates permissions for the current view model."""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.model or self.object.__class__

        model_fields = model._meta
        app_label = model_fields.app_label
        model_name = model_fields.model_name

        context["permissions"] = {
            "add": self.request.user.has_perm(f"{app_label}.add_{model_name}"),
            "change": self.request.user.has_perm(f"{app_label}.change_{model_name}"),
            "view": self.request.user.has_perm(f"{app_label}.view_{model_name}"),
            "delete": self.request.user.has_perm(f"{app_label}.delete_{model_name}"),
        }
        return context
