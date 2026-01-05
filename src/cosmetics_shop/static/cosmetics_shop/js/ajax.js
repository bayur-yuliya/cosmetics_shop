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
document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".favorite-btn").forEach(button => {
        // Удаляем старый обработчик событий и добавляем новый
        button.addEventListener("click", () => {
            const productId = button.dataset.productId;
            const isFavorite = button.dataset.inFavorites === "1";
            const url = isFavorite
                ? `/ajax/favorites/delete/${productId}/`
                : `/ajax/favorites/add/${productId}/`;

            fetch(url, {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCookie("csrftoken"),
                }
            })
            .then(res => res.json())
            .then(data => {
                if (data.in_favorites !== undefined) {
                    // Обновляем иконку и состояние
                    if (data.in_favorites) {
                        button.innerHTML = "♥";
                        button.dataset.inFavorites = "1";
                    } else {
                        button.innerHTML = "♡";
                        button.dataset.inFavorites = "0";
                    }
                }
            })
            .catch(error => {
                console.error("Ошибка:", error);
            });
        });
    });
});

document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".js-cart-btn").forEach(button => {
        button.addEventListener("click", () => {
            const productCode = button.dataset.productCode;

            fetch(`/ajax/cart/add/${productCode}/`, {
                method:"POST",
                headers: {
                    "X-CSRFToken": getCookie("csrftoken"),
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({})
            })
            .then(res => {
                if (!res.ok) {
                    throw new Error('Network response was not ok');
                }
                return res.json();
            })
            .then(data => {
                if (data.success) {
                    console.log('Обновляем счетчик значением:', data.count);
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

            fetch(`/ajax/cart/remove/${productCode}/`, {
                method:"POST",
                headers: {
                    "X-CSRFToken": getCookie("csrftoken"),
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({})
            })

            .then(res => {
                if (!res.ok) {
                    throw new Error('Network response was not ok');
                }
                return res.json();
            })
            .then(data => {
                if (data.success) {
                    console.log('Товар уменьшен в количестве в корзине');
                    console.log('Обновляем счетчик значением:', data.count);
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
// Модифицированная функция
function updateCartCounter(count) {
    console.log('Обновление счетчика:', count); // Для отладки

    // Способ 1: Если есть элемент с классом cart-counter
    const cartCounterElements = document.querySelectorAll('.cart-counter');
    cartCounterElements.forEach(element => {
        element.textContent = count > 0 ? `(${count})` : '';
    });

    // Способ 2: Ищем ссылку на корзину и обновляем её текст
    const cartLinks = document.querySelectorAll('a[href*="cart"]');
    cartLinks.forEach(link => {
        // Сохраняем базовый текст (без числа в скобках)
        const baseText = link.textContent.replace(/\(\d+\)/g, '').trim();
        link.textContent = count > 0 ?
            `${baseText} (${count})` :
            baseText;
    });

    // Способ 3: Если в шаблоне используется контекстный процессор
    const cartButtons = document.querySelectorAll('.nav-item a[href*="cart"]');
    cartButtons.forEach(button => {
        const baseHtml = button.innerHTML.replace(/\(\d+\)/g, '');
        button.innerHTML = count > 0 ?
            `${baseHtml.trim()} (${count})` :
            baseHtml.trim();
    });
}

function updateItemCounter(productCode, quantity) {
    const counter = document.querySelector(
        `.js-item-counter-quantity[data-product-code="${productCode}"]`
    );

    if (!counter) return;

    if (quantity > 0) {
        counter.textContent = quantity;
    } else {
        // если товара больше нет — можно скрыть строку
        const row = counter.closest("tr");
        if (row) row.remove();
    }
}

function updateTotalPrice(totalPrice) {
    const totalElement = document.getElementById("cart-total");
    if (!totalElement) return;

    totalElement.textContent = `Итого: ${totalPrice} грн`;
}


function showMessage(message) {
    if (!message) return;

    const container = document.getElementById("messages-container");

    const alert = document.createElement("div");
    alert.className = `alert alert-${message.level === "error" ? "danger" : "success"} alert-dismissible fade show`;
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
    const link = e.target.closest("a");
    if (!link) return;

    if  (link.closest(".sorting-panel")) {
        e.preventDefault();

        fetch(link.href, {
            headers: {
                "X-Requested-With": "XMLHttpRequest",
            },
        })
        .then(res => res.json())
        .then(data => {
            document.getElementById("products-container").innerHTML = data.html;
            history.pushState(null, "", link.href);
        });
    }
});

// Filter panel
document.querySelector("form").addEventListener("submit", function (e) {
    e.preventDefault();

    const form = this;
    const params = new URLSearchParams(new FormData(form));

    fetch(`?${params.toString()}`, {
        headers: {
            "X-Requested-With": "XMLHttpRequest",
        },
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById("products-container").innerHTML = data.html;
        history.pushState(null, "", `?${params.toString()}`);
    });
});
