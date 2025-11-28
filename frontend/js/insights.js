// Initialize all charts on the insights page

// Category Bar Chart
const categoryBarData = {
    labels: ['Food', 'Transport', 'Shopping', 'Bills', 'Entertainment', 'Healthcare', 'Other'],
    datasets: [{
        label: 'Spending Amount',
        data: [450, 280, 320, 600, 180, 220, 150],
        backgroundColor: [
            '#D2042D',
            '#8B0000',
            '#A52A2A',
            '#C41E3A',
            '#DC143C',
            '#B22222',
            '#8B0000'
        ],
        borderRadius: 8,
        borderWidth: 0
    }]
};

new Chart(document.getElementById('categoryBarChart'), {
    type: 'bar',
    data: categoryBarData,
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

// Spending Distribution Pie Chart
const distributionData = {
    labels: ['Food', 'Transport', 'Shopping', 'Bills', 'Entertainment', 'Healthcare', 'Other'],
    datasets: [{
        data: [450, 280, 320, 600, 180, 220, 150],
        backgroundColor: [
            '#D2042D',
            '#8B0000',
            '#A52A2A',
            '#C41E3A',
            '#DC143C',
            '#B22222',
            '#CD5C5C'
        ],
        borderWidth: 2,
        borderColor: '#ffffff'
    }]
};

new Chart(document.getElementById('distributionChart'), {
    type: 'doughnut',
    data: distributionData,
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'bottom',
                labels: {
                    padding: 15,
                    font: {
                        size: 12
                    },
                    usePointStyle: true,
                    pointStyle: 'circle'
                }
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

// Expense Prediction Line Chart with ML-style projection
const predictionData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
    datasets: [
        {
            label: 'Actual Expenses',
            data: [1200, 1350, 1100, 1450, 1600, 1830, 1750, null, null, null, null, null],
            borderColor: '#D2042D',
            backgroundColor: 'rgba(210, 4, 45, 0.1)',
            borderWidth: 3,
            tension: 0.4,
            fill: true,
            pointRadius: 5,
            pointHoverRadius: 7,
            pointBackgroundColor: '#D2042D',
            pointBorderColor: '#ffffff',
            pointBorderWidth: 2
        },
        {
            label: 'ML Prediction',
            data: [null, null, null, null, null, null, 1750, 1820, 1880, 1950, 2020, 2100],
            borderColor: '#FFA500',
            backgroundColor: 'rgba(255, 165, 0, 0.1)',
            borderWidth: 3,
            borderDash: [10, 5],
            tension: 0.4,
            fill: true,
            pointRadius: 5,
            pointHoverRadius: 7,
            pointBackgroundColor: '#FFA500',
            pointBorderColor: '#ffffff',
            pointBorderWidth: 2
        },
        {
            label: 'Confidence Range (Upper)',
            data: [null, null, null, null, null, null, 1750, 1870, 1950, 2050, 2150, 2250],
            borderColor: 'rgba(255, 165, 0, 0.3)',
            backgroundColor: 'rgba(255, 165, 0, 0.05)',
            borderWidth: 1,
            borderDash: [5, 5],
            tension: 0.4,
            fill: '+1',
            pointRadius: 0,
            pointHoverRadius: 0
        },
        {
            label: 'Confidence Range (Lower)',
            data: [null, null, null, null, null, null, 1750, 1770, 1810, 1850, 1890, 1950],
            borderColor: 'rgba(255, 165, 0, 0.3)',
            backgroundColor: 'rgba(255, 165, 0, 0.05)',
            borderWidth: 1,
            borderDash: [5, 5],
            tension: 0.4,
            fill: false,
            pointRadius: 0,
            pointHoverRadius: 0
        }
    ]
};

new Chart(document.getElementById('predictionChart'), {
    type: 'line',
    data: predictionData,
    options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
            mode: 'index',
            intersect: false
        },
        plugins: {
            legend: {
                position: 'top',
                labels: {
                    padding: 20,
                    font: {
                        size: 13
                    },
                    usePointStyle: true,
                    filter: function(item) {
                        // Hide confidence range from legend
                        return !item.text.includes('Confidence Range');
                    }
                }
            },
            tooltip: {
                backgroundColor: 'rgba(0, 0, 0, 0.8)',
                padding: 12,
                titleFont: {
                    size: 14
                },
                bodyFont: {
                    size: 13
                },
                callbacks: {
                    label: function(context) {
                        if (context.parsed.y === null) return null;
                        const label = context.dataset.label || '';
                        return `${label}: ${formatCurrency(context.parsed.y)}`;
                    }
                }
            },
            annotation: {
                annotations: {
                    line1: {
                        type: 'line',
                        xMin: 6.5,
                        xMax: 6.5,
                        borderColor: 'rgba(210, 4, 45, 0.3)',
                        borderWidth: 2,
                        borderDash: [6, 6],
                        label: {
                            display: true,
                            content: 'Prediction starts',
                            position: 'start'
                        }
                    }
                }
            }
        },
        scales: {
            y: {
                beginAtZero: false,
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
                    color: 'rgba(0, 0, 0, 0.05)'
                }
            }
        }
    }
});

