const filterForm = document.getElementById('filter-form');

if (filterForm) {
    // 1. Очистка при отправке
    filterForm.addEventListener('submit', function () {
        const inputs = this.querySelectorAll('input, select');
        inputs.forEach(input => {
            if (!input.value || input.value.trim() === "") {
                input.disabled = true;
            }
        });
    });

    // 2. Функция для разблокировки всех полей
    const enableInputs = () => {
        const inputs = filterForm.querySelectorAll('input, select');
        inputs.forEach(input => {
            input.disabled = false;
        });
    };

    // 3. Разблокировка при загрузке и возврате (bfcache)
    window.addEventListener('pageshow', function (event) {
        enableInputs();
        setTimeout(enableInputs, 0);
    });
}