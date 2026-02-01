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

    if (quantity > 1) {
        counter.textContent = quantity;
    // если раньше была выключена — включаем обратно
        if (removeBtn) {
            removeBtn.disabled = false;
            removeBtn.classList.remove("disabled");
        }
        } else {
            counter.textContent = 1;

            // делаем кнопку "-" неактивной
            if (removeBtn) {
                removeBtn.disabled = true;
                removeBtn.classList.add("disabled");
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

// Sorting panel
document.addEventListener("click", function (e) {
    const link = e.target.closest(".sorting-panel a");
    if (!link) return;

    e.preventDefault();

    const currentParams = new URLSearchParams(window.location.search);

    if (link.classList.contains("reset")) {
        currentParams.delete("sort");
        currentParams.delete("direction");
    } else {
        // обычная сортировка
        // перезаписываем только sort и direction
        const linkParams = new URLSearchParams(link.search);
        linkParams.forEach((value, key) => {
            if (key === "sort" || key === "direction") {
                currentParams.delete(key); // удаляем старое
                currentParams.append(key, value); // добавляем новое
            }
        });
    };

    fetch(`?${currentParams.toString()}`, {
        headers: {
            "X-Requested-With": "XMLHttpRequest",
        },
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById("products-container").innerHTML = data.html;
        // ОБНОВЛЕНИЕ ПАНЕЛИ СОРТИРОВКИ
        // Теперь кнопки получат новые ссылки (asc поменяется на desc)
        const sortingPanel = document.getElementById("sorting-panel-container");
        if (sortingPanel && data.sorting_html) {
            sortingPanel.innerHTML = data.sorting_html;
        }
        history.pushState(null, "", `?${currentParams.toString()}`);
    });
});

// Filter panel
document.addEventListener("submit", function (e) {
    if (e.target && e.target.id === "product-filter-form") {

        e.preventDefault();
        const form = e.target;

        // 1. текущие параметры из URL (там уже есть sort/direction)
        const params = new URLSearchParams(window.location.search);

        // 2. данные формы ПЕРЕЗАПИСЫВАЮТ фильтры
        const formData = new FormData(form);

        //удалить старые значения полей формы
        for (const key of new Set([...formData.keys()])) {
            params.delete(key);
        }
        formData.forEach((value, key) => {
            if (value === "") {
                params.delete(key);
            } else {
                params.append(key, value);
            }
        });

        // 3. сбрасываем страницу (важно)
        params.delete("page");

        fetch(`?${params.toString()}`, {
            headers: {
                "X-Requested-With": "XMLHttpRequest",
            },
        })
        .then(res => res.json())
        .then(data => {
            document.getElementById("products-container").innerHTML = data.html;
            if (data.url) {
                history.pushState(null, "", data.url);
            }
        });
    }
});
