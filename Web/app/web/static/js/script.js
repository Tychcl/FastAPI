document.addEventListener('DOMContentLoaded', () => {
    
});

function show(id, wrap){
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