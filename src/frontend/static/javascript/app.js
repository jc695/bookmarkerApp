// HTMX Setup
htmx.logAll = true; // Remove in production

// Theme Switcher
const themeSwitcher = {
    init() {
        const savedTheme = localStorage.getItem('theme') || 'light';
        document.documentElement.setAttribute('data-theme', savedTheme);
        this.updateSwitcher(savedTheme);
    },
    
    updateSwitcher(theme) {
        document.querySelectorAll('[data-theme-option]').forEach(el => {
            el.classList.toggle('active', el.dataset.themeOption === theme);
        });
    },
    
    setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        this.updateSwitcher(theme);
    }
};

// Font Size Control
const fontSizeControl = {
    sizes: ['small', 'medium', 'large'],
    current: localStorage.getItem('font-size') || 'medium',
    
    init() {
        document.body.classList.add(`font-${this.current}`);
        this.updateButtons();
    },
    
    adjust(delta) {
        const currentIndex = this.sizes.indexOf(this.current);
        const newIndex = Math.max(0, Math.min(currentIndex + delta, this.sizes.length - 1));
        this.current = this.sizes[newIndex];
        document.body.className = `font-${this.current}`;
        localStorage.setItem('font-size', this.current);
        this.updateButtons();
    },
    
    updateButtons() {
        document.querySelectorAll('[data-font-control]').forEach(btn => {
            btn.disabled = false;
        });
        if (this.current === 'small') {
            document.querySelector('[data-font-control="decrease"]').disabled = true;
        }
        if (this.current === 'large') {
            document.querySelector('[data-font-control="increase"]').disabled = true;
        }
    }
};

// Modal Handling
const modal = {
    open(modalId) {
        const modalEl = document.getElementById(modalId);
        if (modalEl) {
            modalEl.style.display = 'block';
            document.body.style.overflow = 'hidden';
        }
    },
    
    close(modalId) {
        const modalEl = document.getElementById(modalId);
        if (modalEl) {
            modalEl.style.display = 'none';
            document.body.style.overflow = '';
        }
    }
};

// Menu Handling
document.addEventListener('click', (e) => {
    if (e.target.matches('.menu-btn')) {
        const menu = e.target.closest('.article-card').querySelector('.menu');
        menu.style.display = menu.style.display === 'block' ? 'none' : 'block';
    } else if (!e.target.closest('.menu') && !e.target.closest('.menu-btn')) {
        document.querySelectorAll('.menu').forEach(menu => {
            menu.style.display = 'none';
        });
    }
});

// Search Functionality
document.getElementById('searchInput')?.addEventListener('input', (e) => {
    const term = e.target.value.toLowerCase();
    document.querySelectorAll('.article-card').forEach(card => {
        const title = card.querySelector('.article-title').textContent.toLowerCase();
        card.style.display = title.includes(term) ? 'block' : 'none';
    });
});

// Collection Form
document.getElementById('collectionForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const data = {
        name: formData.get('name'),
        description: formData.get('description')
    };
    
    try {
        const response = await fetch('/api/collections', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            modal.close('collectionModal');
            location.reload();
        }
    } catch (error) {
        console.error('Error creating collection:', error);
    }
});

// HTMX Events
document.body.addEventListener('htmx:afterSwap', (e) => {
    if (e.detail.elt.classList.contains('article-card')) {
        // Initialize new elements
    }
});

document.body.addEventListener('htmx:afterRequest', (e) => {
    if (e.detail.failed) {
        // Handle errors
    }
});

// Initialize components
themeSwitcher.init();
fontSizeControl.init();