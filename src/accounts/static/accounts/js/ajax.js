function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.slice(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function setupAjaxForm({
  formId,
  buttonId,
  errorId,
  errorMessage,
  loadingText = "Загрузка...",
  defaultText
}) {
  const form = document.querySelector(`#${formId}`);
  if (!form) return;

  const button = document.querySelector(`#${buttonId}`);
  if (!button) return;

  const btnText = button.querySelector(".btn-text");
  const spinner = button.querySelector(".spinner-border");
  const errorDiv = document.querySelector(`#${errorId}`);

  // ─── Очистка ошибки при любом изменении в форме ───
  const inputs = form.querySelectorAll('input');
  inputs.forEach(input => {
    input.addEventListener('input', () => {
      if (!errorDiv.classList.contains('d-none')) {
        errorDiv.classList.add('d-none');
        errorDiv.innerText = '';
      }
    });
  });

  // ─── Проверка email на blur (только для регистрации) ───
  if (formId === "registerForm") {
    const emailInput = form.querySelector('input[name="email"]');
    if (emailInput) {
      emailInput.addEventListener("blur", async function () {
        const email = this.value.trim();
        if (!email) return;

        try {
          const res = await fetch(form.action, {   // ← важно: правильный адрес!
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "X-Requested-With": "XMLHttpRequest",
              "X-CSRFToken": getCookie("csrftoken"),
            },
            body: JSON.stringify({ email }),
          });

          const data = await res.json();

          if (data.exists) {
            errorDiv.innerText = "Пользователь с таким email уже существует.";
            errorDiv.classList.remove("d-none");
          } else {
            errorDiv.classList.add("d-none");
            errorDiv.innerText = "";
          }
        } catch (err) {
          console.error("Ошибка проверки email:", err);
        }
      });
    }
  }

  // ─── Обработка отправки формы ───
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (button.disabled) return;
    // Уже есть видимая ошибка → не отправляем
    if (!errorDiv.classList.contains("d-none")) {
      return;
    }

    // Блокировка интерфейса
    button.disabled = true;
    if (spinner) spinner.classList.remove("d-none");
    if (btnText) btnText.innerText = loadingText;
    errorDiv.classList.add("d-none");

    try {
    const response = await fetch(form.action, {
        method: "POST",
        body: new FormData(form),
        credentials: "same-origin",
        headers: {
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": getCookie("csrftoken"),
        },
    });

    button.disabled = true;
    let data;

    try {
        data = await response.json();  // ← один раз здесь
    } catch (jsonErr) {
        console.error("Не удалось распарсить JSON:", jsonErr);
        const text = await response.text();
        console.log("Сырой ответ:", text.substring(0, 500));
        errorDiv.innerText = "Сервер вернул неожиданный ответ. Попробуйте позже.";
        errorDiv.classList.remove("d-none");
        return;
    }

    if (response.ok) {
        window.location.href = data.redirect || response.url || window.location.href;
        return;
    }

    // ─── Теперь обрабатываем 400 ───
    if (response.status === 400) {
        let msg = errorMessage;

        // Текущий формат allauth: data.form.fields.<field>.errors
        if (data.form && data.form.fields) {
            const fields = data.form.fields;

            if (fields.email && fields.email.errors && fields.email.errors.length) {
                msg = fields.email.errors.join(" • ");
            } else if (fields.password1 && fields.password1.errors) {
                msg = fields.password1.errors.join(" • ");
            } else if (fields.password2 && fields.password2.errors) {
                msg = fields.password2.errors.join(" • ");
            } else {
                msg = "Ошибка в данных. Проверьте поля.";
            }
        } else if (data.non_field_errors) {
            msg = data.non_field_errors.join(" • ");
        }

        errorDiv.innerText = msg.trim() || errorMessage;
        errorDiv.classList.remove("d-none");
    }

} catch (err) {
    console.error("Ошибка при отправке:", err);
    errorDiv.innerText = "Ошибка соединения. Попробуйте позже.";
    errorDiv.classList.remove("d-none");
}finally {
      // Обязательно возвращаем всё в исходное состояние
      button.disabled = false;
      if (spinner) spinner.classList.add("d-none");
      if (btnText) btnText.innerText = defaultText;
    }
  });
}

setupAjaxForm({
  formId: "loginForm",
  buttonId: "loginButton",
  errorId: "loginErrors",
  errorMessage: "Неверный email или пароль.",
  loadingText: "Входим...",
  defaultText: "Войти",
});

setupAjaxForm({
  formId: "registerForm",
  buttonId: "registerButton",
  errorId: "registerErrors",
  errorMessage: "Ошибка регистрации. Проверьте данные.",
  loadingText: "Создаём аккаунт...",
  defaultText: "Зарегистрироваться",
});