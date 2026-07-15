function is_valid_username(username) {
    return /^[a-zA-Z]+$/.test(username);
}

function is_valid_password(password) {
    return /^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};:'",.<>/?\\|`~]).{8,}$/.test(password);
}

function is_valid_email(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function show(id, wrap = 'menu-wrapper'){
    const wrapper = document.getElementById(wrap);
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

function toggleTheme() {
    document.body.classList.toggle('dark-theme');
    const isDark = document.body.classList.contains('dark-theme');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
    updateThemeIcon(isDark);
}

function updateThemeIcon(isDark) {
    const icon = document.getElementById('theme-icon');
    if (!icon) return;
    if (isDark) {
        icon.innerHTML = `
            <circle cx="12" cy="12" r="5" class="icon-stroke" stroke-width="1.8"/>
            <line x1="12" y1="1" x2="12" y2="4" class="icon-stroke" stroke-width="1.8" stroke-linecap="round"/>
            <line x1="12" y1="20" x2="12" y2="23" class="icon-stroke" stroke-width="1.8" stroke-linecap="round"/>
            <line x1="1" y1="12" x2="4" y2="12" class="icon-stroke" stroke-width="1.8" stroke-linecap="round"/>
            <line x1="20" y1="12" x2="23" y2="12" class="icon-stroke" stroke-width="1.8" stroke-linecap="round"/>
            <line x1="4.22" y1="4.22" x2="6.34" y2="6.34" class="icon-stroke" stroke-width="1.8" stroke-linecap="round"/>
            <line x1="17.66" y1="17.66" x2="19.78" y2="19.78" class="icon-stroke" stroke-width="1.8" stroke-linecap="round"/>
            <line x1="4.22" y1="19.78" x2="6.34" y2="17.66" class="icon-stroke" stroke-width="1.8" stroke-linecap="round"/>
            <line x1="17.66" y1="6.34" x2="19.78" y2="4.22" class="icon-stroke" stroke-width="1.8" stroke-linecap="round"/>
        `;
    } else {
        icon.innerHTML = `
            <path d="M12 3C9.8 3 7.8 4 6.3 5.5C4.8 7 3.8 9 3.8 11.2C3.8 15.6 7.4 19.2 11.8 19.2C14 19.2 16 18.2 17.5 16.7C19 15.2 20 13.2 20 11C20 6.6 16.4 3 12 3Z" class="icon-stroke" stroke-width="1.8" fill="none"/>
        `;
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-theme');
        updateThemeIcon(true);
    } else {
        updateThemeIcon(false);
    }
});