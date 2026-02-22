const ctx = document.getElementById('salesChart');
const avb = document.getElementById('averageBillChart');
let salesChart, avgChart;

// Функция инициализации пустых графиков
function initCharts() {
    const commonOptions = {
        responsive: true,
        maintainAspectRatio: false,
        scales: { y: { beginAtZero: true } }
    };

    salesChart = new Chart(ctx, {
        type: 'bar',
        data: { labels: [], datasets: [{ label: 'Загрузка...', data: [], backgroundColor: 'rgba(54, 162, 235, 0.5)' }] },
        options: commonOptions
    });

    avgChart = new Chart(avb, {
        type: 'bar',
        data: { labels: [], datasets: [{ label: 'Загрузка...', data: [], backgroundColor: 'rgba(75, 192, 192, 0.5)' }] },
        options: {
            ...commonOptions,
            scales: {
                y: {
                    ticks: { callback: value => value + ' грн' }
                }
            }
        }
    });
}

async function loadChart(year) {
    try {
        const response = await fetch(`/staff/ajax/charts/sales/?year=${year}`);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

        const data = await response.json();

        // Обновляем данные первого графика
        salesChart.data.labels = data.labels;
        salesChart.data.datasets[0].data = data.sales;
        salesChart.data.datasets[0].label = `Количество заказов за ${data.year}`;

        // Обновляем данные второго графика
        avgChart.data.labels = data.labels;
        avgChart.data.datasets[0].data = data.average_bill;
        avgChart.data.datasets[0].label = `Средний чек за ${data.year} (грн)`;

        // Вызываем обновление с анимацией
        salesChart.update();
        avgChart.update();

    } catch (error) {
        console.error('Error updating chart:', error);
    }
}

// Запуск при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    initCharts(); // Создаем пустые объекты
    const yearSelect = document.getElementById('yearSelect');

    // Сразу загружаем данные для выбранного года
    loadChart(yearSelect.value);

    yearSelect.addEventListener('change', (e) => loadChart(e.target.value));
});