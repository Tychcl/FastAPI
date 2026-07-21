let user;

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
    const form = document.getElementById('update-user-data');
    try {
        const password = form.querySelector('input#current-password').value;
        if (!is_valid_password(password)){
            alert("Неверный формат пароля");
            return;
        }
        const new_password = form.querySelector('input#new-password').value;
        if (new_password && !is_valid_password(new_password)){
            alert("Неверный формат нового пароля");
            return;
        }
        
        const inputs = form.querySelectorAll('input');
        const user_keys = Object.keys(user);
        let send_data = {};
        
        for (let i = 0; i < inputs.length; i++) {
            const id = inputs[i].id;
            if (id !== 'current-password' && id !== 'new-password' && 
                user_keys.includes(id) && inputs[i].value != user[id]) {
                send_data[id] = inputs[i].value;
            }
        }
        send_data.password = password;
        
        if (new_password) {
            send_data.new_password = new_password;
        }
        
        console.log(send_data)

        const response = await fetch('/api/v1/user/me', {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'same-origin',
            body: JSON.stringify(send_data)
        });

        const data = await response.json().catch(() => ({}));

        if (response.ok) {
            alert('Данные обновлены');
            localStorage.setItem("user", JSON.stringify(data));
            document.getElementById('username-mini').innerHTML = send_data['username']
            user = data;
        } else {
            alert(data.detail || 'Ошибка обновления');
        }

    } catch (error) {
        console.error('Ошибка:', error);
        alert('Произошла ошибка при обновлении');
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

async function changeEmail() {
    const new_email = prompt('Желаете сменить почту?', "");
    console.log(new_email)
    if (is_valid_email(new_email)) {
        try {
            const response = await fetch('/api/v1/auth/email/change', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'same-origin',
                body: JSON.stringify({ new_email }),
            });
            const data = await response.json().catch(() => ({}));
            if (response.ok) {
                alert("На вашу текущую почту была отправлена ссылка для смена\nНа новую почту был отправлен код");
                window.location.href = `/authorize/email/verify?token=${data.token}`;
            } else {
                alert(data.message);
            }
        } catch (e) {
            console.log(e)
        }
    }
}

document.addEventListener('DOMContentLoaded', function() {
    user = JSON.parse(localStorage.getItem('user'));
    document.getElementById('emailInput').addEventListener('click', changeEmail);
    document.getElementById('update-user-data').addEventListener('submit', dataHandler);
    document.getElementById('update-user-privacy').addEventListener('submit', privacyHandler);
});