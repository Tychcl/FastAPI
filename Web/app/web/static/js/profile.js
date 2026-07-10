function is_valid_username(username) {
    return /^[a-zA-Z]+$/.test(username);
}

function is_valid_password(password) {
    return /^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};:'",.<>/?\\|`~]).{8,}$/.test(password);
}

async function login(event) {
    event.preventDefault();
    const form = document.getElementById('loginForm');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const usernameError = document.getElementById('usernameError');
    const passwordError = document.getElementById('passwordError');
    const formError = document.getElementById('formError');
    usernameError.textContent = '';
    passwordError.textContent = '';
    formError.textContent = '';
    let valid = true;
    const username = usernameInput.value.trim();
    const password = passwordInput.value;
    if (!is_valid_username(username)) {
        usernameError.textContent = 'Логин должен содержать только латинские буквы (a-z, A-Z)';
        valid = false;
    }
    if (!is_valid_password(password)) {
        passwordError.textContent = 'Пароль: мин. 8 символов, 1 заглавная, 1 строчная, 1 цифра, 1 спецсимвол';
        valid = false;
    }
    if (!valid) {
        const firstError = document.querySelector('.error:not(:empty)');
        if (firstError) firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
        return;
    }
    try {
        const response = await fetch('/api/v1/auth/signin', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'same-origin',
            body: JSON.stringify({ username, password }),
        });

        if (response.ok) {
            window.location.href = '/profile';
        } else {
            const data = await response.json().catch(() => ({}));
            const errorMsg = data.detail || 'Неверный логин или пароль';
            formError.textContent = errorMsg;
        }
    } catch (error) {
        console.error('Ошибка:', error);
        formError.textContent = 'Произошла ошибка при входе. Попробуйте позже.';
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const loginform = document.getElementById('loginForm');
    if (loginform) {
        loginform.addEventListener('submit', login);
    }
});

async function logout() {
    try {
        const response = await fetch('/api/v1/auth/signout', {
            method: 'POST',
            credentials: 'same-origin'
        });
        if (response.ok) {
            window.location.href = '/profile';
        } else {
            alert('Ошибка при выходе');
        }
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Произошла ошибка при выходе');
    }
}