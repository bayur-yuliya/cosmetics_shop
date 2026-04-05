import logging

from django.contrib import messages
from django.contrib.auth import login
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from accounts.forms import SetInitialPasswordForm
from accounts.utils.account_services import activate_user

logger = logging.getLogger(__name__)


def activate_account(request: HttpRequest) -> HttpResponse:
    token_value = request.GET.get("token")

    if not token_value:
        logger.warning("Attempting to open the activation page without a token")
        messages.error(request, "Не удалось получить токен")
        return redirect("main_page")

    if request.method == "POST":
        form = SetInitialPasswordForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data["password1"]

            user = activate_user(token=token_value, password=password)

            if user:
                login(
                    request, user, backend="django.contrib.auth.backends.ModelBackend"
                )
                messages.success(request, "Аккаунт успешно создан и активирован!")
                return redirect("main_page")
            else:
                messages.error(request, "Ссылка недействительна или просрочена.")

    else:
        form = SetInitialPasswordForm()

    return render(
        request,
        "accounts/activate_staff_password.html",
        {"title": "Активация приглашения", "form": form},
    )
