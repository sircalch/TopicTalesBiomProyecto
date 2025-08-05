/* ============================================================
   SIDEBAR BEHAVIOR FIXES - TopicTales Biomédica  
   Control de comportamiento de menús desplegables
   ============================================================ */

class SidebarManager {
    constructor() {
        this.init();
    }

    init() {
        console.log('SidebarManager: Inicializando control de sidebar...');
        this.preventAutoExpansion();
        this.setupClickHandlers();
        this.fixHoverStates();
        this.setupKeyboardNavigation();
        this.observeMutations();
    }

    preventAutoExpansion() {
        // Prevenir auto-expansion de menús
        const hasMenuItems = document.querySelectorAll('.pcoded-navbar .pcoded-inner-navbar li.pcoded-hasmenu');
        
        hasMenuItems.forEach(item => {
            // Marcar como controlado manualmente
            item.setAttribute('data-auto-expanded', 'false');
            
            // Asegurar que el submenu esté cerrado inicialmente
            const submenu = item.querySelector('.pcoded-submenu');
            if (submenu && !item.classList.contains('pcoded-trigger')) {
                submenu.style.display = 'none';
                submenu.style.opacity = '0';
                submenu.style.visibility = 'hidden';
            }
            
            // Remover cualquier clase que cause auto-expansion
            item.classList.remove('active');
            if (!this.isCurrentPage(item)) {
                item.classList.remove('pcoded-trigger');
            }
        });
    }

    setupClickHandlers() {
        const hasMenuItems = document.querySelectorAll('.pcoded-navbar .pcoded-inner-navbar li.pcoded-hasmenu > .nav-link');
        
        hasMenuItems.forEach(link => {
            // Remover listeners existentes
            link.removeEventListener('click', this.handleMenuClick);
            
            // Add new controlled click handler
            link.addEventListener('click', (e) => this.handleMenuClick(e));
        });
    }

    handleMenuClick(e) {
        e.preventDefault();
        e.stopPropagation();
        
        const menuItem = e.currentTarget.closest('li.pcoded-hasmenu');
        const submenu = menuItem.querySelector('.pcoded-submenu');
        
        if (!submenu) return;
        
        const isCurrentlyOpen = menuItem.classList.contains('pcoded-trigger');
        
        // Cerrar otros menús abiertos (comportamiento accordion)
        this.closeAllMenus(menuItem);
        
        if (!isCurrentlyOpen) {
            // Abrir este menú
            this.openMenu(menuItem, submenu);
        } else {
            // Cerrar este menú
            this.closeMenu(menuItem, submenu);
        }
    }

    openMenu(menuItem, submenu) {
        menuItem.classList.add('pcoded-trigger');
        menuItem.setAttribute('data-auto-expanded', 'true');
        
        // Animación de apertura
        submenu.style.display = 'block';
        submenu.style.opacity = '0';
        submenu.style.visibility = 'visible';
        submenu.style.maxHeight = '0px';
        
        // Force reflow
        submenu.offsetHeight;
        
        // Animate open
        submenu.style.transition = 'all 0.3s ease-in-out';
        submenu.style.opacity = '1';
        submenu.style.maxHeight = '500px';
        
        console.log('SidebarManager: Menú abierto:', menuItem.getAttribute('data-username'));
    }

    closeMenu(menuItem, submenu) {
        // Animación de cierre
        submenu.style.transition = 'all 0.3s ease-in-out';
        submenu.style.opacity = '0';
        submenu.style.maxHeight = '0px';
        
        setTimeout(() => {
            menuItem.classList.remove('pcoded-trigger');
            menuItem.setAttribute('data-auto-expanded', 'false');
            submenu.style.display = 'none';
            submenu.style.visibility = 'hidden';
        }, 300);
        
        console.log('SidebarManager: Menú cerrado:', menuItem.getAttribute('data-username'));
    }

    closeAllMenus(exceptItem = null) {
        const openMenus = document.querySelectorAll('.pcoded-navbar .pcoded-inner-navbar li.pcoded-hasmenu.pcoded-trigger');
        
        openMenus.forEach(menuItem => {
            if (menuItem === exceptItem) return;
            
            const submenu = menuItem.querySelector('.pcoded-submenu');
            if (submenu) {
                this.closeMenu(menuItem, submenu);
            }
        });
    }

