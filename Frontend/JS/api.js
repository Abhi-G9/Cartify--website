const BASE_URL = 'http://127.0.0.1:8000/api';

// Utility to handle JSON requests
async function fetchAPI(endpoint, method = 'GET', body = null) {
    const headers = { 'Content-Type': 'application/json' };
    const options = { method, headers };
    if (body) options.body = JSON.stringify(body);
    
    const response = await fetch(`${BASE_URL}${endpoint}`, options);
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'API Error');
    return data;
}

function getEmail() { return localStorage.getItem('user_email'); }
function logout() { localStorage.clear(); window.location.href = 'auth.html'; }

// Update UI based on auth state
document.addEventListener('DOMContentLoaded', () => {
    const authLink = document.getElementById('auth-link');
    if (getEmail()) {
        authLink.innerText = 'Logout';
        authLink.onclick = (e) => { e.preventDefault(); logout(); };
    }
});