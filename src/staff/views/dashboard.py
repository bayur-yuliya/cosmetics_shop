from django.contrib.auth.decorators import permission_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from staff.services.dashboard_service import get_dashboard_context


@permission_required("staff.dashboard_view", raise_exception=False)
def index(request: HttpRequest) -> HttpResponse:
    context = get_dashboard_context()
    context["title"] = "Главная страница"
    return render(
        request,
        "staff/dashboard.html",
        context
    )
