/*
  SmartBudget Dashboard JavaScript (final)
  - Loads profile, summary, transactions and forecast
  - Renders metrics, transactions list and donut chart (Chart.js)
  - Handles primary navigation buttons
  - Assumes token is stored in localStorage under 'token'
*/

(function () {
  'use strict';

  const API_BASE = '/api'; // prefix for backend endpoints

  // DOM refs
  const welcomeTitle = document.getElementById('welcome-title');
  const avatarInitials = document.getElementById('avatar-initials');
  const balanceCard = document.getElementById('balance-card');
  const expenseCard = document.getElementById('expense-card');
  const budgetCard = document.getElementById('budget-card');
  const transactionsList = document.getElementById('transactions-list');
  const addExpenseBtn = document.getElementById('add-expense-btn');
  const viewInsightsBtn = document.getElementById('view-insights-btn');
  const viewAllBtn = document.getElementById('view-all-btn');
  const profileBtn = document.getElementById('profile-btn');
  const spendingChartCanvas = document.getElementById('spending-chart');
  const chartLegend = document.getElementById('chart-legend');

  let chartInstance = null;

  // Default category config (icon + color)
  const categoryConfig = {
    Food: { icon: '🍔', color: '#4FD1C5' },
    Transport: { icon: '🚗', color: '#60A5FA' },
    Shopping: { icon: '🛍️', color: '#FBBF24' },
    Entertainment: { icon: '🎬', color: '#4BC0C0' },
    Bills: { icon: '💡', color: '#9966FF' },
    Healthcare: { icon: '⚕️', color: '#FF9F40' },
    Education: { icon: '📚', color: '#FDA4AF' },
    Salary: { icon: '💰', color: '#86EFAC' },
    Investment: { icon: '📈', color: '#93C5FD' },
    Other: { icon: '📦', color: '#CBD5E1' }
  };

  // ----- Utilities -----
  function getAuthHeaders() {
    const token = localStorage.getItem('token');
    const headers = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;
    return headers;
  }

  async function safeJson(response) {
    const text = await response.text();
    try { return text ? JSON.parse(text) : {}; } catch (e) { return {}; }
  }

  function formatCurrency(amount) {
    try {
      return new Intl.NumberFormat(navigator.language || 'en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(amount);
    } catch (e) {
      return `₹${Math.round(amount)}`;
    }
  }

  function formatDate(dateStr) {
    if (!dateStr) return '';
    const d = new Date(dateStr);
    const today = new Date();
    const yesterday = new Date();
    yesterday.setDate(today.getDate() - 1);

    if (d.toDateString() === today.toDateString()) return 'Today';
    if (d.toDateString() === yesterday.toDateString()) return 'Yesterday';
    return d.toLocaleDateString(navigator.language || 'en-IN', { month: 'short', day: 'numeric' });
  }

  function getCategoryConfig(name) {
    return categoryConfig[name] || categoryConfig['Other'];
  }

  // ----- API helpers -----
  async function apiGet(path) {
    try {
      const res = await fetch(`${API_BASE}${path}`, { headers: getAuthHeaders(), credentials: 'same-origin' });
      const json = await safeJson(res);
      if (!res.ok) {
        if (res.status === 401) {
          localStorage.removeItem('token');
          window.location.href = '/index.html';
          return null;
        }
        throw new Error(json.message || 'Request failed');
      }
      return json;
    } catch (err) {
      console.error('API error', path, err);
      return null;
    }
  }

  // ----- Fetchers -----
  async function fetchUserProfile() {
    return await apiGet('/auth/me');
  }
  async function fetchSummary() {
    return await apiGet('/summary');
  }
  async function fetchTransactions(limit = 5) {
    const data = await apiGet(`/expenses?limit=${encodeURIComponent(limit)}`);
    if (Array.isArray(data)) return data;
    if (data && Array.isArray(data.items)) return data.items;
    return [];
  }
  async function fetchForecast() {
    return await apiGet('/forecast');
  }

  // ----- Renderers -----
  function updateWelcome(user) {
    if (!user) return;
    if (user.name) {
      welcomeTitle.textContent = `Welcome back, ${user.name.split(' ')[0]}!`;
      const initials = user.name.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase();
      if (avatarInitials) avatarInitials.textContent = initials;
    }
  }

  function renderMetricCard(containerEl, label, value, change) {
    if (!containerEl) return;
    containerEl.innerHTML = `
      <div class="metric-label">${label}</div>
      <div class="metric-value">${formatCurrency(value || 0)}</div>
      <div class="metric-change ${typeof change === 'number' && change >= 0 ? 'positive' : 'negative'}">
        ${typeof change === 'number' ? (change >= 0 ? '▲ ' : '▼ ') + Math.abs(change).toFixed(1) + '%' : ''}
      </div>
    `;
  }

  function updateMetrics(summary) {
    if (!summary) return;
    renderMetricCard(balanceCard, 'Total Balance', summary.total_balance || 0, summary.total_change ?? 0);
    renderMetricCard(expenseCard, "This Month's Expense", summary.month_expense || 0, summary.expense_change ?? 0);
    renderMetricCard(budgetCard, 'Remaining Budget', summary.remaining_budget || 0, summary.budget_change ?? 0);
  }

  function renderTransactions(transactions = []) {
    if (!transactionsList) return;
    if (!transactions || transactions.length === 0) {
      transactionsList.innerHTML = `
        <div class="empty-state">
          <p>No transactions yet. Add your first expense to get started.</p>
        </div>
      `;
      return;
    }

    transactionsList.innerHTML = transactions.slice(0, 5).map(tx => {
      const cfg = getCategoryConfig(tx.category);
      const isIncome = (tx.type || '').toLowerCase() === 'income';
      const amountClass = isIncome ? 'income' : 'expense';
      const prefix = isIncome ? '+' : '-';
      return `
        <div class="transaction-item" data-id="${tx._id || ''}">
          <div class="transaction-icon" style="background-color: ${cfg.color}22;">
            ${cfg.icon}
          </div>
          <div class="transaction-details">
            <div class="transaction-title">${tx.title || tx.category || 'Transaction'}</div>
            <div class="transaction-meta">${tx.category || 'Other'} • ${formatDate(tx.date)}</div>
          </div>
          <div class="transaction-amount ${amountClass}">
            ${prefix}${formatCurrency(Math.abs(Number(tx.amount || 0)))}
          </div>
        </div>
      `;
    }).join('');
  }

  function clearChart() {
    if (chartInstance) {
      chartInstance.destroy();
      chartInstance = null;
    }
    if (spendingChartCanvas && spendingChartCanvas.parentElement) {
      const es = spendingChartCanvas.parentElement.querySelectorAll('.empty-state');
      es.forEach(n => n.remove());
    }
  }

  function renderChart(forecast) {
    if (!spendingChartCanvas) return;

    if (!forecast || !Array.isArray(forecast.by_category) || forecast.by_category.length === 0) {
      clearChart();
      spendingChartCanvas.parentElement.innerHTML = `
        <div class="empty-state">
          <p>No spending data available yet</p>
        </div>
      `;
      return;
    }

    const categories = forecast.by_category;
    const labels = categories.map(c => c.category);
    const data = categories.map(c => Number(c.predicted || 0));
    const colors = categories.map(c => getCategoryConfig(c.category).color || '#CBD5E1');

    if (chartInstance) chartInstance.destroy();

    const ctx = spendingChartCanvas.getContext ? spendingChartCanvas.getContext('2d') : null;
    chartInstance = new Chart(ctx || spendingChartCanvas, {
      type: 'doughnut',
      data: {
        labels,
        datasets: [{
          data,
          backgroundColor: colors,
          borderColor: '#fff',
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '68%',
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: function (ctx) {
                const label = ctx.label || '';
                const value = ctx.parsed || 0;
                return `${label}: ${formatCurrency(value)}`;
              }
            }
          }
        }
      }
    });

    renderChartLegend(categories);
  }

  function renderChartLegend(categories = []) {
    if (!chartLegend) return;
    chartLegend.innerHTML = categories.map(item => {
      const cfg = getCategoryConfig(item.category);
      return `
        <div class="legend-item">
          <div class="legend-color" style="background-color: ${cfg.color};"></div>
          <div class="legend-label">${item.category}</div>
          <div class="legend-value">${formatCurrency(Number(item.predicted || 0))}</div>
        </div>
      `;
    }).join('');
  }

  // ----- UI wiring -----
  function wireUi() {
    if (addExpenseBtn) addExpenseBtn.addEventListener('click', () => window.location.href = '/add_expense.html');
    if (viewInsightsBtn) viewInsightsBtn.addEventListener('click', () => window.location.href = '/insights.html');
    if (viewAllBtn) viewAllBtn.addEventListener('click', () => window.location.href = '/transactions.html');
    if (profileBtn) profileBtn.addEventListener('click', () => window.location.href = '/profile.html');

    if (transactionsList) {
      transactionsList.addEventListener('click', (e) => {
        const row = e.target.closest('.transaction-item');
        if (!row) return;
        const id = row.dataset.id;
        if (id) window.location.href = `/transaction.html?id=${encodeURIComponent(id)}`;
      });
    }
  }

  // ----- Auth check -----
  function ensureAuth() {
    const token = localStorage.getItem('token');
    if (!token) {
      window.location.href = '/index.html';
      return false;
    }
    return true;
  }

  // ----- Main loader -----
  async function loadDashboard() {
    if (!ensureAuth()) return;
    wireUi();

    const [user, summary, transactions, forecast] = await Promise.all([
      fetchUserProfile(),
      fetchSummary(),
      fetchTransactions(5),
      fetchForecast()
    ]);

    if (user) updateWelcome(user);
    if (summary) updateMetrics(summary);
    renderTransactions(Array.isArray(transactions) ? transactions : (transactions?.items || []));
    renderChart(forecast || { by_category: [] });
  }

  // ----- Fetch helper wrappers calling api endpoints -----
  async function fetchUserProfile() {
    return await apiGet('/auth/me');
  }
  async function fetchSummary() {
    return await apiGet('/summary');
  }
  async function fetchTransactions(limit = 5) {
    return await apiGet(`/expenses?limit=${encodeURIComponent(limit)}`) || [];
  }
  async function fetchForecast() {
    return await apiGet('/forecast');
  }

  // ----- run -----
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', loadDashboard);
  } else {
    loadDashboard();
  }

  // expose for debugging
  window.SmartBudget = window.SmartBudget || {};
  window.SmartBudget.dashboard = { renderChart, renderTransactions, fetchForecast };

})();
