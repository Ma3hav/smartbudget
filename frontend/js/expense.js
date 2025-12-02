/**
 * Expense Management Module
 * Handles adding expenses and displaying recent transactions
 */

// ===============================
// STATE MANAGEMENT
// ===============================
const expenseState = {
    isLoading: false,
    recentExpenses: [],
    categories: []
};


// ===============================
// INITIALIZE ON PAGE LOAD
// ===============================
document.addEventListener('DOMContentLoaded', async function() {
    console.log('🔧 Initializing expense page...');
    
    // Check authentication
    if (!checkAuthentication()) {
        return;
    }
    
    // Load initial data
    await initializeExpensePage();
    
    // Setup form submission
    setupFormSubmission();
    
    console.log('✅ Expense page initialized');
});


// ===============================
// AUTHENTICATION CHECK
// ===============================
function checkAuthentication() {
    const user = localStorage.getItem('user');
    
    if (!user) {
        showError('Please login to continue');
        setTimeout(() => {
            window.location.href = 'index.html';
        }, 1500);
        return false;
    }
    
    try {
        const userData = JSON.parse(user);
        if (!userData.access_token) {
            throw new Error('Invalid token');
        }
        return true;
    } catch (err) {
        console.error('Invalid user data:', err);
        localStorage.removeItem('user');
        window.location.href = 'index.html';
        return false;
    }
}


// ===============================
// INITIALIZE EXPENSE PAGE
// ===============================
async function initializeExpensePage() {
    try {
        showLoadingState();
        
        // Load data in parallel
        await Promise.all([
            loadRecentExpenses(),
            loadCategories()
        ]);
        
        hideLoadingState();
        
    } catch (error) {
        console.error('Error initializing expense page:', error);
        showError('Failed to load expense data');
        hideLoadingState();
    }
}


// ===============================
// LOAD RECENT EXPENSES
// ===============================
async function loadRecentExpenses() {
    if (expenseState.isLoading) {
        return;
    }
    
    expenseState.isLoading = true;
    const recentExpensesContainer = document.getElementById('recentExpenses');
    
    if (!recentExpensesContainer) {
        console.warn('Recent expenses container not found');
        expenseState.isLoading = false;
        return;
    }
    
    try {
        // Show loading state in sidebar
        recentExpensesContainer.innerHTML = `
            <div style="text-align: center; padding: 20px; color: #999;">
                <div class="loading-spinner"></div>
                <p style="margin-top: 12px; font-size: 14px;">Loading...</p>
            </div>
        `;
        
        // Fetch recent expenses (limit to 6 for sidebar)
        const response = await api.getRecentExpenses(6);
        
        if (!response.success) {
            throw new Error(response.message || 'Failed to load expenses');
        }
        
        expenseState.recentExpenses = response.expenses;
        
        // Display expenses
        if (response.expenses.length === 0) {
            recentExpensesContainer.innerHTML = `
                <div style="text-align: center; padding: 30px 20px; color: #999;">
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-bottom: 12px; opacity: 0.5;">
                        <circle cx="12" cy="12" r="10"></circle>
                        <line x1="12" y1="8" x2="12" y2="12"></line>
                        <line x1="12" y1="16" x2="12.01" y2="16"></line>
                    </svg>
                    <p style="font-size: 14px; font-weight: 500;">No expenses yet</p>
                    <p style="font-size: 13px; margin-top: 4px;">Add your first expense!</p>
                </div>
            `;
        } else {
            recentExpensesContainer.innerHTML = response.expenses.map((expense, index) => `
                <div class="sidebar-transaction" style="animation: fadeIn 0.3s ease ${index * 50}ms both;">
                    <div>
                        <h4>${escapeHtml(expense.category)}</h4>
                        <p>${formatDate(expense.date)}</p>
                        ${expense.notes ? `<p style="font-size: 12px; color: #999; margin-top: 2px;">${escapeHtml(expense.notes.substring(0, 30))}${expense.notes.length > 30 ? '...' : ''}</p>` : ''}
                    </div>
                    <div class="amount">-${formatCurrency(expense.amount)}</div>
                </div>
            `).join('');
        }
        
        console.log(`✅ Loaded ${response.expenses.length} recent expenses`);
        
    } catch (error) {
        console.error('Error loading recent expenses:', error);
        recentExpensesContainer.innerHTML = `
            <div style="text-align: center; padding: 30px 20px; color: #D2042D;">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-bottom: 12px;">
                    <circle cx="12" cy="12" r="10"></circle>
                    <line x1="15" y1="9" x2="9" y2="15"></line>
                    <line x1="9" y1="9" x2="15" y2="15"></line>
                </svg>
                <p style="font-size: 14px; font-weight: 500;">Failed to load expenses</p>
                <button onclick="loadRecentExpenses()" style="margin-top: 12px; padding: 8px 16px; background: #D2042D; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 13px;">
                    Retry
                </button>
            </div>
        `;
        showError('Failed to load recent expenses');
    } finally {
        expenseState.isLoading = false;
    }
}


