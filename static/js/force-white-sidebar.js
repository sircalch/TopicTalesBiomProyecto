/* ============================================================
   FORCE WHITE SIDEBAR TEXT - JavaScript Backup
   Forzar colores blancos desde JavaScript como respaldo
   ============================================================ */

class SidebarColorForcer {
    constructor() {
        this.init();
    }

    init() {
        console.log('SidebarColorForcer: Iniciando corrección de colores...');
        this.forceWhiteColors();
        this.observeChanges();
        
        // Aplicar cada segundo durante los primeros 10 segundos
        for (let i = 1; i <= 10; i++) {
            setTimeout(() => this.forceWhiteColors(), i * 1000);
        }
    }

    forceWhiteColors() {
        try {
            // Seleccionar todos los elementos del sidebar
            const navItems = document.querySelectorAll('.pcoded-navbar .pcoded-inner-navbar li.nav-item');
            
            navItems.forEach(item => {
                // Links principales
                const link = item.querySelector('.nav-link');
                if (link) {
                    link.style.color = '#ffffff';
                    link.style.setProperty('color', '#ffffff', 'important');
                }

                // Iconos
                const icons = item.querySelectorAll('.pcoded-micon i');
                icons.forEach(icon => {
                    icon.style.color = '#ffffff';
                    icon.style.setProperty('color', '#ffffff', 'important');
                });

                // Texto de menú
                const mtext = item.querySelector('.pcoded-mtext');
                if (mtext) {
                    mtext.style.color = '#ffffff';
                    mtext.style.setProperty('color', '#ffffff', 'important');
                }

                // Submenu items
                const submenuLinks = item.querySelectorAll('.pcoded-submenu a');
                submenuLinks.forEach(submenuLink => {
                    submenuLink.style.color = 'rgba(255, 255, 255, 0.85)';
                    submenuLink.style.setProperty('color', 'rgba(255, 255, 255, 0.85)', 'important');
                });
            });

            // Títulos de sección
            const captions = document.querySelectorAll('.pcoded-navbar .pcoded-menu-caption label');
            captions.forEach(caption => {
                caption.style.color = 'rgba(255, 255, 255, 0.7)';
                caption.style.setProperty('color', 'rgba(255, 255, 255, 0.7)', 'important');
            });

            // Brand title
            const brandTitle = document.querySelector('.pcoded-navbar .navbar-brand .b-title');
            if (brandTitle) {
                brandTitle.style.color = '#ffffff';
                brandTitle.style.setProperty('color', '#ffffff', 'important');
            }

            console.log('SidebarColorForcer: Colores aplicados correctamente');
        } catch (error) {
            console.error('SidebarColorForcer: Error aplicando colores:', error);
        }
    }

    observeChanges() {
        // Observer para cambios en el DOM
        const observer = new MutationObserver(() => {
            setTimeout(() => this.forceWhiteColors(), 100);
        });

        const sidebar = document.querySelector('.pcoded-navbar');
        if (sidebar) {
            observer.observe(sidebar, {
                childList: true,
                subtree: true,
                attributes: true,
                attributeFilter: ['style', 'class']
            });
        }
    }

    // Método público para forzar colores manualmente
    force() {
        this.forceWhiteColors();
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    // Esperar a que otros scripts se carguen
    setTimeout(() => {
        window.sidebarColorForcer = new SidebarColorForcer();
        console.log('SidebarColorForcer: Inicializado correctamente');
    }, 1000);
});

// También ejecutar cuando la página esté completamente cargada
window.addEventListener('load', function() {
    setTimeout(() => {
        if (window.sidebarColorForcer) {
            window.sidebarColorForcer.force();
        }
    }, 500);
});

// Función global para debugging
window.forceSidebarColors = function() {
    if (window.sidebarColorForcer) {
        window.sidebarColorForcer.force();
        console.log('Colores del sidebar forzados manualmente');
    } else {
        console.log('SidebarColorForcer no está disponible');
    }
};