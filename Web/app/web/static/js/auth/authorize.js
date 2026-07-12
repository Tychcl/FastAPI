function is_valid_username(username) {
    return /^[a-zA-Z]+$/.test(username);
}

function is_valid_password(password) {
    return /^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};:'",.<>/?\\|`~]).{8,}$/.test(password);
}

function is_valid_email(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function switchTab(mode) {
    const tabs = document.querySelectorAll('.tab-btn');
    const forms = document.querySelectorAll('#loginForm, #registerForm, #forgotForm');

    tabs.forEach(tab => tab.classList.remove('active'));
    forms.forEach(form => form.classList.remove('active'));

    if (mode === 'login') {
        document.querySelector('[data-tab="login"]').classList.add('active');
        document.getElementById('loginForm').classList.add('active');
    } 
    if (mode === 'register') {
        document.querySelector('[data-tab="register"]').classList.add('active');
        document.getElementById('registerForm').classList.add('active');
    }
    if (mode === 'forgot') {
        document.querySelector('[data-tab="forgot"]').classList.add('active');
        document.getElementById('forgotForm').classList.add('active');
    }
    document.querySelectorAll('.error').forEach(el => el.textContent = '');
}

async function loginHandler(event) {
    event.preventDefault();
    const login = document.getElementById('login').value.trim();
    const password = document.getElementById('password').value;
    const errorEl = document.getElementById('loginFormError');

    if (!login) {
        document.getElementById('loginError').textContent = 'Введите логин или email';
        return;
    }
    if (!is_valid_password(password)) {
        document.getElementById('passwordError').textContent = 'Пароль: не менее 8 символов, заглавная, строчная, цифра, спецсимвол';
        return;
    }

    try {
        const response = await fetch('/api/v1/auth/signin', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'same-origin',
            body: JSON.stringify({ login, password }),
        });
        if (response.ok) {
            window.location.href = '/profile';
        } else {
            const data = await response.json().catch(() => ({}));
            errorEl.textContent = data.message || 'Неверный логин или пароль';
        }
    } catch (e) {
        errorEl.textContent = 'Ошибка соединения';
    }
}

async function registerHandler(event) {
    event.preventDefault();
    const username = document.getElementById('reg-username').value.trim();
    const email = document.getElementById('reg-email').value.trim();
    const password = document.getElementById('reg-password').value;
    const confirm = document.getElementById('reg-confirm-password').value;
    const errorEl = document.getElementById('registerFormError');

    if (!is_valid_username(username)) {
        document.getElementById('regUsernameError').textContent = 'Логин только латиница';
        return;
    }
    if (!is_valid_email(email)) {
        document.getElementById('regEmailError').textContent = 'Введите корректный email';
        return;
    }
    if (!is_valid_password(password)) {
        document.getElementById('regPasswordError').textContent = 'Пароль: не менее 8 символов, заглавная, строчная, цифра, спецсимвол';
        return;
    }
    if (password !== confirm) {
        document.getElementById('regConfirmError').textContent = 'Пароли не совпадают';
        return;
    }

    try {
        const response = await fetch('/api/v1/auth/signup', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'same-origin',
            body: JSON.stringify({ username, email, password, role_id: 3, confirm }),
        });
        if (response.ok) {
            window.location.href = '/authorize/email/verify';
        } else {
            const data = await response.json().catch(() => ({}));
            errorEl.textContent = data.message || 'Ошибка регистрации';
        }
    } catch (e) {
        errorEl.textContent = 'Ошибка соединения';
    }
}

async function forgotHandler(event) {
    event.preventDefault();
    const login = document.getElementById('forgotlogin').value.trim();
    const errorEl = document.getElementById('forgotloginFormError');

    if (!login) {
        document.getElementById('forgotloginError').textContent = 'Введите логин или email';
        return;
    }
    if (!is_valid_username(login) && !is_valid_email(login)){
        document.getElementById('forgotloginError').textContent = 'Неверный формат логина';
        return;
    }

    try {
        const response = await fetch('/api/v1/auth/password/forgot', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'same-origin',
            body: JSON.stringify({ login }),
        });
        if (response.ok) {
            document.getElementById('forgotloginError').textContent = 'На почту была отправлена ссылка для восстановления пароля';
        } else {
            const data = await response.json().catch(() => ({}));
            errorEl.textContent = data.message || 'Неверный логин или пароль';
        }
    } catch (e) {
        errorEl.textContent = 'Ошибка соединения';
    }
}

document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('loginForm').addEventListener('submit', loginHandler);
    document.getElementById('registerForm').addEventListener('submit', registerHandler);
    document.getElementById('forgotForm').addEventListener('submit', forgotHandler);
    switchTab('login');
});