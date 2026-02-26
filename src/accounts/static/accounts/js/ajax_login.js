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

function setupAjaxForm({ formId, errorId, errorMessage }) {
  const form = document.querySelector(`#${formId}`);
  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const formData = new FormData(form);
    const errorDiv = document.querySelector(`#${errorId}`);

    try {
      const response = await fetch(form.action, {
        method: "POST",
        body: formData,
        credentials: "same-origin",
        headers: {
          "X-Requested-With": "XMLHttpRequest",
          "X-CSRFToken": getCookie("csrftoken"),
        }
      });

      if (response.ok) {
        window.location.href = response.url;
        return;
      }

      if (response.status === 400 || response.status === 403) {
        errorDiv.innerText = errorMessage;
        errorDiv.classList.remove("d-none");
      }
    } catch (error) {
      console.error("Ошибка:", error);
    }
  });
}

setupAjaxForm({
  formId: "loginForm",
  errorId: "loginErrors",
  errorMessage: "Неверный email или пароль."
});

setupAjaxForm({
  formId: "registerForm",
  errorId: "registerErrors",
  errorMessage: "Ошибка регистрации. Проверьте данные."
});