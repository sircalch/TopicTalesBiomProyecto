/**
 * NAVBAR SIDEBAR SYNC - TopicTales Biomédica
 * Script para sincronizar el navbar con el estado del sidebar (colapsado/expandido)
 */
(function() {
    'use strict';
    
    // Función para detectar si el sidebar está colapsado
    function isSidebarCollapsed() {
        const navbar = document.querySelector('.pcoded-navbar');
        if (!navbar) return false;
        
        // Verificar diferentes clases que indican sidebar colapsado
        return (
            navbar.classList.contains('navbar-minimize') ||
            navbar.classList.contains('pcoded-navbar-hide') ||
            document.body.classList.contains('navbar-collapsed') ||
            navbar.classList.contains('menu-collapsed') ||
            getComputedStyle(navbar).width === '70px' ||
            getComputedStyle(navbar).transform.includes('translateX(-')
        );
    }
    
    // Función para actualizar el estado del navbar
    function updateNavbarState() {
        const header = document.querySelector('.pcoded-header');
        const body = document.body;
        
        if (!header) return;
        
        if (isSidebarCollapsed()) {
            // Sidebar colapsado - ajustar navbar
            body.classList.add('navbar-collapsed');
            header.classList.add('sidebar-collapsed');
            
            console.log('[TopicTales] Sidebar colapsado - Navbar ajustado');
        } else {
            // Sidebar expandido - navbar normal
            body.classList.remove('navbar-collapsed');
            header.classList.remove('sidebar-collapsed');
            
            console.log('[TopicTales] Sidebar expandido - Navbar normal');
        }
    }
    
    // Función para observar cambios en el sidebar
    function observeSidebarChanges() {
        const navbar = document.querySelector('.pcoded-navbar');
        if (!navbar) return;
        
        // Observer para cambios de clase
        const classObserver = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
                    setTimeout(updateNavbarState, 50);
                }
            });
        });
        
        classObserver.observe(navbar, {
            attributes: true,
            attributeFilter: ['class']
        });
        
        // Observer para cambios de estilo
        const styleObserver = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'attributes' && mutation.attributeName === 'style') {
                    setTimeout(updateNavbarState, 50);
                }
            });
        });
        
        styleObserver.observe(navbar, {
            attributes: true,
            attributeFilter: ['style']
        });
        
        // Observer para cambios en el body
        const bodyObserver = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
                    setTimeout(updateNavbarState, 50);
                }
            });
        });
        
        bodyObserver.observe(document.body, {
            attributes: true,
            attributeFilter: ['class']
        });
        
        console.log('[TopicTales] Observadores de sidebar iniciados');
    }
    
    // Función para manejar clicks en el toggle del sidebar
    function attachToggleHandlers() {
        // Botones de toggle comunes
        const toggleSelectors = [
            '#mobile-collapse',
            '#mobile-collapse1',
            '.mobile-menu',
            '.navbar-toggle',
            '.pcoded-navbar-toggle',
            '[data-toggle="sidebar"]',
            '.sidebar-toggle'
        ];
        
        toggleSelectors.forEach(function(selector) {
            const elements = document.querySelectorAll(selector);
            elements.forEach(function(element) {
                element.addEventListener('click', function() {
                    // Esperar a que la animación termine
                    setTimeout(updateNavbarState, 300);
                });
            });
        });
        
        console.log('[TopicTales] Handlers de toggle del sidebar adjuntados');
    }
    
    // Función para verificar el estado inicial
    function checkInitialState() {
        setTimeout(function() {
            updateNavbarState();
            
            // Verificar nuevamente después de que se carguen los estilos
            setTimeout(updateNavbarState, 500);
            setTimeout(updateNavbarState, 1000);
        }, 100);
    }
    
    // Función para manejar redimensionamiento de ventana
    function handleWindowResize() {
        window.addEventListener('resize', function() {
            setTimeout(updateNavbarState, 100);
        });
    }
    
    // Inicialización
    function init() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', function() {
                checkInitialState();
                observeSidebarChanges();
                attachToggleHandlers();
                handleWindowResize();
            });
        } else {
            checkInitialState();
            observeSidebarChanges();
            attachToggleHandlers();
            handleWindowResize();
        }
        
        // También ejecutar después de que la página se cargue completamente
        window.addEventListener('load', function() {
            setTimeout(function() {
                checkInitialState();
                observeSidebarChanges();
                attachToggleHandlers();
            }, 200);
        });
    }
    
    // Función de debug para verificar el estado
    window.debugNavbarSidebar = function() {
        console.log('=== DEBUG NAVBAR-SIDEBAR ===');
        console.log('Sidebar colapsado:', isSidebarCollapsed());
        
        const navbar = document.querySelector('.pcoded-navbar');
        if (navbar) {
            console.log('Clases del sidebar:', navbar.className);
            console.log('Ancho del sidebar:', getComputedStyle(navbar).width);
            console.log('Transform del sidebar:', getComputedStyle(navbar).transform);
        }
        
        const header = document.querySelector('.pcoded-header');
        if (header) {
            console.log('Clases del header:', header.className);
            console.log('Left del header:', getComputedStyle(header).left);
            console.log('Width del header:', getComputedStyle(header).width);
        }
        
        console.log('Clases del body:', document.body.className);
        console.log('=== FIN DEBUG ===');
    };
    
    // Iniciar
    init();
    
})();