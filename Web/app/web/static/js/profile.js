let roleMap = {};
function loadRolesFromSelect() {
    const select = document.getElementById('role_id');
    if (!select) return;

    const map = {};
    for (const option of select.options) {
        const value = option.value;
        if (value !== '') {
            map[value] = option.textContent.trim();
        }
    }
    roleMap = map;
    console.log('Роли загружены:', roleMap);
}

function getRoleName(roleId) {
    return roleMap[roleId] || 'Неизвестная роль';
}

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

async function find_users(event) {
    event.preventDefault();
    const form = document.getElementById('users-form');

    const idsInput = form.querySelector('#ids');
    const usernameInput = form.querySelector('#username');
    const role_idSelect = form.querySelector('#role_id');

    const idsRaw = idsInput.value.trim();
    const username = usernameInput.value.trim();
    const role_id = role_idSelect.value;

    const params = new URLSearchParams();

    if (idsRaw) {
        const idsArray = idsRaw.split(/\s+/).filter(id => id.length > 0);
        idsArray.forEach(id => params.append('ids', id));
    }
    if (username) params.append('username', username);
    if (role_id) params.append('role_id', role_id);

    // Если сервер поддерживает пагинацию, можно раскомментировать:
    // params.append('page', 1);
    // params.append('per_page', 25);

    try {
        const response = await fetch(`/api/v1/user/find?${params.toString()}`, {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'same-origin'
        });

        if (!response.ok) {
            throw new Error(`Ошибка ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();

        const resultDiv = document.getElementById('users-result');
        const pagesDiv = document.getElementById('users-pages');

        if (data.users && data.users.length > 0) {
            let html = ``;
            data.users.forEach(user => {
                html += mini_profile_html(user.id, user.username, user.role_id);
            });
            resultDiv.innerHTML = html;
            pagesDiv.innerHTML = '';
        } else {
            resultDiv.innerHTML = '<p>Пользователи не найдены.</p>';
            pagesDiv.innerHTML = '';
        }
    } catch (error) {
        console.error('Ошибка при поиске пользователей:', error);
        document.getElementById('users-result').innerHTML = `<p style="color:red;">Ошибка: ${error.message}</p>`;
        document.getElementById('users-pages').innerHTML = '';
    }
}

document.addEventListener('DOMContentLoaded', function() {
    loadRolesFromSelect();
    const loginform = document.getElementById('loginForm');
    if (loginform) {
        loginform.addEventListener('submit', login);
    }
    const usersform = document.getElementById('users-form');
    if (usersform) {
        usersform.addEventListener('submit', find_users);
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

function show(id){
    const wrapper = document.getElementById('menu-wrapper');
    if (!wrapper) {
        console.error('Элемент #menu-wrapper не найден');
        return;
    }
    const children = wrapper.children;
    for (let child of children) {
        if (child.id !== id) {
            child.classList.remove('visible');
            child.classList.add('hidden');
        } else {
            if (child.classList.contains('hidden')){
                child.classList.remove('hidden');
                child.classList.add('visible');
            }
            else{
                child.classList.remove('visible');
                child.classList.add('hidden');
            }
        }
    }
}

function mini_profile_html(id, username, role_id){
    return `<div class="profile-card profile-card-result">
                <p class="username"><strong>👤 ${username}<span>(${id})</span></strong></p>
                <p><strong>Роль:</strong> ${getRoleName(role_id)}</p>
            </div>`;
}