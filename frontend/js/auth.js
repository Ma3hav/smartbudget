// ===============================
// CONFIG
// ===============================
const API_BASE_URL = "http://127.0.0.1:5000/api";  // Backend URL

// Create API helper using fetch
const api = {
    login: async (email, password) => {
        const res = await fetch(`${API_BASE_URL}/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password })
        });
        return res.json();
    },

    signup: async (name, email, password) => {
        const res = await fetch(`${API_BASE_URL}/auth/signup`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name, email, password })
        });
        return res.json();
    }
};


// ===============================
// TAB SWITCHING
// ===============================
document.querySelectorAll('.auth-tab').forEach(tab => {
    tab.addEventListener('click', function () {
        const targetTab = this.dataset.tab;

        // Update UI
        document.querySelectorAll('.auth-tab').forEach(t => t.classList.remove('active'));
        this.classList.add('active');

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

    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;

    try {
        const response = await api.login(email, password);

        if (response.access_token) {
            // Save token and user
            localStorage.setItem("token", response.access_token);
            localStorage.setItem("user", JSON.stringify(response.user));

            window.location.href = "dashboard.html";
        } else {
            alert(response.message || "Login failed");
        }
    } catch (err) {
        console.error(err);
        alert("An error occurred while logging in.");
    }
});


// ===============================
// SIGNUP FORM
// ===============================
document.getElementById('signupForm').addEventListener('submit', async function (e) {
    e.preventDefault();

    const name = document.getElementById('signupName').value;
    const email = document.getElementById('signupEmail').value;
    const password = document.getElementById('signupPassword').value;

    try {
        const response = await api.signup(name, email, password);

        if (response.success || response.access_token) {
            // Save token and user
            if (response.access_token) {
                localStorage.setItem("token", response.access_token);
            }
            localStorage.setItem("user", JSON.stringify(response.user));

            window.location.href = "dashboard.html";
        } else {
            alert(response.message || "Signup failed");
        }
    } catch (err) {
        console.error(err);
        alert("An error occurred during signup.");
    }
});
