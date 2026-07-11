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