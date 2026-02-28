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
    apiUrl,
    buttonId,
    errorId,
    errorMessage,
    loadingText,
    defaultText
}) {
    const form = document.querySelector(`#${formId}`);
    if (!form) return;

    const button = document.querySelector(`#${buttonId}`);
    const errorDiv = document.querySelector(`#${errorId}`);

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        // Сброс состояния
        button.disabled = true;
        errorDiv.classList.add("d-none");
        errorDiv.innerText = "";

        const formData = new FormData(form);
        const jsonData = Object.fromEntries(formData.entries());

        try {
            const response = await fetch(apiUrl, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken"),
                    "X-Requested-With": "XMLHttpRequest",
                },
                body: JSON.stringify(jsonData),
            });

            const data = await response.json();

            if (response.ok) {
                // Успех -> Редирект
                window.location.href = data.meta?.redirect_url || '/';
                return;
            }

            const errorTranslations = {
                "password_too_short": "Пароль слишком короткий (минимум 8 символов).",
                "email_taken": "Этот email уже занят.",
                "required": "Это поле обязательно для заполнения.",
                "password_entirely_numeric": "Пароль не может состоять только из цифр.",
                "This password is too short. It must contain at least 8 characters.": "Пароль слишком короткий (минимум 8 знаков)."
            };

            // ОБРАБОТКА ОШИБОК
            if (data.errors) {
                let errorMsgs = data.errors.map(err => {
                    if (err.param === 'email' && err.code === 'email_taken') {
                        return "Этот email уже зарегистрирован.";
                    }
                    // 1. Пытаемся найти перевод по коду (code)
                    if (errorTranslations[err.code]) {
                        return errorTranslations[err.code];
                    }
                    // 2. Если по коду не нашли, пытаемся найти по тексту сообщения
                    if (errorTranslations[err.message]) {
                        return errorTranslations[err.message];
                    }
                    // 3. Если перевода нет, оставляем как есть
                    return err.message;
                });
                // Показываем первую ошибку
                errorDiv.innerText = errorMsgs[0];
                errorDiv.classList.remove("d-none");
            } else {
                errorDiv.innerText = errorMessage;
                errorDiv.classList.remove("d-none");
            }

        } catch (err) {
            errorDiv.innerText = "Ошибка сети. Попробуйте позже.";
            errorDiv.classList.remove("d-none");
        } finally {
            button.disabled = false;
        }
    });
}

// Инициализация
setupAjaxForm({
    formId: "loginForm",
    apiUrl: "/_allauth/browser/v1/auth/login", // Официальный API-эндпоинт
    buttonId: "loginButton",
    errorId: "loginErrors",
    errorMessage: "Неверный email или пароль.",
    loadingText: "Входим...",
    defaultText: "Войти",
});

setupAjaxForm({
    formId: "registerForm",
    apiUrl: "/_allauth/browser/v1/auth/signup", // Официальный API-эндпоинт
    buttonId: "registerButton",
    errorId: "registerErrors",
    errorMessage: "Ошибка регистрации. Проверьте данные.",
    loadingText: "Создаём аккаунт...",
    defaultText: "Зарегистрироваться",
});