/**
 * Client-side utilities for Home Budget Tracker.
 * Manages:
 * 1. Double-submit prevention with button spinners
 * 2. Dark mode preference persistence (browser localStorage only; data stays in MySQL)
 * 3. Auto-dismissing toast notifications
 * 4. Responsive touch event optimizations
 */

(function() {
    'use strict';

    // 1. Dark Mode Theme Engine
    function initTheme() {
        const savedTheme = localStorage.getItem('hb_theme') || 'light';
        document.documentElement.setAttribute('data-bs-theme', savedTheme);
        updateThemeIcon(savedTheme);
    }

    function updateThemeIcon(theme) {
        const icon = document.getElementById('themeToggleIcon');
        if (!icon) return;
        if (theme === 'dark') {
            icon.className = 'bi bi-sun-fill text-warning';
        } else {
            icon.className = 'bi bi-moon-stars text-secondary';
        }
    }

    // 2. Submit Button Loading States & Double-Submit Guard
    function initSubmitGuards() {
        document.addEventListener('submit', function(e) {
            const form = e.target;
            if (!form || form.tagName !== 'FORM') return;

            // Don't disable if HTML5 validation fails
            if (form.checkValidity && !form.checkValidity()) {
                return;
            }

            const submitBtn = form.querySelector('button[type="submit"]:not(.no-disable)');
            if (submitBtn && !submitBtn.disabled) {
                // Preserve dimensions so button doesn't jump
                const originalWidth = submitBtn.offsetWidth;
                submitBtn.style.minWidth = `${originalWidth}px`;
                submitBtn.dataset.originalHtml = submitBtn.innerHTML;

                // Add spinner
                submitBtn.disabled = true;
                submitBtn.innerHTML = `
                    <span class="spinner-border spinner-border-sm me-1.5" role="status" aria-hidden="true"></span>
                    <span>Processing...</span>
                `;
            }
        });
    }

    // 3. Auto-Dismiss Bootstrap Toasts (4 seconds)
    function initToasts() {
        const toastElList = [].slice.call(document.querySelectorAll('.toast'));
        toastElList.forEach(toastEl => {
            const toast = new bootstrap.Toast(toastEl, { delay: 4000 });
            toast.show();
        });
    }

    // Initialize on DOM ready
    document.addEventListener('DOMContentLoaded', () => {
        initTheme();
        initSubmitGuards();
        initToasts();

        // Theme Toggle Button click handler
        const toggleBtn = document.getElementById('themeToggleBtn');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => {
                const current = document.documentElement.getAttribute('data-bs-theme') || 'light';
                const next = (current === 'dark') ? 'light' : 'dark';
                document.documentElement.setAttribute('data-bs-theme', next);
                localStorage.setItem('hb_theme', next);
                updateThemeIcon(next);
            });
        }
    });
})();
