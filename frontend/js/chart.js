// Category Pie Chart
const categoryData = {
    labels: ['Food', 'Transport', 'Shopping', 'Bills', 'Entertainment'],
    datasets: [{
        data: [450, 280, 320, 600, 180],
        backgroundColor: [
            '#D2042D',
            '#8B0000',
            '#A52A2A',
            '#C41E3A',
            '#DC143C'
        ],
        borderWidth: 0
    }]
};

const categoryChart = new Chart(document.getElementById('categoryChart'), {
    type: 'doughnut',
    data: categoryData,
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: false
            }
        }
    }
});

// Create custom legend
const legendContainer = document.getElementById('categoryLegend');
categoryData.labels.forEach((label, index) => {
    const legendItem = document.createElement('div');
    legendItem.className = 'legend-item';
    legendItem.innerHTML = `
        <div class="legend-color" style="background-color: ${categoryData.datasets[0].backgroundColor[index]}"></div>
        <span class="legend-label">${label}</span>
    `;
    legendContainer.appendChild(legendItem);
});

// Monthly Expenses Bar Chart
const monthlyData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [{
        label: 'Monthly Expenses',
        data: [1200, 1350, 1100, 1450, 1600, 1830],
        backgroundColor: 'rgba(210, 4, 45, 0.8)',
        borderColor: '#D2042D',
        borderWidth: 2,
        borderRadius: 8
    }]
};

new Chart(document.getElementById('monthlyChart'), {
    type: 'bar',
    data: monthlyData,
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: false
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                ticks: {
                    callback: function(value) {
                        return '$' + value;
                    }
                }
            }
        }
    }
});

// Load recent transactions
async function loadRecentTransactions() {
    const response = await api.getExpenses();
    const transactionsList = document.getElementById('transactionsList');
    
    transactionsList.innerHTML = response.expenses.slice(0, 5).map(expense => `
        <div class="transaction-item">
            <div class="transaction-info">
                <h4>${expense.category}</h4>
                <p>${formatDate(expense.date)} • ${expense.paymentType}</p>
            </div>
            <div class="transaction-amount">-${formatCurrency(expense.amount)}</div>
        </div>
    `).join('');
}

// Load transactions on page load
loadRecentTransactions();