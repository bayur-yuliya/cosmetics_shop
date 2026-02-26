function setupAjaxForm({
  formId,
  buttonId,
  errorId,
  loadingText,
  defaultText
}) {
  const form = document.querySelector(`#${formId}`);
  if (!form) return;

  const button = document.querySelector(`#${buttonId}`);
  const btnText = button.querySelector(".btn-text");
  const spinner = button.querySelector(".spinner-border");
  const errorDiv = document.querySelector(`#${errorId}`);
  const csrfToken = form.querySelector("[name=csrfmiddlewaretoken]").value;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    // блокировка кнопки
    button.disabled = true;
    spinner.classList.remove("d-none");
    btnText.innerText = loadingText;
    errorDiv.classList.add("d-none");

    try {
      const response = await fetch(form.action, {
        method: "POST",
        body: new FormData(form),
        credentials: "same-origin",
        headers: {
          "X-Requested-With": "XMLHttpRequest",
          "X-CSRFToken": csrfToken,
        }
      });

      if (response.ok) {
        window.location.reload();
        return;
      }

      errorDiv.innerText = "Ошибка регистрации. Проверьте введённые данные.";
      errorDiv.classList.remove("d-none");

    } catch (error) {
      errorDiv.innerText = "Ошибка сети.";
      errorDiv.classList.remove("d-none");
    }

    // возвращаем кнопку
    button.disabled = false;
    spinner.classList.add("d-none");
    btnText.innerText = defaultText;
  });
}

setupAjaxForm({
  formId: "loginForm",
  buttonId: "loginButton",
  errorId: "loginErrors",
  loadingText: "Входим...",
  defaultText: "Войти"
});

setupAjaxForm({
  formId: "registerForm",
  buttonId: "registerButton",
  errorId: "registerErrors",
  loadingText: "Создаём аккаунт...",
  defaultText: "Зарегистрироваться"
});