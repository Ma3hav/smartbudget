/**
 * SmartBudget Dashboard JavaScript
 * Handles all dashboard functionality including charts, stats, and real-time updates
 */

// Global chart instances
let categoryChart = null;
let monthlyChart = null;
let spendingTrendChart = null;

// Global state
const dashboardState = {
    isLoading: false,
    lastUpdate: null,
    currentPeriod: 'month', // month, week, year
    userData: null
};

/**
 * Initialize Dashboard
 */
async function initializeDashboard() {
    console.log('🚀 Initializing SmartBudget Dashboard...');
    
    // Get user data from localStorage
    dashboardState.userData = JSON.parse(localStorage.getItem('user') || '{}');
    
    // Display user greeting
    displayUserGreeting();
    
    // Load all dashboard data
    await loadAllDashboardData();
    
    // Setup event listeners
    setupEventListeners();
    
    // Setup auto-refresh
    setupAutoRefresh();
    
    console.log('✅ Dashboard initialized successfully');
}

/**
 * Display personalized user greeting
 */
function displayUserGreeting() {
    const userName = dashboardState.userData.name || 'User';
    const hour = new Date().getHours();
    let greeting = 'Good morning';
    
    if (hour >= 12 && hour < 17) greeting = 'Good afternoon';
    else if (hour >= 17) greeting = 'Good evening';
    
    // Add greeting to page title if element exists
    const pageTitle = document.querySelector('.page-title');
    if (pageTitle) {
        pageTitle.innerHTML = `${greeting}, ${userName.split(' ')[0]}! <span style="font-size: 0.6em; color: #666;">📊</span>`;
    }
}

/**
 * Load all dashboard data
 */
async function loadAllDashboardData() {
    if (dashboardState.isLoading) return;
    
    dashboardState.isLoading = true;
    showLoadingState();
    
    try {
        // Load data in parallel for better performance
        const [statsResult, expensesResult, categoriesResult] = await Promise.all([
            api.getDashboardStats(),
            api.getRecentExpenses(10),
            api.getCategories()
        ]);
        
        // Update summary cards
        if (statsResult.success) {
            updateSummaryCards(statsResult.stats);
            initializeCategoryChart(statsResult.stats.by_category || []);
        }
        
        // Load monthly trend
        await initializeMonthlyChart();
        
        // Load recent transactions
        if (expensesResult.success) {
            displayRecentTransactions(expensesResult.expenses);
        }
        
        // Check for alerts/anomalies
        await checkForAlerts();
        
        dashboardState.lastUpdate = new Date();
        hideLoadingState();
        
    } catch (error) {
        console.error('❌ Error loading dashboard data:', error);
        showErrorNotification('Failed to load dashboard data. Please refresh the page.');
        hideLoadingState();
    } finally {
        dashboardState.isLoading = false;
    }
}

/**
 * Update summary cards with real data
 */
function updateSummaryCards(stats) {
    const totalSpent = stats.total_spent || 0;
    const totalTransactions = stats.total_transactions || 0;
    const averageTransaction = stats.average_transaction || 0;
    
    // Get user budget from profile
    const monthlyBudget = dashboardState.userData.profile?.monthly_budget || 5000;
    const monthlyIncome = dashboardState.userData.profile?.monthly_income || 0;
    const remainingBudget = Math.max(0, monthlyBudget - totalSpent);
    
    // Calculate percentages
    const budgetUsedPercent = monthlyBudget > 0 ? (totalSpent / monthlyBudget * 100) : 0;
    const savingsPercent = monthlyIncome > 0 ? ((monthlyIncome - totalSpent) / monthlyIncome * 100) : 0;
    
    // Update Card 1: Total Balance / Monthly Income
    updateCard(1, {
        value: monthlyIncome > 0 ? monthlyIncome : 12450,
        change: `Available for ${getCurrentMonth()}`,
        changeClass: 'positive',
        icon: 'dollar'
    });
    
    // Update Card 2: Monthly Expenses
    updateCard(2, {
        value: totalSpent,
        change: `${budgetUsedPercent.toFixed(1)}% of budget used`,
        changeClass: budgetUsedPercent > 90 ? 'negative' : budgetUsedPercent > 75 ? 'warning' : 'positive',
        icon: 'trending-down'
    });
    
    // Update Card 3: Remaining Budget
    updateCard(3, {
        value: remainingBudget,
        change: budgetUsedPercent <= 100 ? 'On track' : 'Over budget!',
        changeClass: budgetUsedPercent <= 100 ? 'positive' : 'negative',
        icon: 'credit-card'
    });
    
    // Add transaction count info
    displayTransactionStats(totalTransactions, averageTransaction);
}

