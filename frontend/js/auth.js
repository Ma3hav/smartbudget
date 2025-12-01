/**
 * Authentication Module
 * Handles login and signup functionality using the centralized API module
 */

// ===============================
// TAB SWITCHING
// ===============================
document.querySelectorAll('.auth-tab').forEach(tab => {
    tab.addEventListener('click', function () {
        const targetTab = this.dataset.tab;

        // Update active tab styling
        document.querySelectorAll('.auth-tab').forEach(t => t.classList.remove('active'));
        this.classList.add('active');

        // Toggle form visibility
        document.getElementById('loginForm').style.display =
            targetTab === 'login' ? 'block' : 'none';

        document.getElementById('signupForm').style.display =
            targetTab === 'signup' ? 'block' : 'none';
    });
});


// ===============================
// LOGIN FORM
// ===============================
document.getElementById('loginForm').addEventListener('submit', async function (e) {
    e.preventDefault();

    const email = document.getElementById('loginEmail').value.trim();
    const password = document.getElementById('loginPassword').value;

    // Basic validation
    if (!email || !password) {
        showError('Please enter both email and password');
        return;
    }

    // Disable submit button to prevent double submission
    const submitButton = this.querySelector('button[type="submit"]');
    const originalText = submitButton.textContent;
    submitButton.disabled = true;
    submitButton.textContent = 'Logging in...';

    try {
        const response = await api.login(email, password);

        if (response.success) {
            showSuccess('Login successful! Redirecting...');
            
            // Small delay for user feedback before redirect
            setTimeout(() => {
                window.location.href = 'dashboard.html';
            }, 500);
        } else {
            showError(response.message || 'Login failed. Please check your credentials.');
            submitButton.disabled = false;
            submitButton.textContent = originalText;
        }
    } catch (err) {
        console.error('Login error:', err);
        showError('An error occurred while logging in. Please try again.');
        submitButton.disabled = false;
        submitButton.textContent = originalText;
    }
});


// ===============================
// SIGNUP FORM
// ===============================
document.getElementById('signupForm').addEventListener('submit', async function (e) {
    e.preventDefault();

    const name = document.getElementById('signupName').value.trim();
    const email = document.getElementById('signupEmail').value.trim();
    const password = document.getElementById('signupPassword').value;

    // Validation
    if (!name || !email || !password) {
        showError('Please fill in all fields');
        return;
    }

    if (name.length < 2) {
        showError('Name must be at least 2 characters long');
        return;
    }

    if (!isValidEmail(email)) {
        showError('Please enter a valid email address');
        return;
    }

    if (password.length < 8) {
        showError('Password must be at least 8 characters long');
        return;
    }

    // Disable submit button
    const submitButton = this.querySelector('button[type="submit"]');
    const originalText = submitButton.textContent;
    submitButton.disabled = true;
    submitButton.textContent = 'Creating Account...';

    try {
        const response = await api.signup(name, email, password);

        if (response.success) {
            showSuccess('Account created successfully! Redirecting...');
            
            // Small delay for user feedback before redirect
            setTimeout(() => {
                window.location.href = 'dashboard.html';
            }, 500);
        } else {
            showError(response.message || 'Signup failed. Please try again.');
            submitButton.disabled = false;
            submitButton.textContent = originalText;
        }
    } catch (err) {
        console.error('Signup error:', err);
        showError('An error occurred during signup. Please try again.');
        submitButton.disabled = false;
        submitButton.textContent = originalText;
    }
});


// ===============================
// HELPER FUNCTIONS
// ===============================

/**
 * Validate email format
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
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
 * Show notification (error or success)
 */
function showNotification(message, type = 'error') {
    // Remove any existing notifications
    const existingNotification = document.querySelector('.auth-notification');
    if (existingNotification) {
        existingNotification.remove();
    }

    // Create notification element
    const notification = document.createElement('div');
    notification.className = `auth-notification auth-notification-${type}`;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        left: 50%;
        transform: translateX(-50%);
        padding: 16px 24px;
        background: ${type === 'error' ? '#D2042D' : '#22c55e'};
        color: white;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 10000;
        font-size: 14px;
        font-weight: 500;
        max-width: 90%;
        text-align: center;
        animation: slideDown 0.3s ease;
    `;
    notification.textContent = message;

    // Add animation styles
    if (!document.getElementById('notification-styles')) {
        const style = document.createElement('style');
        style.id = 'notification-styles';
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
            @keyframes slideUp {
                from {
                    transform: translateX(-50%) translateY(0);
                    opacity: 1;
                }
                to {
                    transform: translateX(-50%) translateY(-100%);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
    }

    document.body.appendChild(notification);

    // Auto-remove after 4 seconds
    setTimeout(() => {
        notification.style.animation = 'slideUp 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 4000);
}


// ===============================
// AUTO-REDIRECT IF ALREADY LOGGED IN
// ===============================
document.addEventListener('DOMContentLoaded', function() {
    // Check if user is already logged in
    const user = localStorage.getItem('user');
    if (user) {
        try {
            const userData = JSON.parse(user);
            if (userData.access_token) {
                console.log('User already logged in, redirecting to dashboard...');
                window.location.href = 'dashboard.html';
            }
        } catch (err) {
            // Invalid user data, clear it
            localStorage.removeItem('user');
        }
    }
});


// ===============================
// KEYBOARD SHORTCUTS
// ===============================
document.addEventListener('keydown', function(e) {
    // Alt+L for Login tab
    if (e.altKey && e.key === 'l') {
        e.preventDefault();
        document.querySelector('[data-tab="login"]').click();
        document.getElementById('loginEmail').focus();
    }
    
    // Alt+S for Signup tab
    if (e.altKey && e.key === 's') {
        e.preventDefault();
        document.querySelector('[data-tab="signup"]').click();
        document.getElementById('signupName').focus();
    }
});