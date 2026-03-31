import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import DeleteView, ListView

from config.settings.base import PRODUCTS_PER_PAGE
from staff.mixins import (
    ModelPermissionMixin,
    PageTitleMixin,
    StaffPermissionExceptionMixin,
)

logger = logging.getLogger(__name__)


class BaseStaffListView(
    PageTitleMixin,
    ModelPermissionMixin,
    LoginRequiredMixin,
    StaffPermissionExceptionMixin,
    ListView,
):
    template_name = "staff/catalog/lists_page.html"
    paginate_by = PRODUCTS_PER_PAGE
    context_object_name = "objects"


class BaseStaffManageView(
    PageTitleMixin, LoginRequiredMixin, StaffPermissionExceptionMixin
):
    template_name: str | None = "staff/catalog/manage_page.html"


class BaseStaffDeleteView(
    PageTitleMixin, LoginRequiredMixin, StaffPermissionExceptionMixin, DeleteView
):
    http_method_names = ["post", "delete"]

    def form_valid(self, form):
        success_url = self.get_success_url()

        logger.info(
            f"Staff delete: user_id={self.request.user.id}, object_id={self.object.id}"
        )

        self.object.delete()

        messages.success(self.request, "Успешное удаление")
        return redirect(success_url)
