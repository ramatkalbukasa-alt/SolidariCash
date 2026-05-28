/* SolidariCash — Main JS */
'use strict';

// Auto-dismiss messages
document.addEventListener('DOMContentLoaded', () => {
    const msgs = document.querySelectorAll('[data-autohide]');
    msgs.forEach(el => {
        setTimeout(() => {
            el.style.transition = 'opacity 0.5s';
            el.style.opacity = '0';
            setTimeout(() => el.remove(), 500);
        }, 4000);
    });
});

// Confirm dangerous actions
document.querySelectorAll('[data-confirm]').forEach(btn => {
    btn.addEventListener('click', e => {
        if (!confirm(btn.dataset.confirm)) e.preventDefault();
    });
});

// Mark notification read via AJAX
function markNotifRead(pk) {
    fetch(`/notifications/${pk}/read/`, {
        method: 'GET',
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    }).then(r => r.json()).then(() => {
        const el = document.getElementById(`notif-${pk}`);
        if (el) el.classList.add('opacity-50');
    });
}
