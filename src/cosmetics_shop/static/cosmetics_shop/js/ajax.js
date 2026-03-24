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

function disablePlusButton(productCode) {
    const row = document.querySelector(
        `.js-item-counter-quantity[data-product-code="${productCode}"]`
    )?.closest("tr");

    if (!row) return;

    const plusBtn = row.querySelector(
        `.js-cart-btn[data-product-code="${productCode}"]`
    );

    if (plusBtn) {
        plusBtn.disabled = true;
        plusBtn.classList.add("disabled");
    }
}

document.addEventListener("click", function (e) {
    const button = e.target.closest(".favorite-btn");
    if (!button) return;

    const productId = button.dataset.productId;
    const formData = new FormData();
    formData.append('product_id', productId);

    fetch(`/ajax/favorites/`, {
        method: "POST",
        headers: {
            "X-CSRFToken": getCookie("csrftoken"),
        },
        body: formData,
    })
    .then(res => res.json())
    .then(data => {

        // Обновляем иконку и состояние
        if (data.in_favorites) {
            button.classList.add("active");
        } else {
            button.classList.remove("active");
            showMessage(data.message);
        }

    })
    .catch(error => {
        console.error("Ошибка:", error);
    });
});

document.addEventListener("click", function (e) {
    const button = e.target.closest(".js-cart-btn-list");
    if (!button) return;

    const productCode = button.dataset.productCode;
    const formData = new FormData();
    formData.append("product_code", productCode);

    fetch(`/ajax/cart/add/`, {
        method: "POST",
        headers: {
            "X-CSRFToken": getCookie("csrftoken"),
        },
        body: formData,
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            button.textContent = "В корзине";
            button.classList.remove("btn-success");
            button.classList.add("btn-primary");
            button.disabled = true;
            button.classList.remove("js-cart-btn");

            updateCartCounter(data.count);
            updateItemCounter(data.product_code, data.product_count);
            updateItemTotal(data.product_code, data.product_total_price);
            updateTotalPrice(data.total_price);
            showMessage(data.message);
        }
    });
});

document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".js-cart-btn").forEach(button => {
        button.addEventListener("click", () => {
            const productCode = button.dataset.productCode;
            const formData = new FormData();
            formData.append("product_code", productCode);

            fetch(`/ajax/cart/add/`, {
                method:"POST",
                headers: {
                    "X-CSRFToken": getCookie("csrftoken"),
                },
                body: formData,
            })
            .then(res => {
                if (!res.ok) {
                    throw new Error('Network response was not ok');
                }
                return res.json();
            })
            .then(data => {
                if (data.success) {
                    updateCartCounter(data.count);
                    updateItemCounter(data.product_code, data.product_count);
                    updateItemTotal(data.product_code, data.product_total_price);
                    updateTotalPrice(data.total_price);
                    showMessage(data.message);

                    // блокируем кнопку "+"
                    if (data.is_max_quantity) {
                        disablePlusButton(data.product_code);
                    }
                }
            })
        });
    });
});


document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".js-cart-btn-remove").forEach(button => {
        button.addEventListener("click", () => {
            const productCode = button.dataset.productCode;
            const formData = new FormData();
            formData.append("product_code", productCode)

            fetch(`/ajax/cart/remove/`, {
                method:"POST",
                headers: {
                    "X-CSRFToken": getCookie("csrftoken"),
                },
                body: formData,
            })

            .then(res => {
                if (!res.ok) {
                    throw new Error('Network response was not ok');
                }
                return res.json();
            })
            .then(data => {
                if (data.success) {
                    updateItemCounter(data.product_code, data.product_count);
                    updateItemTotal(data.product_code, data.product_total_price);
                    updateCartCounter(data.count);
                    updateTotalPrice(data.total_price);
                } else {
                    console.error('Ошибка при удалении товара');
                }
            })
        });
    });
});

// Функция для показа уведомления (опционально)
function updateCartCounter(count) {
    // Если есть элемент с классом cart-counter
    const cartCounterElements = document.querySelectorAll('.cart-counter');
    cartCounterElements.forEach(element => {
        element.textContent = count > 0 ? `(${count})` : '';
    });
}

function updateItemCounter(productCode, quantity) {
    const counter = document.querySelector(
        `.js-item-counter-quantity[data-product-code="${productCode}"]`
    );

    if (!counter) return;

    const row = counter.closest("tr");

    const removeBtn = row?.querySelector(
        `.js-cart-btn-remove[data-product-code="${productCode}"]`
    );

    const plusBtn = row?.querySelector(
        `.js-cart-btn[data-product-code="${productCode}"]`
    );

    // --- ОБНОВЛЯЕМ ЧИСЛО ---
    counter.textContent = quantity;

    // --- ЛОГИКА "-" ---
    if (quantity > 1) {
        if (removeBtn) {
            removeBtn.disabled = false;
            removeBtn.classList.remove("disabled");
        }
    } else {
        if (removeBtn) {
            removeBtn.disabled = true;
            removeBtn.classList.add("disabled");
        }
    }

    // --- ЛОГИКА "+" ---
    const maxStock = parseInt(counter.dataset.maxStock);

    if (plusBtn) {
        if (quantity >= maxStock) {
            plusBtn.disabled = true;
            plusBtn.classList.add("disabled");
        } else {
            plusBtn.disabled = false;
            plusBtn.classList.remove("disabled");
        }
    }
}

