// API Configuration
const API_BASE_URL = "http://127.0.0.1:5000/api";

// Get auth token from localStorage
function getAuthToken() {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    return user.access_token || null;
}

// API Request Helper
async function apiRequest(endpoint, options = {}) {
    const token = getAuthToken();
    
    const defaultHeaders = {
        'Content-Type': 'application/json',
    };
    
    if (token) {
        defaultHeaders['Authorization'] = `Bearer ${token}`;
    }
    
    const config = {
        ...options,
        headers: {
            ...defaultHeaders,
            ...options.headers
        }
    };
    
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
        const data = await response.json();
        
        // Handle unauthorized
        if (response.status === 401) {
            localStorage.removeItem('user');
            window.location.href = 'index.html';
            throw new Error('Unauthorized');
        }
        
        if (!response.ok) {
            throw new Error(data.error || 'Request failed');
        }
        
        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// API Functions
const api = {
    // Authentication
    login: async (email, password) => {
        try {
            const data = await apiRequest('/auth/login', {
                method: 'POST',
                body: JSON.stringify({ email, password })
            });
            
            // Store user with tokens
            localStorage.setItem('user', JSON.stringify({
                ...data.user,
                access_token: data.access_token,
                refresh_token: data.refresh_token
            }));
            
            return { success: true, user: data.user };
        } catch (error) {
            return { success: false, message: error.message };
        }
    },

    signup: async (name, email, password) => {
        try {
            const data = await apiRequest('/auth/register', {
                method: 'POST',
                body: JSON.stringify({ name, email, password })
            });
            
            // Store user with tokens
            localStorage.setItem('user', JSON.stringify({
                ...data.user,
                access_token: data.access_token,
                refresh_token: data.refresh_token
            }));
            
            return { success: true, user: data.user };
        } catch (error) {
            return { success: false, message: error.message };
        }
    },
    
    getCurrentUser: async () => {
        try {
            const data = await apiRequest('/auth/me');
            return { success: true, user: data.user };
        } catch (error) {
            return { success: false, message: error.message };
        }
    },

    // Expenses
    getExpenses: async (filters = {}) => {
        try {
            const params = new URLSearchParams(filters).toString();
            const endpoint = params ? `/expenses/?${params}` : '/expenses/';
            const data = await apiRequest(endpoint);
            return { success: true, expenses: data.expenses, pagination: data.pagination };
        } catch (error) {
            return { success: false, expenses: [], message: error.message };
        }
    },
    
    getRecentExpenses: async (limit = 10) => {
        try {
            const data = await apiRequest(`/expenses/recent?limit=${limit}`);
            return { success: true, expenses: data.expenses };
        } catch (error) {
            return { success: false, expenses: [], message: error.message };
        }
    },

    addExpense: async (expense) => {
        try {
            const data = await apiRequest('/expenses/', {
                method: 'POST',
                body: JSON.stringify(expense)
            });
            return { success: true, expense: data.expense };
        } catch (error) {
            return { success: false, message: error.message };
        }
    },
    
    updateExpense: async (expenseId, updates) => {
        try {
            const data = await apiRequest(`/expenses/${expenseId}`, {
                method: 'PUT',
                body: JSON.stringify(updates)
            });
            return { success: true, expense: data.expense };
        } catch (error) {
            return { success: false, message: error.message };
        }
    },
    
    deleteExpense: async (expenseId) => {
        try {
            await apiRequest(`/expenses/${expenseId}`, {
                method: 'DELETE'
            });
            return { success: true };
        } catch (error) {
            return { success: false, message: error.message };
        }
    },

    // Dashboard Stats
    getDashboardStats: async (startDate = null, endDate = null) => {
        try {
            let endpoint = '/expenses/statistics';
            const params = new URLSearchParams();
            if (startDate) params.append('start_date', startDate);
            if (endDate) params.append('end_date', endDate);
            
            if (params.toString()) {
                endpoint += `?${params.toString()}`;
            }
            
            const data = await apiRequest(endpoint);
            return { success: true, stats: data.statistics };
        } catch (error) {
            return { success: false, message: error.message };
        }
    },
    
    // Categories
    getCategories: async () => {
        try {
            const data = await apiRequest('/categories/');
            return { success: true, categories: data.categories };
        } catch (error) {
            return { success: false, categories: [], message: error.message };
        }
    },
    
    createCategory: async (category) => {
        try {
            const data = await apiRequest('/categories/', {
                method: 'POST',
                body: JSON.stringify(category)
            });
            return { success: true, category: data.category };
        } catch (error) {
            return { success: false, message: error.message };
        }
    },
    
    // Savings Goals
    getSavingsGoals: async (status = null) => {
        try {
            const endpoint = status ? `/savings/?status=${status}` : '/savings/';
            const data = await apiRequest(endpoint);
            return { success: true, goals: data.goals, summary: data.summary };
        } catch (error) {
            return { success: false, goals: [], message: error.message };
        }
    },
    
    createSavingsGoal: async (goal) => {
        try {
            const data = await apiRequest('/savings/', {
                method: 'POST',
                body: JSON.stringify(goal)
            });
            return { success: true, goal: data.goal };
        } catch (error) {
            return { success: false, message: error.message };
        }
    },
    
    addToSavingsGoal: async (goalId, amount, notes = '') => {
        try {
            const data = await apiRequest(`/savings/${goalId}/transaction`, {
                method: 'POST',
                body: JSON.stringify({ action: 'add', amount, notes })
            });
            return { success: true, goal: data.goal };
        } catch (error) {
            return { success: false, message: error.message };
        }
    },
    
    // ML/Insights
    getForecast: async () => {
        try {
            const data = await apiRequest('/ml/forecast');
            return { success: true, forecast: data };
        } catch (error) {
            return { success: false, message: error.message };
        }
    },
    
    getInsights: async () => {
        try {
            const data = await apiRequest('/ml/insights');
            return { success: true, insights: data };
        } catch (error) {
            return { success: false, message: error.message };
        }
    },
    
    getAnomalies: async (monthlyBudget = null) => {
        try {
            const endpoint = monthlyBudget 
                ? `/ml/anomalies?monthly_budget=${monthlyBudget}` 
                : '/ml/anomalies';
            const data = await apiRequest(endpoint);
            return { success: true, anomalies: data };
        } catch (error) {
            return { success: false, message: error.message };
        }
    },
    
    getFinancialHealth: async (income = null, savings = null) => {
        try {
            const params = new URLSearchParams();
            if (income) params.append('income', income);
            if (savings) params.append('savings', savings);
            
            const endpoint = params.toString() 
                ? `/ml/financial-health?${params.toString()}` 
                : '/ml/financial-health';
            
            const data = await apiRequest(endpoint);
            return { success: true, health: data };
        } catch (error) {
            return { success: false, message: error.message };
        }
    },
    
    // Alerts
    getAlerts: async (filters = {}) => {
        try {
            const params = new URLSearchParams(filters).toString();
            const endpoint = params ? `/alerts/?${params}` : '/alerts/';
            const data = await apiRequest(endpoint);
            return { success: true, alerts: data.alerts, unread_count: data.unread_count };
        } catch (error) {
            return { success: false, alerts: [], message: error.message };
        }
    },
    
    markAlertAsRead: async (alertId) => {
        try {
            await apiRequest(`/alerts/${alertId}/read`, {
                method: 'PUT'
            });
            return { success: true };
        } catch (error) {
            return { success: false, message: error.message };
        }
    }
};

// Helper function to format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

// Helper function to format date
function formatDate(dateString) {
    const date = new Date(dateString);
    const options = { month: 'short', day: 'numeric', year: 'numeric' };
    return date.toLocaleDateString('en-US', options);
}

// Helper function to format relative date
function formatRelativeDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;
    if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
    if (diffDays < 365) return `${Math.floor(diffDays / 30)} months ago`;
    return `${Math.floor(diffDays / 365)} years ago`;
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { api, formatCurrency, formatDate, formatRelativeDate };
}