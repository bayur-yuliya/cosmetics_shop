from django.contrib import messages
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, redirect
from django.utils.http import url_has_allowed_host_and_scheme

from accounts.forms import SetInitialPasswordForm
from accounts.models import CustomUser
from accounts.utils.account_services import (
    activate_user_service,
    login_authenticated_user,
)


def login_view(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user: CustomUser | None = authenticate(
            request, username=email, password=password
        )

        next_url = request.GET.get("next")
        if next_url and url_has_allowed_host_and_scheme(
            next_url, allowed_hosts={request.get_host()}
        ):
            next_url_path = next_url
        else:
            next_url_path = "main_page"

        if user is not None:
            login(request, user)
            messages.success(request, "Вы вошли")
        else:
            messages.error(request, "Неверный email или пароль")
        return redirect(next_url_path)

    return redirect("main_page")


@login_required
def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect("main_page")


def activate_account(request: HttpRequest) -> HttpResponse:
    token_value: str | None = request.GET.get("token")
    if token_value is not None:
        if request.method == "POST":
            form = SetInitialPasswordForm(request.POST)
            if form.is_valid():
                password = form.cleaned_data["password1"]
                user = activate_user_service(request, token_value, password)
                login_authenticated_user(request, user, password)
    else:
        messages.error(request, "Не удалось получить токен")
    form = SetInitialPasswordForm()
    return render(
        request,
        "accounts/activate_staff_password.html",
        {
            "title": "Активация приглашения",
            "form": form,
        },
    )
