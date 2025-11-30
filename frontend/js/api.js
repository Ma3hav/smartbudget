// API Configuration
const API_BASE_URL = "http://127.0.0.1:5000/api";

// Mock data storage (replace with real API calls)
const mockExpenses = [
    { id: 1, amount: 45.50, category: 'Food', paymentType: 'Credit Card', date: '2024-11-27', notes: 'Lunch at cafe' },
    { id: 2, amount: 120.00, category: 'Shopping', paymentType: 'Debit Card', date: '2024-11-26', notes: 'New shoes' },
    { id: 3, amount: 85.00, category: 'Transport', paymentType: 'UPI', date: '2024-11-25', notes: 'Taxi fare' },
    { id: 4, amount: 30.00, category: 'Food', paymentType: 'Cash', date: '2024-11-24', notes: 'Groceries' },
    { id: 5, amount: 200.00, category: 'Bills', paymentType: 'Bank Transfer', date: '2024-11-23', notes: 'Electricity bill' }
];

// API Functions
const api = {
    // Authentication
    login: async (email, password) => {
        // Mock login - replace with real API call
        return new Promise((resolve) => {
            setTimeout(() => {
                resolve({ 
                    success: true, 
                    user: { id: 1, name: 'John Doe', email } 
                });
            }, 500);
        });
    },

    signup: async (name, email, password) => {
        // Mock signup - replace with real API call
        return new Promise((resolve) => {
            setTimeout(() => {
                resolve({ 
                    success: true, 
                    user: { id: 1, name, email } 
                });
            }, 500);
        });
    },

    // Expenses
    getExpenses: async () => {
        return new Promise((resolve) => {
            setTimeout(() => {
                resolve({ success: true, expenses: mockExpenses });
            }, 300);
        });
    },

    addExpense: async (expense) => {
        return new Promise((resolve) => {
            setTimeout(() => {
                const newExpense = { 
                    id: mockExpenses.length + 1, 
                    ...expense 
                };
                mockExpenses.unshift(newExpense);
                resolve({ success: true, expense: newExpense });
            }, 300);
        });
    },

    // Dashboard Stats
    getDashboardStats: async () => {
        return new Promise((resolve) => {
            setTimeout(() => {
                resolve({
                    success: true,
                    stats: {
                        totalBalance: 12450,
                        monthlyExpenses: 1830,
                        remainingBudget: 3670
                    }
                });
            }, 300);
        });
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