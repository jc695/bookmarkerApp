// Article card menu toggle
document.querySelectorAll('.menu-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
        const menu = btn.closest('.card-actions').querySelector('.menu');
        menu.classList.toggle('active');
    });
});

// Theme switching
const themeSelector = document.getElementById('theme');
themeSelector.addEventListener('change', (e) => {
    document.body.setAttribute('data-theme', e.target.value);
    localStorage.setItem('theme', e.target.value);
});

// Font size control
document.getElementById('increase-font').addEventListener('click', () => {
    document.body.style.fontSize = 
        parseInt(window.getComputedStyle(document.body).fontSize) + 2 + 'px';
});

// Modal handling
const modal = new Modal({
    trigger: '#newCollectionBtn',
    content: '#collectionModal'
});

// NEW CODE

// Article card menu toggle
document.querySelectorAll('.menu-dots').forEach(button => {
    button.addEventListener('click', (e) => {
        const menu = button.closest('.article-card').querySelector('.menu-items');
        menu.style.display = menu.style.display === 'block' ? 'none' : 'block';
    });
});

// Close menus when clicking outside
document.addEventListener('click', (e) => {
    if (!e.target.matches('.menu-dots, .menu-item')) {
        document.querySelectorAll('.menu-items').forEach(menu => {
            menu.style.display = 'none';
        });
    }
});

// Collection menu interactions
document.querySelectorAll('.add-collection').forEach(button => {
    button.addEventListener('click', () => {
        // Implement collection selection logic
        alert('Add to collection functionality coming soon!');
    });
});