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

    // 3. Auto-Dismiss Bootstrap Toasts (4 seconds for flash notifications)
    function initToasts() {
        const toastElList = [].slice.call(document.querySelectorAll('.toast:not(#copyToast)'));
        toastElList.forEach(toastEl => {
            const toast = new bootstrap.Toast(toastEl, { delay: 4000 });
            toast.show();
        });
    }

    // 4. Clipboard Copy Utilities with Button Feedback & Bootstrap Toast
    function initCopyButtons() {
        document.addEventListener('click', function(e) {
            const btn = e.target.closest('.copy-contact-btn');
            if (!btn) return;

            const textToCopy = btn.getAttribute('data-copy');
            if (!textToCopy) return;

            function triggerSuccessFeedback() {
                // Temporary button state change
                const originalHtml = btn.innerHTML;
                btn.innerHTML = '<i class="bi bi-check2"></i> <span>Copied!</span>';
                btn.classList.remove('btn-outline-primary');
                btn.classList.add('btn-success');

                // Trigger Bootstrap Toast Notification
                const copyToastEl = document.getElementById('copyToast');
                if (copyToastEl) {
                    const msgEl = document.getElementById('copyToastMessage');
                    if (msgEl) {
                        msgEl.textContent = `Copied "${textToCopy}" to clipboard!`;
                    }
                    const toastInstance = bootstrap.Toast.getOrCreateInstance(copyToastEl, { delay: 3000 });
                    toastInstance.show();
                }

                // Revert button appearance after 2 seconds
                setTimeout(() => {
                    btn.innerHTML = originalHtml;
                    btn.classList.remove('btn-success');
                    btn.classList.add('btn-outline-primary');
                }, 2000);
            }

            // Clipboard API with robust fallback
            if (navigator.clipboard && window.isSecureContext) {
                navigator.clipboard.writeText(textToCopy)
                    .then(triggerSuccessFeedback)
                    .catch(() => fallbackCopy(textToCopy, triggerSuccessFeedback));
            } else {
                fallbackCopy(textToCopy, triggerSuccessFeedback);
            }
        });
    }

    function fallbackCopy(text, callback) {
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        try {
            document.execCommand('copy');
            if (callback) callback();
        } catch (err) {
            console.error('Fallback copy failed', err);
        }
        document.body.removeChild(textArea);
    }

    // 5. Active Anchor Navigation Highlighting for Home Page
    function initHomeNavSpy() {
        const navLinks = document.querySelectorAll('.home-nav-link');
        if (!navLinks.length) return;

        const sections = [
            document.getElementById('home'),
            document.getElementById('features'),
            document.getElementById('advantages'),
            document.getElementById('contact')
        ].filter(Boolean);

        if (!sections.length) return;

        // Highlight based on current scroll position
        function updateActiveLink() {
            const scrollPos = window.scrollY + 120;
            let currentSectionId = '';

            for (let i = sections.length - 1; i >= 0; i--) {
                const sec = sections[i];
                if (sec.offsetTop <= scrollPos) {
                    currentSectionId = sec.id;
                    break;
                }
            }

            if (!currentSectionId && sections.length) {
                currentSectionId = sections[0].id;
            }

            navLinks.forEach(link => {
                const href = link.getAttribute('href');
                if (href === `#${currentSectionId}`) {
                    link.classList.add('active');
                } else {
                    link.classList.remove('active');
                }
            });
        }

        window.addEventListener('scroll', updateActiveLink, { passive: true });
        updateActiveLink();
    }

    // 6. Dismiss Spending Alert Banner Handler (hides until page reload)
    function initSpendAlertDismiss() {
        const dismissBtn = document.getElementById('dismissSpendAlertBtn');
        if (dismissBtn) {
            dismissBtn.addEventListener('click', function () {
                const banner = document.getElementById('spendingAlertBanner');
                if (banner) {
                    banner.style.display = 'none';
                }
            });
        }
    }

    // Initialize on DOM ready
    document.addEventListener('DOMContentLoaded', () => {
        initTheme();
        initSubmitGuards();
        initToasts();
        initCopyButtons();
        initHomeNavSpy();
        initSpendAlertDismiss();

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
