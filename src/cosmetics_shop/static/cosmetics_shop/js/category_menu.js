document.addEventListener('DOMContentLoaded', () => {
    const categories = document.querySelectorAll('.category-item');
    const submenus = document.querySelectorAll('.submenu-full');
    const menu = document.querySelector('.categories-menu');

    categories.forEach(cat => {
        cat.addEventListener('mouseenter', () => {
            const id = cat.dataset.category;

            submenus.forEach(sm => sm.style.display = 'none');

            const active = document.querySelector(`.submenu-full[data-submenu="${id}"]`);
            if (active) active.style.display = 'block';
        });
    });

    menu.addEventListener('mouseleave', () => {
        submenus.forEach(sm => sm.style.display = 'none');
    });
});