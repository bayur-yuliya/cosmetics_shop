document.addEventListener('DOMContentLoaded', function() {
    const cityInput = document.querySelector('.np-city-input');
    const warehouseSelect = document.querySelector('.np-warehouse-select');

    // Создаем контейнер для выпадающего списка городов
    const resultsContainer = document.createElement('div');
    resultsContainer.className = 'list-group position-absolute';
    resultsContainer.style.zIndex = '1000';
    cityInput.parentNode.appendChild(resultsContainer);

    // 1. Поиск города
    cityInput.addEventListener('input', function() {
        const query = this.value;
        if (query.length < 2) {
            resultsContainer.innerHTML = '';
            return;
        }

        fetch(`/api/np/cities/?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(res => {
                const cities = res.data;
                resultsContainer.innerHTML = '';

                cities.forEach(city => {
                    const btn = document.createElement('button');
                    btn.className = 'list-group-item list-group-item-action';
                    // В украинском API название города в поле 'Description'
                    btn.textContent = city.Description;
                    btn.type = 'button';

                    btn.onclick = () => {
                        cityInput.value = city.Description;
                        resultsContainer.innerHTML = '';
                        // Загружаем отделения для выбранного города
                        loadWarehouses(city.Ref);
                    };
                    resultsContainer.appendChild(btn);
                });
            });
    });

    // 2. Загрузка отделений
    function loadWarehouses(cityRef) {
        warehouseSelect.innerHTML = '<option>Загрузка...</option>';

        fetch(`/api/np/warehouses/?city_ref=${cityRef}`)
            .then(response => response.json())
            .then(res => {
                const warehouses = res.data;
                warehouseSelect.innerHTML = '<option value="">Выберите отделение</option>';

                warehouses.forEach(wh => {
                    const option = document.createElement('option');
                    option.value = wh.Description; // Сохраняем название текстом
                    option.textContent = wh.Description;
                    warehouseSelect.appendChild(option);
                });
            });
    }
});