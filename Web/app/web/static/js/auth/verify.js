async function verifyHandler(event) {
    event.preventDefault();
    const code = document.getElementById('code').value.trim();
    const errorEl = document.getElementById('FormError');
    errorEl.textContent = '';
    if (!code) {
        errorEl.textContent = 'Введите код';
        return;
    }

    try {
        const response = await fetch('/api/v1/auth/email/verify', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'same-origin',
            body: JSON.stringify({ code }),
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
    document.getElementById('verifyForm').addEventListener('submit', verifyHandler);
});