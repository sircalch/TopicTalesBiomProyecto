/**
 * FORCE ICON DISPLAY - TopicTales Biomédica
 * Script para forzar la visualización correcta de iconos en el sidebar
 */
(function() {
    'use strict';
    
    // Mapa de iconos fallback con símbolos unicode
    const iconFallbacks = {
        'bi-heart-pulse': '♥',
        'bi-person-hearts': '👶',
        'bi-gender-female': '♀',
        'bi-apple': '🍎',
        'bi-brain': '🧠',
        'bi-credit-card-fill': '💳',
        'bi-tools': '🔧',
        'bi-person-circle': '👤',
        'bi-people-fill': '👥',
        'bi-hospital': '🏥',
        'bi-eye': '👁',
        'bi-tooth': '🦷',
        'bi-droplet': '💧',
        'bi-bandaid-fill': '🩹',
        'bi-gear-fill': '⚙',
        'bi-chat-dots-fill': '💬',
        'bi-virus': '🦠',
        'bi-speedometer2': '📊',
        'bi-calendar-event-fill': '📅',
        'bi-file-medical-fill': '📋',
        'bi-graph-up-arrow': '📈',
        'bi-files': '📁',
        'bi-award-fill': '🏆',
        'bi-shield-lock': '🔒',
        'bi-sliders': '⚙',
        'bi-clipboard-data': '📊',
        'bi-receipt': '🧾',
        'bi-list-check': '☑',
        'bi-bar-chart': '📊',
        'bi-wrench': '🔧',
        'bi-tags': '🏷',
        'bi-geo-alt': '📍',
        'bi-envelope': '✉',
        'bi-chat': '💬',
        'bi-bell': '🔔',
        'bi-file-text': '📄'
    };
    
    // Función para verificar si un icono se está mostrando correctamente
    function isIconVisible(iconElement) {
        if (!iconElement) return false;
        
        try {
            const computed = window.getComputedStyle(iconElement);
            const beforeContent = window.getComputedStyle(iconElement, '::before').content;
            
            // Si ya tiene texto content, asumimos que está visible
            if (iconElement.textContent && iconElement.textContent.trim() !== '') {
                return true;
            }
            
            // Verificar si el icono tiene contenido visible en ::before
            const hasBeforeContent = (
                beforeContent && 
                beforeContent !== 'none' && 
                beforeContent !== '""' && 
                beforeContent !== "''" &&
                beforeContent !== 'normal'
            );
            
            // Verificar si la fuente Bootstrap Icons está cargada
            const fontFamily = computed.fontFamily || '';
            const hasBootstrapFont = fontFamily.includes('bootstrap-icons');
            
            return hasBeforeContent || hasBootstrapFont;
        } catch (e) {
            // Si hay error accediendo a los estilos, asumir que no es visible
            return false;
        }
    }
    
    // Función para aplicar fallback a un icono
    function applyIconFallback(iconElement) {
        const classList = Array.from(iconElement.classList);
        let fallbackApplied = false;
        
        for (const className of classList) {
            if (iconFallbacks[className]) {
                iconElement.textContent = iconFallbacks[className];
                iconElement.style.fontFamily = 'serif';
                iconElement.style.fontSize = '16px';
                iconElement.style.lineHeight = '1';
                iconElement.style.display = 'inline-block';
                iconElement.style.textAlign = 'center';
                iconElement.style.width = '16px';
                iconElement.style.height = '16px';
                // Marcar que se aplicó fallback pero NO como cargado
                iconElement.setAttribute('data-fallback-applied', 'true');
                fallbackApplied = true;
                break;
            }
        }
        
        if (!fallbackApplied) {
            // Fallback genérico mejorado - usar icono más apropiado
            iconElement.textContent = '⚪';
            iconElement.style.fontFamily = 'serif';
            iconElement.style.fontSize = '14px';
            iconElement.style.color = 'inherit';
            iconElement.setAttribute('data-fallback-applied', 'generic');
        }
    }
    
    // Función principal para verificar y corregir iconos
    function fixSidebarIcons() {
        const sidebarIcons = document.querySelectorAll('.pcoded-navbar .pcoded-micon i');
        let iconsFixed = 0;
        
        sidebarIcons.forEach(function(icon) {
            // Esperar un momento para que los estilos se apliquen
            setTimeout(function() {
                if (isIconVisible(icon)) {
                    // Marcar como cargado correctamente
                    icon.setAttribute('data-icon-loaded', 'true');
                } else {
                    // Aplicar fallback y NO marcar como cargado
                    applyIconFallback(icon);
                    iconsFixed++;
                }
                
                // Asegurar posicionamiento correcto
                icon.style.position = 'static';
                icon.style.top = 'auto';
                icon.style.left = 'auto';
                icon.style.transform = 'none';
                icon.style.margin = '0';
                icon.style.padding = '0';
                icon.style.display = 'inline-block';
                icon.style.verticalAlign = 'middle';
            }, 300);
        });
        
        if (iconsFixed > 0) {
            console.log(`[TopicTales] Se aplicaron fallbacks a ${iconsFixed} iconos del sidebar`);
        }
    }
    
    // Función para corregir espaciado del sidebar
    function fixSidebarSpacing() {
        const navLinks = document.querySelectorAll('.pcoded-navbar .nav-link');
        
        navLinks.forEach(function(link) {
            // Asegurar flexbox layout
            link.style.display = 'flex';
            link.style.alignItems = 'center';
            link.style.padding = '12px 20px';
            link.style.whiteSpace = 'nowrap';
            
            // Corregir contenedor de iconos
            const iconContainer = link.querySelector('.pcoded-micon');
            if (iconContainer) {
                iconContainer.style.width = '24px';
                iconContainer.style.height = '24px';
                iconContainer.style.minWidth = '24px';
                iconContainer.style.marginRight = '12px';
                iconContainer.style.flexShrink = '0';
                iconContainer.style.position = 'static';
                iconContainer.style.display = 'inline-flex';
                iconContainer.style.alignItems = 'center';
                iconContainer.style.justifyContent = 'center';
            }
            
            // Corregir texto
            const textElement = link.querySelector('.pcoded-mtext');
            if (textElement) {
                textElement.style.flex = '1';
                textElement.style.marginLeft = '0';
                textElement.style.whiteSpace = 'nowrap';
                textElement.style.overflow = 'hidden';
                textElement.style.textOverflow = 'ellipsis';
            }
            
            // Corregir badges
            const badge = link.querySelector('.pcoded-badge');
            if (badge) {
                badge.style.marginLeft = 'auto';
                badge.style.flexShrink = '0';
            }
        });
    }
    
    // Ejecutar cuando el DOM esté listo
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            fixSidebarSpacing();
            fixSidebarIcons();
        });
    } else {
        fixSidebarSpacing();
        fixSidebarIcons();
    }
    
    // También ejecutar después de que se carguen los estilos
    window.addEventListener('load', function() {
        setTimeout(function() {
            fixSidebarSpacing();
            fixSidebarIcons();
        }, 800);
    });
    
    // Reejecutar si el sidebar se recarga dinámicamente
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList') {
                const addedNodes = Array.from(mutation.addedNodes);
                const hasNavbarContent = addedNodes.some(node => 
                    node.nodeType === 1 && (
                        node.matches && node.matches('.pcoded-navbar') ||
                        node.querySelector && node.querySelector('.pcoded-navbar')
                    )
                );
                
                if (hasNavbarContent) {
                    setTimeout(function() {
                        fixSidebarSpacing();
                        fixSidebarIcons();
                    }, 200);
                }
            }
        });
    });
    
    // Observar cambios en el documento
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
    
})();