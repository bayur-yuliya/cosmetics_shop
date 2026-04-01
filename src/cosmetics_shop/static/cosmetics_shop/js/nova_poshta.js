document.addEventListener('DOMContentLoaded', function () {
    const cityInput = document.querySelector('.np-city-input');
    const warehouseSelect = document.querySelector('.np-warehouse-select');

    if (!cityInput || !warehouseSelect) return;

    const DEFAULT_OPTION = '<option value="" selected disabled>Выберите отделение</option>';
    const LOADING_OPTION = '<option value="" selected disabled>Загрузка отделений...</option>';
    const ERROR_OPTION = '<option value="" selected disabled>Отделения не найдены</option>';

    const savedOffice = "{{ form_delivery.initial.post_office|default:'' }}";
    let isSelectingFromList = false; // Флаг, чтобы избежать двойных запросов при клике

    function setSelectState(state) {
        switch (state) {
            case 'default':
                warehouseSelect.innerHTML = DEFAULT_OPTION;
                warehouseSelect.disabled = true;
                break;
            case 'loading':
                warehouseSelect.innerHTML = LOADING_OPTION;
                warehouseSelect.disabled = true;
                break;
            case 'error':
                warehouseSelect.innerHTML = ERROR_OPTION;
                warehouseSelect.disabled = true;
                break;
            case 'enabled':
                warehouseSelect.disabled = false;
                break;
        }
    }

    function loadWarehouses(cityRef, selectedOffice = null) {
        if (!cityRef) {
            setSelectState('default');
            return;
        }

        setSelectState('loading');

        fetch(`/api/np/warehouses/?city_ref=${cityRef}`)
            .then(response => response.json())
            .then(res => {
                if (!res.data || res.data.length === 0) {
                    setSelectState('error');
                    return;
                }

                // Сначала подготавливаем HTML, потом вставляем одним махом (убирает мерцание)
                let options = DEFAULT_OPTION;
                res.data.forEach(wh => {
                    const isSelected = wh.Description === selectedOffice ? 'selected' : '';
                    options += `<option value="${wh.Description}" ${isSelected}>${wh.Description}</option>`;
                });

                warehouseSelect.innerHTML = options;
                setSelectState('enabled');
            })
            .catch(() => {
                setSelectState('default');
            });
    }

    function findCityAndLoadWarehouses(cityName, selectedOffice = null) {
        if (!cityName) {
            setSelectState('default');
            return;
        }

        fetch(`/api/np/cities/?q=${encodeURIComponent(cityName)}`)
            .then(response => response.json())
            .then(res => {
                const city = res.data.find(c => c.Description.toLowerCase() === cityName.toLowerCase());

                if (!city) {
                    setSelectState('default');
                    return;
                }

                loadWarehouses(city.Ref, selectedOffice);
            })
            .catch(() => setSelectState('default'));
    }

    const resultsContainer = document.createElement('div');
    resultsContainer.className = 'list-group position-absolute w-100';
    resultsContainer.style.zIndex = '1000';

    cityInput.parentNode.style.position = 'relative';
    cityInput.parentNode.appendChild(resultsContainer);

    let debounceTimer = null;

    cityInput.addEventListener('input', function () {
        const query = this.value.trim();
        clearTimeout(debounceTimer);

        if (query.length < 2) {
            resultsContainer.innerHTML = '';
            return;
        }

        debounceTimer = setTimeout(() => {
            fetch(`/api/np/cities/?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(res => {
                    resultsContainer.innerHTML = '';
                    res.data.forEach(city => {
                        const btn = document.createElement('button');
                        btn.className = 'list-group-item list-group-item-action';
                        btn.textContent = city.Description;
                        btn.type = 'button';

                        btn.onmousedown = () => { // Используем mousedown, чтобы сработало раньше blur
                            isSelectingFromList = true;
                            cityInput.value = city.Description;
                            resultsContainer.innerHTML = '';
                            loadWarehouses(city.Ref);
                            setTimeout(() => { isSelectingFromList = false; }, 100);
                        };

                        resultsContainer.appendChild(btn);
                    });
                });
        }, 300);
    });

    // Скрываем список при клике вне поля
    document.addEventListener('click', (e) => {
        if (e.target !== cityInput) resultsContainer.innerHTML = '';
    });

    function handleCityChange() {
        if (isSelectingFromList) return;

        const cityName = cityInput.value.trim();
        if (!cityName) {
            setSelectState('default');
        } else {
            findCityAndLoadWarehouses(cityName);
        }
    }

    // 'change' сработает при потере фокуса, если текст изменился
    cityInput.addEventListener('change', handleCityChange);

    cityInput.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            this.blur(); // Спровоцирует событие change
        }
    });

    // Сразу ставим дефолтное состояние
    setSelectState('default');

    const initialCity = cityInput.value.trim();
    if (initialCity) {
        findCityAndLoadWarehouses(initialCity, savedOffice);
    }
});