function updateTotalPrice(totalPrice) {
    const totalElement = document.getElementById("cart-total");
    if (!totalElement) return;

    const formatted = new Intl.NumberFormat('uk-UA', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
    }).format(totalPrice);

    totalElement.textContent = `Итого: ${formatted} грн`;
}


function showMessage(message) {
    if (!message) return;

    const container = document.getElementById("messages-container");

    const alert = document.createElement("div");

    const level =
        message.level === "error" ? "danger" :
        message.level === "warning" ? "warning" :
        "success";

    alert.className = `alert alert-${level} alert-dismissible fade show`;
    alert.role = "alert";

    alert.innerHTML = `
        ${message.text}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    container.appendChild(alert);

    // автозакрытие
    setTimeout(() => {
        alert.classList.remove("show");
        alert.remove();
    }, 4000);
}

document.addEventListener("DOMContentLoaded", () => {
    djangoMessages.forEach(message => showMessage(message));
});


function updateItemQuantity(productCode, quantity) {
    const el = document.querySelector(
        `.js-item-counter-total[data-product-code="${productCode}"]`
    );
    if (!el) return;

    el.textContent = quantity;
}

function updateItemTotal(productCode, totalPrice) {
    const el = document.querySelector(
        `.js-item-counter-total[data-product-code="${productCode}"]`
    );
    if (!el) return;

    const price = parseFloat(totalPrice);

    el.textContent = new Intl.NumberFormat("uk-UA", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
    }).format(price) + " грн";
}

function updateContent(url) {
    fetch(url, {
        headers: {
            "X-Requested-With": "XMLHttpRequest",
        },
    })
    .then(res => res.json())
    .then(data => {
        // 1. Обновляем товары
        document.getElementById("products-container").innerHTML = data.html;

        // 2. Обновляем панель сортировки
        const sortingPanel = document.getElementById("sorting-panel-container");
        if (sortingPanel && data.sorting_html) {
            sortingPanel.innerHTML = data.sorting_html;
        }

        // 3. Обновляем URL
        history.pushState(null, "", data.url);
    })
    .catch(error => console.error('Error:', error));
}

// === ЛОГИКА СОРТИРОВКИ ===
document.addEventListener("click", function (e) {
    // Ищем клик внутри контейнера сортировки
    const link = e.target.closest("#sorting-panel-container a");
    if (!link) return;

    e.preventDefault();

    // 1. Берем текущие параметры страницы (чтобы сохранить фильтры: бренд, цена и т.д.)
    const currentParams = new URLSearchParams(window.location.search);

    // 2. Узнаем, что мы хотим изменить (сортировку) из ссылки, на которую нажали
    const linkUrl = new URL(link.href);
    const linkParams = linkUrl.searchParams;

    if (link.classList.contains("reset")) {
        // Если нажали "Сбросить" - удаляем сортировку, но оставляем фильтры
        currentParams.delete("sort");
        currentParams.delete("direction");
    } else {
        // Обновляем параметры сортировки
        if (linkParams.has("sort")) {
            currentParams.set("sort", linkParams.get("sort"));
        }
        if (linkParams.has("direction")) {
            currentParams.set("direction", linkParams.get("direction"));
        }
    }

    // Сбрасываем пагинацию при смене сортировки
    currentParams.delete("page");

    updateContent(`?${currentParams.toString()}`);
});

// === ЛОГИКА ФИЛЬТРАЦИИ ===
document.addEventListener("submit", function (e) {
    if (e.target && e.target.id === "product-filter-form") {
        e.preventDefault();
        const form = e.target;
        const formData = new FormData(form);

        // 1. Берем текущие параметры URL, чтобы сохранить СОРТИРОВКУ
        const currentParams = new URLSearchParams(window.location.search);
        const currentSort = currentParams.get("sort");
        const currentDirection = currentParams.get("direction");

        // 2. Создаем новые параметры чисто из формы
        const newParams = new URLSearchParams(formData);

        // 3. Возвращаем сортировку обратно (если она была)
        if (currentSort) newParams.set("sort", currentSort);
        if (currentDirection) newParams.set("direction", currentDirection);

        // 4. Очищаем пустые параметры (красоты ради)
        const keysToDelete = [];
        newParams.forEach((value, key) => {
            if (value === "" || value === null) {
                keysToDelete.push(key);
            }
        });
        keysToDelete.forEach(key => newParams.delete(key));

        // Сбрасываем пагинацию при фильтрации
        newParams.delete("page");

        updateContent(`?${newParams.toString()}`);
    }
});