// ===============================
// LOAD CATEGORIES
// ===============================
async function loadCategories() {
    try {
        const response = await api.getCategories();
        
        if (response.success && response.categories) {
            expenseState.categories = response.categories;
            
            // Populate category dropdown
            const categorySelect = document.getElementById('category');
            if (categorySelect && response.categories.length > 0) {
                categorySelect.innerHTML = response.categories.map(cat => 
                    `<option value="${escapeHtml(cat.name)}">${escapeHtml(cat.name)}</option>`
                ).join('');
            }
            
            console.log(`✅ Loaded ${response.categories.length} categories`);
        }
    } catch (error) {
        console.error('Error loading categories:', error);
        // Don't show error to user - will use default categories
    }
}


// ===============================
// FORM SUBMISSION
// ===============================
function setupFormSubmission() {
    const form = document.getElementById('expenseForm');
    
    if (!form) {
        console.warn('Expense form not found');
        return;
    }
    
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Get form values
        const amount = document.getElementById('amount').value;
        const category = document.getElementById('category').value;
        const paymentType = document.getElementById('paymentType').value;
        const date = document.getElementById('date').value;
        const notes = document.getElementById('notes').value;
        
        // Validate form
        if (!validateExpenseForm(amount, category, paymentType, date)) {
            return;
        }
        
        // Prepare expense data
        const expense = {
            amount: parseFloat(amount),
            category: category,
            payment_type: paymentType,
            date: new Date(date).toISOString(),
            notes: notes.trim(),
            tags: [] // Can be extended later
        };
        
        // Submit expense
        await submitExpense(expense);
    });
}


// ===============================
// VALIDATE EXPENSE FORM
// ===============================
function validateExpenseForm(amount, category, paymentType, date) {
    // Validate amount
    if (!amount || parseFloat(amount) <= 0) {
        showError('Please enter a valid amount greater than 0');
        document.getElementById('amount').focus();
        return false;
    }
    
    if (parseFloat(amount) > 1000000) {
        showError('Amount seems unreasonably high. Please check.');
        document.getElementById('amount').focus();
        return false;
    }
    
    // Validate category
    if (!category) {
        showError('Please select a category');
        document.getElementById('category').focus();
        return false;
    }
    
    // Validate payment type
    if (!paymentType) {
        showError('Please select a payment type');
        document.getElementById('paymentType').focus();
        return false;
    }
    
    // Validate date
    if (!date) {
        showError('Please select a date');
        document.getElementById('date').focus();
        return false;
    }
    
    const selectedDate = new Date(date);
    const today = new Date();
    
    if (selectedDate > today) {
        showError('Cannot add expenses for future dates');
        document.getElementById('date').focus();
        return false;
    }
    
    return true;
}


