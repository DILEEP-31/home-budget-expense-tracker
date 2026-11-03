/**
 * Client-Side JavaScript for Public Landing Page
 * Features:
 * 1. Typewriter animation for hero headline
 * 2. Animated count-up numbers for factual project statistics
 * 3. IntersectionObserver scroll reveal with staggered delays
 * 4. Active navbar link spy with smooth scrolling
 * 5. Clipboard copy handler with button feedback & Bootstrap toast
 * 6. Dark/Light mode theme sync
 * 7. Accessibility guard for prefers-reduced-motion
 */

(function () {
    'use strict';

    // Check accessibility reduced motion preference
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    // 1. Mark JS enabled for progressive enhancement
    if (!prefersReducedMotion) {
        document.body.classList.add('js-enabled');
    }

    // 2. Typewriter Effect for Hero Headline
    function initTypewriter() {
        const headlineEl = document.getElementById('typewriterHeadline');
        if (!headlineEl) return;

        const targetText = "Track every rupee. Save more every month.";

        if (prefersReducedMotion) {
            headlineEl.textContent = targetText;
            return;
        }

        headlineEl.textContent = '';
        let charIndex = 0;
        const typeSpeed = 55; // ms per char

        function typeNextChar() {
            if (charIndex < targetText.length) {
                headlineEl.textContent += targetText.charAt(charIndex);
                charIndex++;
                setTimeout(typeNextChar, typeSpeed);
            }
        }

        // Start typing shortly after DOM loads
        setTimeout(typeNextChar, 350);
    }

    // 3. Animated Number Counters
    function initCounters() {
        const counterEls = document.querySelectorAll('.counter-value');
        if (!counterEls.length) return;

        if (prefersReducedMotion) {
            counterEls.forEach(el => {
                el.textContent = el.getAttribute('data-target') || el.textContent;
            });
            return;
        }

        let animated = false;
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting && !animated) {
                    animated = true;
                    counterEls.forEach(el => {
                        const target = parseInt(el.getAttribute('data-target'), 10);
                        const suffix = el.getAttribute('data-suffix') || '';
                        const duration = 1400; // ms
                        const stepTime = 25;
                        const totalSteps = duration / stepTime;
                        const stepIncrement = target / totalSteps;
                        let current = 0;

                        const timer = setInterval(() => {
                            current += stepIncrement;
                            if (current >= target) {
                                el.textContent = target + suffix;
                                clearInterval(timer);
                            } else {
                                el.textContent = Math.floor(current) + suffix;
                            }
                        }, stepTime);
                    });
                    observer.disconnect();
                }
            });
        }, { threshold: 0.25 });

        const statsSection = document.getElementById('statsStrip');
        if (statsSection) {
            observer.observe(statsSection);
        }
    }

    // 4. Scroll Reveal via IntersectionObserver
    function initScrollReveal() {
        if (prefersReducedMotion) return;

        const revealElements = document.querySelectorAll('.reveal-on-scroll');
        if (!revealElements.length) return;

        const revealObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('is-revealed');
                    revealObserver.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.12,
            rootMargin: '0px 0px -40px 0px'
        });

        revealElements.forEach(el => revealObserver.observe(el));
    }

    // 5. Active Navbar Link Highlighting
    function initNavScrollspy() {
        const navLinks = document.querySelectorAll('.public-nav-link');
        if (!navLinks.length) return;

        const sections = [
            document.getElementById('home'),
            document.getElementById('about'),
            document.getElementById('features'),
            document.getElementById('advantages'),
            document.getElementById('contact')
        ].filter(Boolean);

        if (!sections.length) return;

        function onScroll() {
            const scrollPos = window.scrollY + 140;
            let currentId = '';

            for (let i = sections.length - 1; i >= 0; i--) {
                const sec = sections[i];
                if (sec.offsetTop <= scrollPos) {
                    currentId = sec.id;
                    break;
                }
            }

            if (!currentId && sections.length) {
                currentId = sections[0].id;
            }

            navLinks.forEach(link => {
                const href = link.getAttribute('href');
                if (href && href.endsWith(`#${currentId}`)) {
                    link.classList.add('active');
                } else {
                    link.classList.remove('active');
                }
            });
        }

        window.addEventListener('scroll', onScroll, { passive: true });
        onScroll();
    }

    // 6. Clipboard Copy with Toast Feedback
    function initCopyButtons() {
        document.addEventListener('click', function (e) {
            const btn = e.target.closest('.copy-contact-btn');
            if (!btn) return;

            const textToCopy = btn.getAttribute('data-copy');
            if (!textToCopy) return;

            function triggerSuccess() {
                const originalHtml = btn.innerHTML;
                btn.innerHTML = '<i class="bi bi-check2"></i> <span>Copied!</span>';
                btn.classList.remove('btn-outline-primary');
                btn.classList.add('btn-success');

                const toastEl = document.getElementById('copyToast');
                if (toastEl) {
                    const msgEl = document.getElementById('copyToastMessage');
                    if (msgEl) {
                        msgEl.textContent = `Copied "${textToCopy}" to clipboard!`;
                    }
                    const toastInstance = bootstrap.Toast.getOrCreateInstance(toastEl, { delay: 3000 });
                    toastInstance.show();
                }

                setTimeout(() => {
                    btn.innerHTML = originalHtml;
                    btn.classList.remove('btn-success');
                    btn.classList.add('btn-outline-primary');
                }, 2000);
            }

            if (navigator.clipboard && window.isSecureContext) {
                navigator.clipboard.writeText(textToCopy).then(triggerSuccess).catch(() => fallbackCopy(textToCopy, triggerSuccess));
            } else {
                fallbackCopy(textToCopy, triggerSuccess);
            }
        });
    }

    function fallbackCopy(text, callback) {
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
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

    // 7. Dark Mode Theme Engine
    function initTheme() {
        const savedTheme = localStorage.getItem('hb_theme') || 'light';
        document.documentElement.setAttribute('data-bs-theme', savedTheme);
        updateThemeIcon(savedTheme);

        const toggleBtn = document.getElementById('themeToggleBtn');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => {
                const current = document.documentElement.getAttribute('data-bs-theme') || 'light';
                const next = current === 'dark' ? 'light' : 'dark';
                document.documentElement.setAttribute('data-bs-theme', next);
                localStorage.setItem('hb_theme', next);
                updateThemeIcon(next);
            });
        }
    }

    function updateThemeIcon(theme) {
        const icon = document.getElementById('themeToggleIcon');
        if (!icon) return;
        icon.className = theme === 'dark' ? 'bi bi-sun-fill text-warning' : 'bi bi-moon-stars text-secondary';
    }

    // Initialize all modules on DOM ready
    document.addEventListener('DOMContentLoaded', () => {
        initTheme();
        initTypewriter();
        initCounters();
        initScrollReveal();
        initNavScrollspy();
        initCopyButtons();
    });
})();
