from django.contrib import messages
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, redirect
from django.utils.http import url_has_allowed_host_and_scheme

from accounts.forms import SetInitialPasswordForm
from accounts.models import CustomUser


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
            form = SetInitialPasswordForm(request.POST, token=token_value)
            if form.is_valid():
                user, password = form.get_user_and_password()
                if user is not None:
                    login(request, user)
                    messages.success(request, "Аккаунт активирован!")
                    return redirect("main_page")
    else:
        messages.error(request, "Не удалось получить токен")
        return redirect("main_page")

    form = SetInitialPasswordForm()
    return render(
        request,
        "accounts/activate_staff_password.html",
        {
            "title": "Активация приглашения",
            "form": form,
        },
    )