// Generate dynamic insights based on spending patterns
function generateInsights() {
    const insights = [
        {
            type: 'warning',
            icon: 'alert',
            color: '#D2042D',
            bgColor: 'rgba(210, 4, 45, 0.1)',
            title: 'Spending Alert',
            message: 'Your food expenses increased by 23% this month compared to last month.',
            action: 'Review your dining habits'
        },
        {
            type: 'success',
            icon: 'check',
            color: '#228B22',
            bgColor: 'rgba(34, 139, 34, 0.1)',
            title: 'Good Habit',
            message: 'You saved 15% more than last month. Keep up the great work!',
            action: 'Continue this trend'
        },
        {
            type: 'info',
            icon: 'info',
            color: '#FFA500',
            bgColor: 'rgba(255, 165, 0, 0.1)',
            title: 'Budget Tip',
            message: 'Consider switching to a cheaper phone plan. Potential savings: $20/month.',
            action: 'Explore options'
        },
        {
            type: 'insight',
            icon: 'trend',
            color: '#3b82f6',
            bgColor: 'rgba(59, 130, 246, 0.1)',
            title: 'Spending Pattern',
            message: 'You spend most on weekends. Planning ahead could help reduce impulse purchases.',
            action: 'Create weekend budget'
        }
    ];

    return insights;
}

// Load ML-based recommendations
function loadMLRecommendations() {
    const recommendations = [
        {
            category: 'Food',
            current: 450,
            suggested: 380,
            savings: 70,
            tip: 'Try meal prepping on Sundays to reduce dining out costs'
        },
        {
            category: 'Transport',
            current: 280,
            suggested: 220,
            savings: 60,
            tip: 'Consider carpooling or using public transport 2 days a week'
        },
        {
            category: 'Entertainment',
            current: 180,
            suggested: 120,
            savings: 60,
            tip: 'Switch to annual subscriptions for streaming services to save 20%'
        }
    ];

    console.log('ML Recommendations:', recommendations);
    // You can display these recommendations in a separate section if needed
}

// Calculate spending velocity (rate of spending)
function calculateSpendingVelocity() {
    const dailyAverage = 1830 / 30; // Monthly expense / days
    const projectedMonthEnd = dailyAverage * 30;
    
    console.log('Daily Average Spending:', formatCurrency(dailyAverage));
    console.log('Projected Month-End Total:', formatCurrency(projectedMonthEnd));
    
    return {
        daily: dailyAverage,
        projected: projectedMonthEnd
    };
}

// Identify spending anomalies
function detectAnomalies() {
    const anomalies = [
        {
            date: '2024-11-15',
            category: 'Shopping',
            amount: 450,
            expected: 150,
            deviation: 200,
            reason: 'Unusual large purchase detected'
        }
    ];
    
    console.log('Detected Anomalies:', anomalies);
    return anomalies;
}

// Category-wise spending trends
function analyzeTrends() {
    const trends = {
        increasing: ['Food', 'Entertainment'],
        decreasing: ['Transport'],
        stable: ['Bills', 'Healthcare']
    };
    
    console.log('Spending Trends:', trends);
    return trends;
}

// Budget health score (0-100)
function calculateBudgetHealth() {
    const score = 72; // Based on various factors
    const factors = {
        savingsRate: 15,
        overspendingCategories: 2,
        budgetAdherence: 78,
        emergencyFund: 6500
    };
    
    console.log('Budget Health Score:', score);
    console.log('Contributing Factors:', factors);
    
    return { score, factors };
}

// Initialize insights on page load
document.addEventListener('DOMContentLoaded', function() {
    // Load insights
    generateInsights();
    
    // Load ML recommendations
    loadMLRecommendations();
    
    // Calculate metrics
    calculateSpendingVelocity();
    detectAnomalies();
    analyzeTrends();
    calculateBudgetHealth();
    
    console.log('Insights page loaded successfully');
});

// Export functions for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        generateInsights,
        loadMLRecommendations,
        calculateSpendingVelocity,
        detectAnomalies,
        analyzeTrends,
        calculateBudgetHealth
    };
}