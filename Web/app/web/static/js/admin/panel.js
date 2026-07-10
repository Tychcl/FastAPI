let roleMap = {};
let page = 1;
let per_page = 25;

function mini_profile_html(id, username, role_id){
    return `<div class="profile-card profile-card-result">
                <p class="username"><strong>👤 ${username}<span>(${id})</span></strong></p>
                <p><strong>Роль:</strong> ${getRoleName(role_id)}</p>
            </div>`;
}

function page_button_html(n){
    return `<button onclick="select_page(${n})" class="menu-btn menu-btn--green">
                <span class="menu-btn__text">${n}</span>
            </button>`;
}

function page_button_separator_html(){
    return `<span class="pages-separator">...</span>`;
}

async function select_page(n){
    page = n;
    if (page != n){
        await find_users();
    }
}

async function find_users(event) {
    try{
        if (event){
            event.preventDefault();
            page = 1;
        }
    }
    catch{}
    
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
    params.append('page', page);
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
        pagesDiv.innerHTML = '';

        if (data.users && data.users.length > 0) {
            let html = ``;
            data.users.forEach(user => {
                html += mini_profile_html(user.id, user.username, user.role_id);
            });
            resultDiv.innerHTML = html;
            pages = Math.max(1, Math.ceil(data.filtered / per_page))
            if (pages < 6){
                for(i = 1; i <= pages; i++){
                    pagesDiv.innerHTML += page_button_html(i);
                }
            }
            else{
                min_page = Math.max(1, page - 2)
                max_page = Math.min(pages, page + 2)
                if (min_page > 1){
                    pagesDiv.innerHTML += page_button_html(1);
                    pagesDiv.innerHTML += page_button_separator_html();
                }
                for(i = min_page; i <= max_page; i++){
                    pagesDiv.innerHTML += page_button_html(i);
                }
                if (max_page < pages){
                    pagesDiv.innerHTML += page_button_separator_html();
                    pagesDiv.innerHTML += page_button_html(pages);
                }
            }
            
        } else {
            resultDiv.innerHTML = '<p>Пользователи не найдены.</p>';
        }
    } catch (error) {
        console.error('Ошибка при поиске пользователей:', error);
        document.getElementById('users-result').innerHTML = `<p style="color:red;">Ошибка: ${error.message}</p>`;
        document.getElementById('users-pages').innerHTML = '';
    }
}

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

document.addEventListener('DOMContentLoaded', function() {
    loadRolesFromSelect();
    const usersform = document.getElementById('users-form');
    if (usersform) {
        usersform.addEventListener('submit', find_users);
    }
});