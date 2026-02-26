from django.contrib import messages
from django.contrib.auth import login
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, redirect

from accounts.forms import SetInitialPasswordForm


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