    fixHoverStates() {
        // Prevenir estados hover problemáticos
        const navItems = document.querySelectorAll('.pcoded-navbar .pcoded-inner-navbar li.nav-item');
        
        navItems.forEach(item => {
            // Remover clases de hover automático
            item.addEventListener('mouseenter', (e) => {
                // No hacer nada especial en hover para menús dropdown
                if (item.classList.contains('pcoded-hasmenu')) {
                    return;
                }
            });
            
            item.addEventListener('mouseleave', (e) => {
                // Limpiar estados hover residuales
                item.style.background = '';
            });
        });
    }

    setupKeyboardNavigation() {
        const navLinks = document.querySelectorAll('.pcoded-navbar .pcoded-inner-navbar .nav-link');
        
        navLinks.forEach(link => {
            link.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    
                    const menuItem = link.closest('li.pcoded-hasmenu');
                    if (menuItem) {
                        this.handleMenuClick(e);
                    } else {
                        // Navigate to regular link
                        link.click();
                    }
                }
            });
        });
    }

    isCurrentPage(menuItem) {
        // Check if any submenu item matches current page
        const submenuLinks = menuItem.querySelectorAll('.pcoded-submenu a');
        const currentPath = window.location.pathname;
        
        for (const link of submenuLinks) {
            const href = link.getAttribute('href');
            if (href && currentPath.includes(href)) {
                return true;
            }
        }
        
        return false;
    }

    observeMutations() {
        // Observe DOM changes that might re-trigger auto-expansion
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        const hasMenuItems = node.querySelectorAll?.('.pcoded-hasmenu') || [];
                        if (hasMenuItems.length > 0) {
                            setTimeout(() => this.preventAutoExpansion(), 100);
                        }
                    }
                });
            });
        });

        observer.observe(document.querySelector('.pcoded-navbar'), {
            childList: true,
            subtree: true
        });
    }

    // Public methods for external control
    expandMenu(menuSelector) {
        const menuItem = document.querySelector(menuSelector);
        if (menuItem && menuItem.classList.contains('pcoded-hasmenu')) {
            const submenu = menuItem.querySelector('.pcoded-submenu');
            if (submenu) {
                this.openMenu(menuItem, submenu);
            }
        }
    }

    collapseMenu(menuSelector) {
        const menuItem = document.querySelector(menuSelector);
        if (menuItem && menuItem.classList.contains('pcoded-hasmenu')) {
            const submenu = menuItem.querySelector('.pcoded-submenu');
            if (submenu) {
                this.closeMenu(menuItem, submenu);
            }
        }
    }

    collapseAll() {
        this.closeAllMenus();
    }

    // Set active menu item based on current page
    setActivePage() {
        const currentPath = window.location.pathname;
        const allLinks = document.querySelectorAll('.pcoded-navbar .nav-link');
        
        // Remove all active states first
        allLinks.forEach(link => {
            link.classList.remove('active');
            link.closest('li').classList.remove('active');
        });
        
        // Find and set active link
        allLinks.forEach(link => {
            const href = link.getAttribute('href');
            if (href && currentPath.includes(href)) {
                link.classList.add('active');
                link.closest('li').classList.add('active');
                
                // If it's in a submenu, expand parent
                const parentMenu = link.closest('.pcoded-submenu')?.closest('li.pcoded-hasmenu');
                if (parentMenu) {
                    const submenu = parentMenu.querySelector('.pcoded-submenu');
                    this.openMenu(parentMenu, submenu);
                }
            }
        });
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Wait a bit for other scripts to load
    setTimeout(() => {
        window.sidebarManager = new SidebarManager();
        window.sidebarManager.setActivePage();
        console.log('SidebarManager: Inicializado correctamente');
    }, 500);
});

// Reinitialize if page changes (for SPA)
window.addEventListener('popstate', function() {
    if (window.sidebarManager) {
        window.sidebarManager.setActivePage();
    }
});

// Export for external use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SidebarManager;
}