// ===============================
// SUBMIT EXPENSE
// ===============================
async function submitExpense(expense) {
    const submitButton = document.querySelector('#expenseForm button[type="submit"]');
    const originalText = submitButton.innerHTML;
    
    try {
        // Disable button and show loading
        submitButton.disabled = true;
        submitButton.innerHTML = `
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="animation: spin 1s linear infinite;">
                <circle cx="12" cy="12" r="10"></circle>
            </svg>
            Adding...
        `;
        
        // Add CSS for spin animation if not exists
        if (!document.getElementById('spin-animation')) {
            const style = document.createElement('style');
            style.id = 'spin-animation';
            style.textContent = `
                @keyframes spin {
                    from { transform: rotate(0deg); }
                    to { transform: rotate(360deg); }
                }
            `;
            document.head.appendChild(style);
        }
        
        // Submit to API
        const response = await api.addExpense(expense);
        
        if (!response.success) {
            throw new Error(response.message || 'Failed to add expense');
        }
        
        // Success!
        showSuccess('Expense added successfully! 🎉');
        console.log('✅ Expense added:', response.expense);
        
        // Reset form
        document.getElementById('expenseForm').reset();
        
        // Reset date to today
        document.getElementById('date').valueAsDate = new Date();
        
        // Reload recent expenses
        await loadRecentExpenses();
        
        // Re-enable button
        submitButton.disabled = false;
        submitButton.innerHTML = originalText;
        
        // Focus on amount field for quick next entry
        document.getElementById('amount').focus();
        
    } catch (error) {
        console.error('Error adding expense:', error);
        showError(error.message || 'Failed to add expense. Please try again.');
        
        // Re-enable button
        submitButton.disabled = false;
        submitButton.innerHTML = originalText;
    }
}


// ===============================
// HELPER FUNCTIONS
// ===============================

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Show loading state
 */
function showLoadingState() {
    const recentExpenses = document.getElementById('recentExpenses');
    if (recentExpenses) {
        recentExpenses.innerHTML = `
            <div class="loading-spinner"></div>
        `;
    }
    
    // Add loading spinner CSS if not exists
    if (!document.getElementById('loading-spinner-styles')) {
        const style = document.createElement('style');
        style.id = 'loading-spinner-styles';
        style.textContent = `
            .loading-spinner {
                width: 40px;
                height: 40px;
                margin: 20px auto;
                border: 4px solid #f3f3f3;
                border-top: 4px solid #D2042D;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
        `;
        document.head.appendChild(style);
    }
}

/**
 * Hide loading state
 */
function hideLoadingState() {
    // Loading state will be replaced by content
}

/**
 * Show error notification
 */
function showError(message) {
    showNotification(message, 'error');
}

/**
 * Show success notification
 */
function showSuccess(message) {
    showNotification(message, 'success');
}

/**
 * Show notification
 */
function showNotification(message, type = 'error') {
    // Remove existing notification
    const existing = document.querySelector('.expense-notification');
    if (existing) {
        existing.remove();
    }
    
    const notification = document.createElement('div');
    notification.className = `expense-notification expense-notification-${type}`;
    notification.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        padding: 16px 24px;
        background: ${type === 'error' ? '#D2042D' : '#22c55e'};
        color: white;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 10000;
        font-size: 14px;
        font-weight: 500;
        max-width: 400px;
        animation: slideInRight 0.3s ease;
        display: flex;
        align-items: center;
        gap: 12px;
    `;
    
    notification.innerHTML = `
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            ${type === 'error' ? 
                '<circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line>' :
                '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline>'
            }
        </svg>
        <span>${escapeHtml(message)}</span>
    `;
    
    // Add animation styles
    if (!document.getElementById('notification-animations')) {
        const style = document.createElement('style');
        style.id = 'notification-animations';
        style.textContent = `
            @keyframes slideInRight {
                from {
                    transform: translateX(400px);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
            @keyframes slideOutRight {
                from {
                    transform: translateX(0);
                    opacity: 1;
                }
                to {
                    transform: translateX(400px);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
    }
    
    document.body.appendChild(notification);
    
    // Auto-remove after 4 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 4000);
}


// ===============================
// EXPORT FOR EXTERNAL USE
// ===============================
if (typeof window !== 'undefined') {
    window.loadRecentExpenses = loadRecentExpenses;
    window.expenseState = expenseState;
}