document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('loginForm');
    if (!form) return;
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const usernameError = document.getElementById('usernameError');
    const passwordError = document.getElementById('passwordError');
    const formError = document.getElementById('formError');
    const usernameRegex = /^[a-zA-Z]+$/;
    const passwordRegex = /^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};:'",.<>/?\\|`~]).{8,}$/;
    form.addEventListener('submit', function(e) {
        let valid = true;
        usernameError.textContent = '';
        passwordError.textContent = '';
        formError.textContent = '';
        const username = usernameInput.value.trim();
        if (!usernameRegex.test(username)) {
            usernameError.textContent = 'Логин должен содержать только латинские буквы (a-z, A-Z)';
            valid = false;
        }
        const password = passwordInput.value;
        if (!passwordRegex.test(password)) {
            passwordError.textContent = 'Пароль: мин. 8 символов, 1 заглавная, 1 строчная, 1 цифра, 1 спецсимвол';
            valid = false;
        }
        if (!valid) {
            e.preventDefault();
            const firstError = document.querySelector('.error:not(:empty)');
            if (firstError) firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    });
});

function logout(){
    
}