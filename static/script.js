/* ============================================================
   Utility helpers
   ============================================================ */

function showMessage(id, text, type = 'error') {
    const el = document.getElementById(id);
    if (!el) return;
    el.textContent = text;
    el.className = `alert alert-${type}`;
    el.classList.remove('hidden');
}

function hideMessage(id) {
    const el = document.getElementById(id);
    if (el) el.classList.add('hidden');
}

function setLoading(btn, loading) {
    const text = btn.querySelector('.btn-text');
    const spinner = btn.querySelector('.btn-spinner');
    btn.disabled = loading;
    if (text) text.classList.toggle('hidden', loading);
    if (spinner) spinner.classList.toggle('hidden', !loading);
}

function togglePassword(inputId, btn) {
    const input = document.getElementById(inputId);
    if (!input) return;
    const show = input.type === 'password';
    input.type = show ? 'text' : 'password';
    btn.textContent = show ? '🙈' : '👁';
}

/* ============================================================
   Password strength meter
   ============================================================ */

function checkStrength(password) {
    let score = 0;
    if (password.length >= 8) score++;
    if (password.length >= 12) score++;
    if (/[A-Z]/.test(password)) score++;
    if (/[0-9]/.test(password)) score++;
    if (/[^A-Za-z0-9]/.test(password)) score++;
    return score; // 0-5
}

const passwordInput = document.getElementById('password');
const strengthFill = document.getElementById('strengthFill');
const strengthLabel = document.getElementById('strengthLabel');

if (passwordInput && strengthFill) {
    const labels = ['', 'Very weak', 'Weak', 'Fair', 'Strong', 'Very strong'];
    const colors = ['', '#ef4444', '#f97316', '#eab308', '#22c55e', '#16a34a'];

    passwordInput.addEventListener('input', () => {
        const score = checkStrength(passwordInput.value);
        strengthFill.style.width = `${(score / 5) * 100}%`;
        strengthFill.style.background = colors[score] || 'transparent';
        if (strengthLabel) {
            strengthLabel.textContent = passwordInput.value ? labels[score] : '';
        }
    });
}

/* ============================================================
   Register form
   ============================================================ */

const registerForm = document.getElementById('registerForm');
if (registerForm) {
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        hideMessage('errorMsg');
        hideMessage('successMsg');

        const btn = document.getElementById('submitBtn');
        const email = document.getElementById('email').value.trim();
        const password = document.getElementById('password').value;
        const usernameEl = document.getElementById('username');
        const username = usernameEl ? usernameEl.value.trim() : '';

        if (!email) return showMessage('errorMsg', 'Email is required.');
        if (!password) return showMessage('errorMsg', 'Password is required.');
        if (password.length < 8) return showMessage('errorMsg', 'Password must be at least 8 characters.');

        setLoading(btn, true);

        try {
            const response = await fetch('/auth/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password, username: username || undefined }),
            });

            const data = await response.json();

            if (response.ok) {
                showMessage('successMsg', '🎉 Account created! Redirecting to login…', 'success');
                setTimeout(() => window.location.href = '/login', 1500);
            } else {
                showMessage('errorMsg', data.detail || data.message || 'Registration failed.');
            }
        } catch {
            showMessage('errorMsg', 'Network error. Please try again.');
        } finally {
            setLoading(btn, false);
        }
    });
}

/* ============================================================
   Login form
   ============================================================ */

const loginForm = document.getElementById('loginForm');
if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        hideMessage('errorMsg');

        const btn = document.getElementById('submitBtn');
        const email = document.getElementById('email').value.trim();
        const password = document.getElementById('password').value;

        if (!email) return showMessage('errorMsg', 'Please enter your email.');
        if (!password) return showMessage('errorMsg', 'Please enter your password.');

        setLoading(btn, true);

        try {
            const formData = new URLSearchParams();
            formData.append('username', email); // router accepts "username" key
            formData.append('password', password);

            const response = await fetch('/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: formData,
            });

            const data = await response.json();

            if (response.ok) {
                // Cookie is set server-side (httponly); just redirect
                window.location.href = '/dashboard';
            } else {
                showMessage('errorMsg', data.detail || data.message || 'Invalid email or password.');
            }
        } catch {
            showMessage('errorMsg', 'Network error. Please try again.');
        } finally {
            setLoading(btn, false);
        }
    });
}

/* ============================================================
   Dashboard — load user data & handle logout
   ============================================================ */

async function loadDashboard() {
    const loadingState = document.getElementById('loadingState');
    const profileCard = document.getElementById('profileCard');
    if (!profileCard) return; // Not on dashboard page

    try {
        const response = await fetch('/auth/me');

        if (response.status === 401) {
            // Session expired — redirect to login
            window.location.href = '/login';
            return;
        }

        if (!response.ok) throw new Error('Failed to load profile');

        const user = await response.json();

        // Populate navbar
        const navUsername = document.getElementById('navUsername');
        const navRole = document.getElementById('navRole');
        if (navUsername) navUsername.textContent = user.username;
        if (navRole) {
            navRole.textContent = user.role;
            navRole.className = `nav-badge role-${user.role}`;
        }

        // Populate profile card
        const avatarEl = document.getElementById('avatarInitial');
        if (avatarEl) avatarEl.textContent = user.username.charAt(0).toUpperCase();

        const set = (id, value) => { const el = document.getElementById(id); if (el) el.textContent = value; };
        set('welcomeMsg', `Welcome, ${user.username}! 👋`);
        set('userEmail', user.email);
        set('infoUsername', user.username);
        set('infoEmail', user.email);
        set('infoRole', user.role.charAt(0).toUpperCase() + user.role.slice(1));
        set('infoAge', user.age);

        // Show card, hide skeleton
        if (loadingState) loadingState.classList.add('hidden');
        profileCard.classList.remove('hidden');

    } catch (err) {
        if (loadingState) loadingState.innerHTML = '<p class="loading-text" style="color:#ef4444">⚠️ Failed to load profile. <a href="/login">Login again</a></p>';
    }
}

const logoutBtn = document.getElementById('logoutBtn');
if (logoutBtn) {
    logoutBtn.addEventListener('click', async () => {
        logoutBtn.disabled = true;
        logoutBtn.textContent = 'Logging out…';
        await fetch('/auth/logout', { method: 'POST' });
        window.location.href = '/login';
    });

    // Load profile when on dashboard
    loadDashboard();
}