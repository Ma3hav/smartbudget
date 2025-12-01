// Global chart instances
let categoryChart = null;
let monthlyChart = null;

// Load dashboard data and initialize charts
async function loadDashboardData() {
    try {
        // Get statistics
        const statsResponse = await api.getDashboardStats();
        
        if (!statsResponse.success) {
            throw new Error('Failed to load statistics');
        }
        
        const stats = statsResponse.stats;
        
        // Update summary cards
        updateSummaryCards(stats);
        
        // Initialize charts with real data
        initializeCategoryChart(stats.by_category || []);
        initializeMonthlyChart();
        
        // Load recent transactions
        await loadRecentTransactions();
        
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        showError('Failed to load dashboard data');
    }
}

// Update summary cards with real data
function updateSummaryCards(stats) {
    // Calculate values
    const totalSpent = stats.total_spent || 0;
    const totalTransactions = stats.total_transactions || 0;
    
    // Update Total Balance (you might want to get this from user profile)
    const balanceCard = document.querySelector('.summary-card:nth-child(1) .card-value');
    if (balanceCard) {
        // This should come from user profile - using placeholder
        balanceCard.textContent = formatCurrency(12450);
    }
    
    // Update Monthly Expenses
    const expenseCard = document.querySelector('.summary-card:nth-child(2) .card-value');
    if (expenseCard) {
        expenseCard.textContent = formatCurrency(totalSpent);
    }
    
    // Update Remaining Budget
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    const monthlyBudget = user.profile?.monthly_budget || 5000;
    const remainingBudget = monthlyBudget - totalSpent;
    
    const budgetCard = document.querySelector('.summary-card:nth-child(3) .card-value');
    if (budgetCard) {
        budgetCard.textContent = formatCurrency(Math.max(0, remainingBudget));
    }
    
    // Update percentage change indicators
    const changeSpan = document.querySelector('.summary-card:nth-child(2) .card-change');
    if (changeSpan) {
        const percentSpent = (totalSpent / monthlyBudget) * 100;
        changeSpan.textContent = `${percentSpent.toFixed(1)}% of budget used`;
        changeSpan.className = percentSpent > 90 ? 'card-change negative' : 'card-change positive';
    }
}

// Initialize Category Pie Chart
function initializeCategoryChart(categoryData) {
    const canvas = document.getElementById('categoryChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // Destroy existing chart
    if (categoryChart) {
        categoryChart.destroy();
    }
    
    // Prepare data
    const labels = categoryData.map(cat => cat.category);
    const data = categoryData.map(cat => cat.total);
    const colors = [
        '#D2042D', '#8B0000', '#A52A2A', '#C41E3A', 
        '#DC143C', '#B22222', '#CD5C5C'
    ];
    
    // Create chart
    categoryChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors.slice(0, labels.length),
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${label}: ${formatCurrency(value)} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
    
    // Create custom legend
    createCustomLegend(labels, data, colors);
}

// Create custom legend for category chart
function createCustomLegend(labels, data, colors) {
    const legendContainer = document.getElementById('categoryLegend');
    if (!legendContainer) return;
    
    legendContainer.innerHTML = '';
    
    labels.forEach((label, index) => {
        const legendItem = document.createElement('div');
        legendItem.className = 'legend-item';
        legendItem.innerHTML = `
            <div class="legend-color" style="background-color: ${colors[index]}"></div>
            <span class="legend-label">${label}: ${formatCurrency(data[index])}</span>
        `;
        legendContainer.appendChild(legendItem);
    });
}

// Initialize Monthly Expenses Bar Chart
async function initializeMonthlyChart() {
    const canvas = document.getElementById('monthlyChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // Destroy existing chart
    if (monthlyChart) {
        monthlyChart.destroy();
    }
    
    // Get last 6 months of data
    const monthlyData = await getMonthlyExpenseData();
    
    monthlyChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: monthlyData.labels,
            datasets: [{
                label: 'Monthly Expenses',
                data: monthlyData.data,
                backgroundColor: 'rgba(210, 4, 45, 0.8)',
                borderColor: '#D2042D',
                borderWidth: 2,
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return formatCurrency(context.parsed.y);
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '$' + value;
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

// Get monthly expense data for the last 6 months
async function getMonthlyExpenseData() {
    const months = [];
    const data = [];
    const now = new Date();
    
    // Generate last 6 months
    for (let i = 5; i >= 0; i--) {
        const date = new Date(now.getFullYear(), now.getMonth() - i, 1);
        const monthName = date.toLocaleString('default', { month: 'short' });
        months.push(monthName);
        
        // Get stats for this month
        const startDate = new Date(date.getFullYear(), date.getMonth(), 1);
        const endDate = new Date(date.getFullYear(), date.getMonth() + 1, 0);
        
        try {
            const response = await api.getDashboardStats(
                startDate.toISOString(),
                endDate.toISOString()
            );
            
            if (response.success) {
                data.push(response.stats.total_spent || 0);
            } else {
                data.push(0);
            }
        } catch (error) {
            console.error('Error getting monthly data:', error);
            data.push(0);
        }
    }
    
    return { labels: months, data: data };
}

// Load recent transactions
async function loadRecentTransactions() {
    try {
        const response = await api.getRecentExpenses(5);
        const transactionsList = document.getElementById('transactionsList');
        
        if (!transactionsList) return;
        
        if (!response.success || response.expenses.length === 0) {
            transactionsList.innerHTML = '<p style="text-align: center; color: #999; padding: 20px;">No recent transactions</p>';
            return;
        }
        
        transactionsList.innerHTML = response.expenses.map(expense => `
            <div class="transaction-item">
                <div class="transaction-info">
                    <h4>${expense.category}</h4>
                    <p>${formatDate(expense.date)} • ${expense.payment_type}</p>
                </div>
                <div class="transaction-amount">-${formatCurrency(expense.amount)}</div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading transactions:', error);
        const transactionsList = document.getElementById('transactionsList');
        if (transactionsList) {
            transactionsList.innerHTML = '<p style="text-align: center; color: #D2042D; padding: 20px;">Failed to load transactions</p>';
        }
    }
}

// Show error message
function showError(message) {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 16px 24px;
        background: #D2042D;
        color: white;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 10000;
    `;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => notification.remove(), 3000);
}

// Initialize dashboard when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', loadDashboardData);
} else {
    loadDashboardData();
}

// Refresh dashboard every 5 minutes
setInterval(loadDashboardData, 5 * 60 * 1000);