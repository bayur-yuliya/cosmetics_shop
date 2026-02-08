from typing import Type

from django.db import models
from django.http import HttpRequest
from django.views.generic.base import ContextMixin


class PageTitleMixin(ContextMixin):
    page_title = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.page_title
        return context


class ModelPermissionMixin(ContextMixin):
    """Automatically calculates permissions for the current view model."""

    model: Type[models.Model] | None = None
    request: HttpRequest
    object: models.Model | None = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        target_model = self.model
        if target_model is None and self.object is not None:
            target_model = type(self.object)

        if target_model:
            opts = target_model._meta
            app_label = opts.app_label
            model_name = opts.model_name

            context["permissions"] = {
                "add": self.request.user.has_perm(f"{app_label}.add_{model_name}"),
                "change": self.request.user.has_perm(
                    f"{app_label}.change_{model_name}"
                ),
                "view": self.request.user.has_perm(f"{app_label}.view_{model_name}"),
                "delete": self.request.user.has_perm(
                    f"{app_label}.delete_{model_name}"
                ),
            }
        return context
