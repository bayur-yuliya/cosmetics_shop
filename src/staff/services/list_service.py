from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import ListView, CreateView, DeleteView, UpdateView

from config.settings import PRODUCTS_PER_PAGE
from staff.mixins import (
    PageTitleMixin,
    ModelPermissionMixin,
    StaffPermissionExceptionMixin,
)


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


class BaseStaffCreateView(
    PageTitleMixin, LoginRequiredMixin, StaffPermissionExceptionMixin, CreateView
):
    template_name = "staff/catalog/create_page.html"


class BaseStaffChangeView(
    PageTitleMixin, LoginRequiredMixin, StaffPermissionExceptionMixin, UpdateView
):
    template_name = "staff/catalog/update_page.html"


class BaseStaffDeleteView(
    PageTitleMixin, LoginRequiredMixin, StaffPermissionExceptionMixin, DeleteView
):
    http_method_names = ["post", "delete"]

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.delete()
        messages.success(self.request, "Успешное удаление")
        return redirect(success_url)
