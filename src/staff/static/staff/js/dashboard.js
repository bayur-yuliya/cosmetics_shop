const ctx = document.getElementById('salesChart');
const avb = document.getElementById('averageBillChart');
let salesChart, avgChart;

async function loadChart(year) {
    const response = await fetch(`sales_data/?year=${year}`);
    const data = await response.json();

    const config = {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [{
                label: `Количество заказов за ${data.year}`,
                data: data.sales,
                borderWidth: 1,
                backgroundColor: 'rgba(54, 162, 235, 0.5)',
            }]
        },
        options: {
        scales: {
            y: {
                beginAtZero: true,
                ticks: {
                    stepSize: 1,
                    precision: 0,
                }
            }
        }
        }
    };
    const config_avb = {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [{
                label: `Количество заказов за ${data.year}`,
                data: data.average_bill,
                borderWidth: 1,
                backgroundColor: 'rgba(54, 162, 235, 0.5)',
            }]
        },
        options: {
        scales: {
            y: {
                beginAtZero: true,
            }
        }
        }
    };
    if (salesChart) salesChart.destroy();
    if (avgChart) avgChart.destroy();

    salesChart = new Chart(ctx, config);
    avgChart = new Chart(avb, config_avb);
}

document.getElementById('yearSelect').addEventListener('change', e => {
    loadChart(e.target.value);
});

loadChart(document.getElementById('yearSelect').value);