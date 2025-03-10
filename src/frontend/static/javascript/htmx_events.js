// htmx_events.js (updated)
document.body.addEventListener('htmx:afterSwap', function(evt) {
    // Handle popup feedback insertion
    if (evt.detail.target.id === 'popup-feedback') {
        const popup = evt.detail.target;
        setTimeout(() => {
            popup.classList.add('animate-fade-out');
            setTimeout(() => popup.remove(), 500);
        }, 2000);
    }
});