from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import redirect
from django.views.generic import ListView, CreateView, DeleteView, UpdateView

from staff.mixins import PageTitleMixin, ModelPermissionMixin


class BaseStaffListView(
    PageTitleMixin,
    ModelPermissionMixin,
    LoginRequiredMixin,
    PermissionRequiredMixin,
    ListView,
):
    template_name = "staff/directory/lists_page.html"
    paginate_by = 20
    context_object_name = "objects"


class BaseStaffCreateView(
    PageTitleMixin, LoginRequiredMixin, PermissionRequiredMixin, CreateView
):
    template_name = "staff/directory/create_page.html"


class BaseStaffChangeView(
    PageTitleMixin, LoginRequiredMixin, PermissionRequiredMixin, UpdateView
):
    template_name = "staff/directory/update_page.html"


class BaseStaffDeleteView(
    PageTitleMixin, LoginRequiredMixin, PermissionRequiredMixin, DeleteView
):
    http_method_names = ["post", "delete"]

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.delete()
        messages.success(self.request, "Успешное удаление")
        return redirect(success_url)