/**
 * Update individual summary card
 */
function updateCard(cardNumber, data) {
    const card = document.querySelector(`.summary-card:nth-child(${cardNumber})`);
    if (!card) return;
    
    const valueElement = card.querySelector('.card-value');
    const changeElement = card.querySelector('.card-change');
    
    if (valueElement) {
        // Animate value change
        animateValue(valueElement, data.value);
    }
    
    if (changeElement) {
        changeElement.textContent = data.change;
        changeElement.className = `card-change ${data.changeClass}`;
    }
}

/**
 * Animate number change
 */
function animateValue(element, targetValue) {
    const currentValue = parseFloat(element.textContent.replace(/[^0-9.-]+/g, '')) || 0;
    const duration = 1000; // 1 second
    const steps = 60;
    const stepValue = (targetValue - currentValue) / steps;
    const stepDuration = duration / steps;
    
    let currentStep = 0;
    
    const timer = setInterval(() => {
        currentStep++;
        const newValue = currentValue + (stepValue * currentStep);
        element.textContent = formatCurrency(newValue);
        
        if (currentStep >= steps) {
            clearInterval(timer);
            element.textContent = formatCurrency(targetValue);
        }
    }, stepDuration);
}

/**
 * Display transaction statistics
 */
function displayTransactionStats(count, average) {
    const statsContainer = document.querySelector('.transaction-stats');
    if (!statsContainer) {
        // Create stats container if it doesn't exist
        const summaryCards = document.querySelector('.summary-cards');
        if (summaryCards) {
            const statsDiv = document.createElement('div');
            statsDiv.className = 'transaction-stats';
            statsDiv.style.cssText = `
                grid-column: 1 / -1;
                display: flex;
                gap: 16px;
                padding: 16px;
                background: rgba(210, 4, 45, 0.05);
                border-radius: 12px;
                margin-top: -12px;
            `;
            statsDiv.innerHTML = `
                <div style="flex: 1; text-align: center;">
                    <p style="color: #666; font-size: 13px; margin-bottom: 4px;">Total Transactions</p>
                    <p style="color: #1a1a1a; font-size: 20px; font-weight: 700;">${count}</p>
                </div>
                <div style="flex: 1; text-align: center;">
                    <p style="color: #666; font-size: 13px; margin-bottom: 4px;">Average Transaction</p>
                    <p style="color: #1a1a1a; font-size: 20px; font-weight: 700;">${formatCurrency(average)}</p>
                </div>
                <div style="flex: 1; text-align: center;">
                    <p style="color: #666; font-size: 13px; margin-bottom: 4px;">This Month</p>
                    <p style="color: #D2042D; font-size: 20px; font-weight: 700;">${getCurrentMonth()}</p>
                </div>
            `;
            summaryCards.appendChild(statsDiv);
        }
    } else {
        // Update existing stats
        const values = statsContainer.querySelectorAll('p');
        if (values[1]) values[1].textContent = count;
        if (values[3]) values[3].textContent = formatCurrency(average);
    }
}

/**
 * Initialize Category Doughnut Chart
 */
