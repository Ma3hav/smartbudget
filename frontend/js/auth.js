// Tab switching
document.querySelectorAll('.auth-tab').forEach(tab => {
    tab.addEventListener('click', function() {
        const targetTab = this.dataset.tab;
        
        // Update active tab
        document.querySelectorAll('.auth-tab').forEach(t => t.classList.remove('active'));
        this.classList.add('active');
        
        // Show/hide forms
        document.getElementById('loginForm').style.display = targetTab === 'login' ? 'block' : 'none';
        document.getElementById('signupForm').style.display = targetTab === 'signup' ? 'block' : 'none';
    });
});

// Login form submission
document.getElementById('loginForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    
    try {
        const response = await api.login(email, password);
        
        if (response.success) {
            // Store user data
            localStorage.setItem('user', JSON.stringify(response.user));
            
            // Redirect to dashboard
            window.location.href = 'dashboard.html';
        } else {
            alert('Login failed. Please try again.');
        }
    } catch (error) {
        console.error('Login error:', error);
        alert('An error occurred. Please try again.');
    }
});

// Signup form submission
document.getElementById('signupForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const name = document.getElementById('signupName').value;
    const email = document.getElementById('signupEmail').value;
    const password = document.getElementById('signupPassword').value;
    
    try {
        const response = await api.signup(name, email, password);
        
        if (response.success) {
            // Store user data
            localStorage.setItem('user', JSON.stringify(response.user));
            
            // Redirect to dashboard
            window.location.href = 'dashboard.html';
        } else {
            alert('Signup failed. Please try again.');
        }
    } catch (error) {
        console.error('Signup error:', error);
        alert('An error occurred. Please try again.');
    }
});
