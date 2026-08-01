var emojis;

document.addEventListener('DOMContentLoaded', function() {
    fetch('/static/files/emoji.json').then(response => response.json())
        .then(data => {
                emojis = data;
                firstRender();
            })
        .catch(error => console.error('Ошибка загрузки:', error));
});

function firstRender(){
    category_list = document.querySelector('div.emoji-box-category-select');
    emoji_list = document.querySelector('div.emoji-box-emoji-select')
    category_list.innerHTML = '';
    emoji_list.innerHTML = '';
    emojis.forEach(e => {
        category_list.innerHTML += category(e.id, e.name, e.symbol);
        emoji_list.innerHTML += categorySelect(e.id, e.name, e.symbol);
    });
    render(0);
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const categoryId = entry.target.id;
                const container = entry.target.querySelector('.emoji-box-emojis');
                render(categoryId);
            }
        });
        }, { threshold: 1, root: document.querySelector('.emoji-box-emoji-select')
    });
    const categories = document.querySelectorAll('.emoji-box-category');
    categories.forEach(cat => {
        if (cat.id !== '0') {
            observer.observe(cat);
        }
    });
}

function render(id){
    if (id < 0 && id >= emojis.length) { return false; }
    emoji_category = emojis[id]
    if (emoji_category.loaded) {return false; }
    parent = document.querySelector(`div#${emoji_category.name}.emoji-box-emojis`)
    parent.innerHTML = '';
    if (emoji_category.subCategories) {
        emoji_category.subCategories.forEach(sub => {
            sub.emojis.forEach(e => {
                parent.innerHTML += emoji(e.symbol, e.name);
            });
        });
    }
    if (emoji_category.emojis){
        emoji_category.emojis.forEach(e => {
            parent.innerHTML += emoji(e.symbol, e.name);
        });
    }
    emoji_category.loaded = true;
    return true;
}

function category(id, name, symbol){
    return `<a title="${name}" href="#${id}">${symbol}</a>`;
}

function categorySelect(id, name, symbol){
    return `<div id="${id}" class="emoji-box-category">
                <p>${symbol} ${name}</p>
                <div id="${name}" class="emoji-box-emojis"></div>
            </div>`;
}

function emoji(symbol, name = ''){
    return `<a title="${name}" onclick="select('${symbol}')">${symbol}</a>`;
}

function select(str){
    const input = document.querySelector('input#ico.menu-btn')
    input.value = str
}