function initializeCategoryChart(categoryData) {
    const canvas = document.getElementById('categoryChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // Destroy existing chart
    if (categoryChart) {
        categoryChart.destroy();
    }
    
    // Handle empty data
    if (!categoryData || categoryData.length === 0) {
        displayNoDataMessage(canvas, 'No expenses recorded yet');
        return;
    }
    
    // Prepare data
    const labels = categoryData.map(cat => cat.category);
    const data = categoryData.map(cat => cat.total);
    const percentages = categoryData.map(cat => cat.percentage || 0);
    
    // Color palette - shades of red
    const colors = [
        '#D2042D', // Cherry Red
        '#8B0000', // Dark Red
        '#A52A2A', // Brown Red
        '#C41E3A', // Cardinal Red
        '#DC143C', // Crimson
        '#B22222', // Fire Brick
        '#CD5C5C', // Indian Red
        '#8B0000', // Dark Red (repeat for more categories)
    ];
    
    // Create chart
    categoryChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors.slice(0, labels.length),
                borderWidth: 3,
                borderColor: '#ffffff',
                hoverOffset: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '65%',
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.9)',
                    padding: 12,
                    titleFont: {
                        size: 14,
                        weight: 'bold'
                    },
                    bodyFont: {
                        size: 13
                    },
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return [
                                `${label}`,
                                `Amount: ${formatCurrency(value)}`,
                                `Percentage: ${percentage}%`
                            ];
                        }
                    }
                }
            },
            animation: {
                animateRotate: true,
                animateScale: true,
                duration: 1000,
                easing: 'easeInOutQuart'
            }
        }
    });
    
    // Create custom legend
    createCustomLegend(labels, data, percentages, colors);
}

/**
 * Create custom legend for category chart
 */
function createCustomLegend(labels, data, percentages, colors) {
    const legendContainer = document.getElementById('categoryLegend');
    if (!legendContainer) return;
    
    legendContainer.innerHTML = '';
    
    const total = data.reduce((a, b) => a + b, 0);
    
    labels.forEach((label, index) => {
        const percentage = ((data[index] / total) * 100).toFixed(1);
        
        const legendItem = document.createElement('div');
        legendItem.className = 'legend-item';
        legendItem.style.cssText = `
            cursor: pointer;
            transition: all 0.3s;
        `;
        
        legendItem.innerHTML = `
            <div class="legend-color" style="background-color: ${colors[index]}; width: 16px; height: 16px; border-radius: 4px;"></div>
            <span class="legend-label" style="font-size: 13px; color: #333;">
                ${label}: <strong>${formatCurrency(data[index])}</strong> (${percentage}%)
            </span>
        `;
        
        // Add hover effect
        legendItem.addEventListener('mouseenter', function() {
            this.style.backgroundColor = '#f5f5f5';
            this.style.padding = '4px 8px';
            this.style.borderRadius = '6px';
            this.style.marginLeft = '-8px';
            this.style.marginRight = '-8px';
        });
        
        legendItem.addEventListener('mouseleave', function() {
            this.style.backgroundColor = 'transparent';
            this.style.padding = '0';
            this.style.marginLeft = '0';
            this.style.marginRight = '0';
        });
        
        legendContainer.appendChild(legendItem);
    });
}

/**
 * Initialize Monthly Expenses Bar Chart
 */
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
    
    if (monthlyData.data.every(val => val === 0)) {
        displayNoDataMessage(canvas, 'No monthly data available');
        return;
    }
    
    monthlyChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: monthlyData.labels,
            datasets: [{
                label: 'Monthly Expenses',
                data: monthlyData.data,
                backgroundColor: monthlyData.data.map((value, index) => {
                    // Different opacity for current month
                    const isCurrentMonth = index === monthlyData.data.length - 1;
                    return isCurrentMonth ? 'rgba(210, 4, 45, 1)' : 'rgba(210, 4, 45, 0.7)';
                }),
                borderColor: '#D2042D',
                borderWidth: 2,
                borderRadius: 8,
                borderSkipped: false,
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
                    backgroundColor: 'rgba(0, 0, 0, 0.9)',
                    padding: 12,
                    titleFont: {
                        size: 14,
                        weight: 'bold'
                    },
                    bodyFont: {
                        size: 13
                    },
                    callbacks: {
                        label: function(context) {
                            return `Expenses: ${formatCurrency(context.parsed.y)}`;
                        },
                        afterLabel: function(context) {
                            // Show comparison with previous month
                            const currentValue = context.parsed.y;
                            const previousValue = context.dataset.data[context.dataIndex - 1];
                            
                            if (previousValue && previousValue > 0) {
                                const change = ((currentValue - previousValue) / previousValue * 100).toFixed(1);
                                const arrow = change > 0 ? '↑' : '↓';
                                return `${arrow} ${Math.abs(change)}% vs last month`;
                            }
                            return '';
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '$' + value.toLocaleString();
                        },
                        font: {
                            size: 12
                        },
                        color: '#666'
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)',
                        drawBorder: false
                    }
                },
                x: {
                    ticks: {
                        font: {
                            size: 12,
                            weight: 'bold'
                        },
                        color: '#333'
                    },
                    grid: {
                        display: false,
                        drawBorder: false
                    }
                }
            },
            animation: {
                duration: 1000,
                easing: 'easeInOutQuart'
            }
        }
    });
}

