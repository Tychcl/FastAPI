async function logout() {
    try {
        const response = await fetch('/api/v1/auth/signout', {
            method: 'POST',
            credentials: 'same-origin'
        });
        if (response.ok) {
            localStorage.removeItem("user");
            window.location.href = '/profile';
        } else {
            alert('Ошибка при выходе');
        }
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Произошла ошибка при выходе');
    }
}

async function dataHandler(event) {
    event.preventDefault();
    try{

    } catch (error) {
        console.error('Ошибка:', error);
        alert('Произошла ошибка при выходе');
    }
}

async function privacyHandler(event) {
    event.preventDefault();
    const show_email = document.getElementById('show_email').checked;
    const show_about = document.getElementById('show_about').checked;
    try {
        const response = await fetch('/api/v1/user/me/privacy', {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'same-origin',
            body: JSON.stringify({ show_email, show_about })
        });

        if (response.ok) {
            alert('Настройки приватности обновлены');
        } else {
            const data = await response.json().catch(() => ({}));
            alert(data.detail || 'Ошибка обновления настроек');
        }
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Произошла ошибка при обновлении настроек');
    }
}

function changeEmail() {
    const change = confirm('Желаете сменить почту?');
    if (change) {
        
    }
}

document.addEventListener('DOMContentLoaded', function() {
     document.getElementById('email').addEventListener('click', changeEmail);
    document.getElementById('update-user-data').addEventListener('submit', dataHandler);
    document.getElementById('update-user-privacy').addEventListener('submit', privacyHandler);
});