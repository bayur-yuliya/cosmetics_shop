import logging

from django.contrib import messages
from django.contrib.auth import login
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from accounts.forms import SetInitialPasswordForm

logger = logging.getLogger(__name__)


def activate_account(request: HttpRequest) -> HttpResponse:
    token_value: str | None = request.GET.get("token")

    if token_value is None:
        logger.warning("Activation without token")
        messages.error(request, "Не удалось получить токен")
        return redirect("main_page")

    logger.debug("Activation page opened")

    if request.method == "POST":
        form = SetInitialPasswordForm(request.POST, token=token_value)
        if form.is_valid():
            user, password = form.get_user_and_password()
            if user is not None:
                logger.info(f"User activated via view: user_id={user.id}")

                login(
                    request, user, backend="django.contrib.auth.backends.ModelBackend"
                )

                messages.success(request, "Аккаунт активирован!")
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