/**
 * Get monthly expense data for the last 6 months
 */
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
        const endDate = new Date(date.getFullYear(), date.getMonth() + 1, 0, 23, 59, 59);
        
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
            console.error(`Error getting data for ${monthName}:`, error);
            data.push(0);
        }
    }
    
    return { labels: months, data: data };
}

/**
 * Display recent transactions
 */
function displayRecentTransactions(expenses) {
    const transactionsList = document.getElementById('transactionsList');
    
    if (!transactionsList) return;
    
    if (!expenses || expenses.length === 0) {
        transactionsList.innerHTML = `
            <div style="text-align: center; padding: 40px; color: #999;">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-bottom: 12px;">
                    <circle cx="12" cy="12" r="10"></circle>
                    <line x1="12" y1="8" x2="12" y2="12"></line>
                    <line x1="12" y1="16" x2="12.01" y2="16"></line>
                </svg>
                <p style="font-size: 16px; font-weight: 500;">No transactions yet</p>
                <p style="font-size: 14px; margin-top: 8px;">Start by adding your first expense!</p>
            </div>
        `;
        return;
    }
    
    transactionsList.innerHTML = expenses.map((expense, index) => {
        const fadeDelay = index * 50; // Stagger animation
        
        return `
            <div class="transaction-item" style="animation: fadeInUp 0.3s ease ${fadeDelay}ms both;">
                <div class="transaction-info">
                    <h4>${expense.category}</h4>
                    <p>${formatDate(expense.date)} • ${expense.payment_type}</p>
                    ${expense.notes ? `<p style="font-size: 12px; color: #999; margin-top: 4px;">${expense.notes}</p>` : ''}
                </div>
                <div class="transaction-amount">-${formatCurrency(expense.amount)}</div>
            </div>
        `;
    }).join('');
    
    // Add animation styles
    const style = document.createElement('style');
    style.textContent = `
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
    `;
    document.head.appendChild(style);
}

/**
 * Check for alerts and anomalies
 */
async function checkForAlerts() {
    try {
        const monthlyBudget = dashboardState.userData.profile?.monthly_budget;
        
        if (monthlyBudget) {
            const anomaliesResponse = await api.getAnomalies(monthlyBudget);
            
            if (anomaliesResponse.success) {
                displayAnomalyAlerts(anomaliesResponse.anomalies);
            }
        }
    } catch (error) {
        console.error('Error checking alerts:', error);
    }
}

/**
 * Display anomaly alerts
 */
function displayAnomalyAlerts(anomalies) {
    if (!anomalies || !anomalies.budget_status) return;
    
    const budgetStatus = anomalies.budget_status;
    
    if (budgetStatus.is_overrun_risk && budgetStatus.severity !== 'low') {
        showWarningBanner(budgetStatus.message, budgetStatus.severity);
    }
    
    // Display amount anomalies
    if (anomalies.amount_anomalies && anomalies.amount_anomalies.length > 0) {
        anomalies.amount_anomalies.forEach(anomaly => {
            if (anomaly.severity === 'high') {
                showWarningBanner(anomaly.message, 'medium');
            }
        });
    }
}

/**
 * Show warning banner
 */
