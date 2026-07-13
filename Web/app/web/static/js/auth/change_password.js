async function changeHandler(event) {
    event.preventDefault();
    const password = document.getElementById('new-password').value.trim();
    const confirm = document.getElementById('confirm-password').value.trim();
    const errorEl = document.getElementById('FormError');
    errorEl.textContent = '';
    if (!confirm || !password) {
        errorEl.textContent = 'Введите пароль';
        return;
    }

    if (!is_valid_password(confirm) || !is_valid_password(password)) {
        errorEl.textContent = 'Не верный формат пароля';
        return;
    }

    if (confirm != password) {
        errorEl.textContent = 'Пароли не совпадают';
        return;
    }

    try {
        const queryString = window.location.search;
        const urlParams = new URLSearchParams(queryString);
        const token = urlParams.get('token');
        const response = await fetch('/api/v1/auth/password/change', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'same-origin',
            body: JSON.stringify({ token, password, confirm }),
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

document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('changeForm').addEventListener('submit', changeHandler);
});