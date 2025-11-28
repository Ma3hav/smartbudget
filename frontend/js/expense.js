// Load recent expenses in sidebar
async function loadRecentExpenses() {
    const response = await api.getExpenses();
    const recentExpenses = document.getElementById('recentExpenses');
    
    recentExpenses.innerHTML = response.expenses.slice(0, 6).map(expense => `
        <div class="sidebar-transaction">
            <div>
                <h4>${expense.category}</h4>
                <p>${formatDate(expense.date)}</p>
            </div>
            <div class="amount">-${formatCurrency(expense.amount)}</div>
        </div>
    `).join('');
}

// Form submission
document.getElementById('expenseForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const expense = {
        amount: parseFloat(document.getElementById('amount').value),
        category: document.getElementById('category').value,
        paymentType: document.getElementById('paymentType').value,
        date: document.getElementById('date').value,
        notes: document.getElementById('notes').value
    };
    
    try {
        const response = await api.addExpense(expense);
        
        if (response.success) {
            // Show success message
            alert('Expense added successfully!');
            
            // Reset form
            this.reset();
            document.getElementById('date').valueAsDate = new Date();
            
            // Reload recent expenses
            loadRecentExpenses();
        } else {
            alert('Failed to add expense. Please try again.');
        }
    } catch (error) {
        console.error('Error adding expense:', error);
        alert('An error occurred. Please try again.');
    }
});