function showWarningBanner(message, severity) {
    const banner = document.createElement('div');
    banner.className = `alert-banner alert-${severity}`;
    banner.style.cssText = `
        position: fixed;
        top: 80px;
        left: 50%;
        transform: translateX(-50%);
        padding: 16px 24px;
        background: ${severity === 'high' ? '#D2042D' : '#FFA500'};
        color: white;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 1000;
        max-width: 600px;
        display: flex;
        align-items: center;
        gap: 12px;
        animation: slideDown 0.3s ease;
    `;
    
    banner.innerHTML = `
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="8" x2="12" y2="12"></line>
            <line x1="12" y1="16" x2="12.01" y2="16"></line>
        </svg>
        <span>${message}</span>
        <button onclick="this.parentElement.remove()" style="margin-left: auto; background: none; border: none; color: white; cursor: pointer; font-size: 20px;">×</button>
    `;
    
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideDown {
            from {
                transform: translateX(-50%) translateY(-100%);
                opacity: 0;
            }
            to {
                transform: translateX(-50%) translateY(0);
                opacity: 1;
            }
        }
    `;
    document.head.appendChild(style);
    
    document.body.appendChild(banner);
    
    // Auto-remove after 10 seconds
    setTimeout(() => {
        banner.style.animation = 'slideDown 0.3s ease reverse';
        setTimeout(() => banner.remove(), 300);
    }, 10000);
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Refresh button (if exists)
    const refreshBtn = document.getElementById('refreshDashboard');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', async () => {
            await loadAllDashboardData();
            showSuccessNotification('Dashboard refreshed!');
        });
    }
    
    // Period selector (if exists)
    const periodSelector = document.getElementById('periodSelector');
    if (periodSelector) {
        periodSelector.addEventListener('change', async (e) => {
            dashboardState.currentPeriod = e.target.value;
            await loadAllDashboardData();
        });
    }
}

/**
 * Setup auto-refresh
 */
function setupAutoRefresh() {
    // Refresh dashboard every 5 minutes
    setInterval(() => {
        if (!dashboardState.isLoading) {
            loadAllDashboardData();
            console.log('📊 Dashboard auto-refreshed');
        }
    }, 5 * 60 * 1000);
}

/**
 * Helper Functions
 */

function getCurrentMonth() {
    return new Date().toLocaleString('default', { month: 'long', year: 'numeric' });
}

function showLoadingState() {
    const loadingOverlay = document.createElement('div');
    loadingOverlay.id = 'dashboardLoading';
    loadingOverlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(255, 255, 255, 0.8);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 9999;
    `;
    loadingOverlay.innerHTML = `
        <div style="text-align: center;">
            <div style="width: 48px; height: 48px; border: 4px solid #f3f3f3; border-top: 4px solid #D2042D; border-radius: 50%; animation: spin 1s linear infinite;"></div>
            <p style="margin-top: 16px; color: #666; font-weight: 500;">Loading dashboard...</p>
        </div>
    `;
    
    const style = document.createElement('style');
    style.textContent = `
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    `;
    document.head.appendChild(style);
    
    document.body.appendChild(loadingOverlay);
}

function hideLoadingState() {
    const loadingOverlay = document.getElementById('dashboardLoading');
    if (loadingOverlay) {
        loadingOverlay.remove();
    }
}

function displayNoDataMessage(canvas, message) {
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.font = '14px Inter, sans-serif';
    ctx.fillStyle = '#999';
    ctx.textAlign = 'center';
    ctx.fillText(message, canvas.width / 2, canvas.height / 2);
}

function showSuccessNotification(message) {
    showNotification(message, 'success');
}

function showErrorNotification(message) {
    showNotification(message, 'error');
}

function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 16px 24px;
        background: ${type === 'success' ? '#22c55e' : '#D2042D'};
        color: white;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 10000;
        animation: slideIn 0.3s ease;
        max-width: 400px;
    `;
    notification.textContent = message;
    
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from {
                transform: translateX(400px);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
    `;
    document.head.appendChild(style);
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideIn 0.3s ease reverse';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

/**
 * Initialize dashboard when DOM is ready
 */
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeDashboard);
} else {
    initializeDashboard();
}

// Export functions for external use
if (typeof window !== 'undefined') {
    window.dashboardRefresh = loadAllDashboardData;
    window.dashboardState = dashboardState;
}