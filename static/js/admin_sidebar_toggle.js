/**
 * Admin Sidebar Toggle JavaScript
 * Provides collapsible sidebar functionality for Django admin interface
 */

(function() {
    'use strict';

    // Wait for DOM to be fully loaded
    document.addEventListener('DOMContentLoaded', function() {
        initializeSidebarToggle();
    });

    function initializeSidebarToggle() {
        const sidebar = document.getElementById('content-related');
        
        // Only initialize if sidebar exists on the page
        if (!sidebar) {
            return;
        }

        // Create toggle button
        const toggleButton = createToggleButton();
        document.body.appendChild(toggleButton);

        // Create overlay for mobile
        const overlay = createOverlay();
        document.body.appendChild(overlay);

        // Create close button inside sidebar
        const closeButton = createCloseButton();
        sidebar.insertBefore(closeButton, sidebar.firstChild);

        // Set up event listeners
        setupEventListeners(toggleButton, closeButton, overlay, sidebar);

        // Handle keyboard navigation
        setupKeyboardNavigation(sidebar);

        // Handle responsive behavior
        handleResponsiveChanges();
    }

    function createToggleButton() {
        const button = document.createElement('button');
        button.className = 'sidebar-toggle-btn';
        button.setAttribute('aria-label', 'Toggle sidebar');
        button.setAttribute('data-tooltip', 'Toggle sidebar');
        button.innerHTML = `
            <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path d="M3 18h18v-2H3v2zm0-5h18v-2H3v2zm0-7v2h18V6H3z"/>
            </svg>
        `;
        return button;
    }

    function createOverlay() {
        const overlay = document.createElement('div');
        overlay.className = 'sidebar-overlay';
        overlay.setAttribute('aria-hidden', 'true');
        return overlay;
    }

    function createCloseButton() {
        const button = document.createElement('button');
        button.className = 'sidebar-close-btn';
        button.setAttribute('aria-label', 'Close sidebar');
        button.innerHTML = `
            <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12 19 6.41z"/>
            </svg>
        `;
        return button;
    }

    function setupEventListeners(toggleButton, closeButton, overlay, sidebar) {
        // Toggle button click
        toggleButton.addEventListener('click', function(e) {
            e.preventDefault();
            toggleSidebar(sidebar, overlay, toggleButton);
        });

        // Close button click
        closeButton.addEventListener('click', function(e) {
            e.preventDefault();
            closeSidebar(sidebar, overlay, toggleButton);
        });

        // Overlay click to close
        overlay.addEventListener('click', function(e) {
            e.preventDefault();
            closeSidebar(sidebar, overlay, toggleButton);
        });

        // ESC key to close sidebar
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && sidebar.classList.contains('sidebar-visible')) {
                closeSidebar(sidebar, overlay, toggleButton);
            }
        });
    }

    function setupKeyboardNavigation(sidebar) {
        // Make sidebar focusable when visible
        sidebar.addEventListener('transitionend', function() {
            if (sidebar.classList.contains('sidebar-visible')) {
                // Focus first focusable element in sidebar
                const focusableElements = sidebar.querySelectorAll(
                    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
                );
                if (focusableElements.length > 0) {
                    focusableElements[0].focus();
                }
            }
        });
    }

    function toggleSidebar(sidebar, overlay, toggleButton) {
        const isVisible = sidebar.classList.contains('sidebar-visible');
        
        if (isVisible) {
            closeSidebar(sidebar, overlay, toggleButton);
        } else {
            openSidebar(sidebar, overlay, toggleButton);
        }
    }

    function openSidebar(sidebar, overlay, toggleButton) {
        sidebar.classList.add('sidebar-visible');
        overlay.classList.add('active');
        toggleButton.classList.add('active');
        
        // Update ARIA attributes
        sidebar.setAttribute('aria-hidden', 'false');
        overlay.setAttribute('aria-hidden', 'false');
        toggleButton.setAttribute('aria-expanded', 'true');
        toggleButton.setAttribute('data-tooltip', 'Close sidebar');

        // Prevent body scroll on mobile
        if (window.innerWidth <= 768) {
            document.body.style.overflow = 'hidden';
        }

        // Save state in localStorage
        localStorage.setItem('admin-sidebar-visible', 'true');
    }

    function closeSidebar(sidebar, overlay, toggleButton) {
        sidebar.classList.remove('sidebar-visible');
        overlay.classList.remove('active');
        toggleButton.classList.remove('active');
        
        // Update ARIA attributes
        sidebar.setAttribute('aria-hidden', 'true');
        overlay.setAttribute('aria-hidden', 'true');
        toggleButton.setAttribute('aria-expanded', 'false');
        toggleButton.setAttribute('data-tooltip', 'Toggle sidebar');

        // Restore body scroll
        document.body.style.overflow = '';

        // Save state in localStorage
        localStorage.setItem('admin-sidebar-visible', 'false');
    }

    function handleResponsiveChanges() {
        let resizeTimer;
        
        window.addEventListener('resize', function() {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(function() {
                const sidebar = document.getElementById('content-related');
                const overlay = document.querySelector('.sidebar-overlay');
                const toggleButton = document.querySelector('.sidebar-toggle-btn');
                
                if (!sidebar) return;

                // On desktop, remove mobile-specific restrictions
                if (window.innerWidth > 768) {
                    document.body.style.overflow = '';
                }
            }, 250);
        });
    }

    // Restore sidebar state from localStorage on page load
    function restoreSidebarState() {
        const savedState = localStorage.getItem('admin-sidebar-visible');
        if (savedState === 'true') {
            // Small delay to ensure elements are ready
            setTimeout(function() {
                const sidebar = document.getElementById('content-related');
                const overlay = document.querySelector('.sidebar-overlay');
                const toggleButton = document.querySelector('.sidebar-toggle-btn');
                
                if (sidebar && overlay && toggleButton) {
                    openSidebar(sidebar, overlay, toggleButton);
                }
            }, 100);
        }
    }

    // Initialize state restoration
    document.addEventListener('DOMContentLoaded', function() {
        setTimeout(restoreSidebarState, 200);
    });

})();