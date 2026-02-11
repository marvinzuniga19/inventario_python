/**
 * Gestor de Temas - Sistema Dinámico de Personalización
 * Maneja cambios de temas, previsualización y persistencia
 */

class ThemeManager {
    constructor() {
        this.currentTheme = null;
        this.isPreviewMode = false;
        this.previewTimeout = null;
        this.themePresets = window.THEME_PRESETS || {};
        
        this.init();
    }

    /**
     * Inicializar el gestor de temas
     */
    init() {
        this.obtenerTemaUsuario();
        this.bindEventos();
        this.aplicarTema(this.currentTheme);
        
        console.log('Theme Manager inicializado:', {
            currentTheme: this.currentTheme,
            availableThemes: Object.keys(this.themePresets)
        });
    }

    /**
     * Obtener el tema del usuario desde meta tags o default
     */
    obtenerTemaUsuario() {
        // Intentar obtener del meta tag
        const temaMeta = document.querySelector('meta[name="current-theme"]');
        if (temaMeta) {
            this.currentTheme = temaMeta.getAttribute('data-theme-name') || 'default';
        } else {
            this.currentTheme = 'default';
        }
        
        // Verificar que el tema exista
        if (!this.themePresets[this.currentTheme]) {
            this.currentTheme = 'default';
        }
    }

    /**
     * Obtener CSRF token del formulario
     */
    obtenerCSRFToken() {
        const csrfToken = document.querySelector('input[name="csrf_token"]');
        return csrfToken ? csrfToken.value : '';
    }

    /**
     * Bind de eventos
     */
    bindEventos() {
        // Botones de previsualización de tema
        document.addEventListener('click', (e) => {
            if (e.target.closest('.preview-theme')) {
                e.preventDefault();
                const button = e.target.closest('.preview-theme');
                const themeName = button.getAttribute('data-theme');
                this.iniciarPrevisualizacion(themeName);
            }
        });

        // Botones de guardar tema
        document.addEventListener('click', (e) => {
            if (e.target.closest('.save-theme')) {
                e.preventDefault();
                const themeName = e.target.closest('.save-theme').getAttribute('data-theme');
                this.guardarTema(themeName);
            }
        });

        // Botones de descartar cambios
        document.addEventListener('click', (e) => {
            if (e.target.closest('.discard-theme')) {
                e.preventDefault();
                this.descartarPrevisualizacion();
            }
        });

        // Auto-guardar después de 30 segundos de previsualización
        this.setupAutoSave();
    }

    /**
     * Aplicar un tema específico
     */
    aplicarTema(themeName) {
        const theme = this.themePresets[themeName];
        if (!theme) {
            console.error(`Tema no encontrado: ${themeName}`);
            return false;
        }

        try {
            // Aplicar variables CSS dinámicamente
            const root = document.documentElement;
            
            // Mapeo de variables CSS a propiedades del tema
            const cssVariables = {
                '--sidebar-gradient-start': theme.gradient_start,
                '--sidebar-gradient-end': theme.gradient_end,
                '--sidebar-text-color': theme.text,
                '--sidebar-text-hover': theme.text_hover,
                '--sidebar-text-inactive': theme.text_hover || theme.text,
                '--sidebar-bg-hover': theme.bg_hover,
                '--sidebar-bg-active': theme.bg_active,
                '--sidebar-border-color': theme.border_color,
                '--sidebar-header-border': theme.header_border,
                '--sidebar-footer-border': theme.footer_border,
                '--sidebar-active-indicator': theme.active_indicator
            };

            // Aplicar cada variable CSS
            Object.entries(cssVariables).forEach(([property, value]) => {
                if (value) {
                    root.style.setProperty(property, value);
                }
            });

            // Actualizar clases de estado en las tarjetas de tema
            this.actualizarEstadoTarjetas(themeName);
            
            console.log(`Tema aplicado: ${themeName}`, cssVariables);
            return true;
            
        } catch (error) {
            console.error(`Error aplicando tema ${themeName}:`, error);
            return false;
        }
    }

    /**
     * Iniciar previsualización de un tema
     */
    iniciarPrevisualizacion(themeName) {
        if (this.isPreviewMode && this.currentPreviewTheme === themeName) {
            return; // Ya estamos previsualizando este tema
        }

        this.isPreviewMode = true;
        this.currentPreviewTheme = themeName;
        
        // Aplicar el tema
        this.aplicarTema(themeName);
        
        // Mostrar indicador de previsualización
        this.mostrarIndicadorPrevisualizacion();
        
        // Configurar auto-guardado
        this.configurarAutoGuardado();
        
        console.log(`Previsualización iniciada: ${themeName}`);
    }

    /**
     * Mostrar indicador de previsualización
     */
    mostrarIndicadorPrevisualizacion() {
        // Eliminar indicador existente
        this.quitarIndicadorPrevisualizacion();
        
        // Crear nuevo indicador
        const indicator = document.createElement('div');
        indicator.className = 'preview-indicator';
        indicator.innerHTML = `
            <div class="spinner-border spinner-border-sm me-2" role="status">
                <span class="visually-hidden">Previsualizando...</span>
            </div>
            <span>Modo Previsualización</span>
            <div class="preview-actions ms-3">
                <button class="btn btn-success btn-sm save-theme" data-theme="${this.currentPreviewTheme}">
                    <i class="bi bi-check"></i> Guardar
                </button>
                <button class="btn btn-secondary btn-sm discard-theme ms-1">
                    <i class="bi bi-x"></i> Descartar
                </button>
            </div>
        `;
        
        // Agregar estilos si no existen
        if (!document.querySelector('#preview-indicator-styles')) {
            const style = document.createElement('style');
            style.id = 'preview-indicator-styles';
            style.textContent = `
                .preview-indicator {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    background: rgba(0, 0, 0, 0.9);
                    color: white;
                    padding: 12px 16px;
                    border-radius: 8px;
                    z-index: 9999;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                    font-size: 14px;
                    backdrop-filter: blur(10px);
                    animation: slideIn 0.3s ease-out;
                }
                
                @keyframes slideIn {
                    from {
                        transform: translateX(100%);
                        opacity: 0;
                    }
                    to {
                        transform: translateX(0);
                        opacity: 1;
                    }
                }
                
                .preview-actions {
                    display: flex;
                    align-items: center;
                }
                
                @media (max-width: 768px) {
                    .preview-indicator {
                        top: 10px;
                        right: 10px;
                        left: 10px;
                        flex-direction: column;
                        align-items: flex-start;
                    }
                    
                    .preview-actions {
                        margin-top: 8px;
                        margin-left: 0;
                    }
                }
            `;
            document.head.appendChild(style);
        }
        
        document.body.appendChild(indicator);
    }

    /**
     * Quitar indicador de previsualización
     */
    quitarIndicadorPrevisualizacion() {
        const existingIndicator = document.querySelector('.preview-indicator');
        if (existingIndicator) {
            existingIndicator.remove();
        }
    }

    /**
     * Guardar un tema (persistir en el servidor)
     */
    async guardarTema(themeName) {
        try {
            // Enviar al servidor
            const response = await fetch('/auth/guardar-tema', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.obtenerCSRFToken()
                },
                body: JSON.stringify({
                    tema_preferido: themeName
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                
                // Actualizar estado
                this.currentTheme = themeName;
                this.isPreviewMode = false;
                this.quitarIndicadorPrevisualizacion();
                
                // Actualizar meta tag
                const temaMeta = document.querySelector('meta[name="current-theme"]');
                if (temaMeta) {
                    temaMeta.setAttribute('data-theme-name', themeName);
                }
                
                // Mostrar mensaje de éxito
                this.mostrarMensaje('Tema guardado exitosamente', 'success');
                
                console.log('Tema guardado:', data);
                
            } else {
                const error = await response.json();
                this.mostrarMensaje('Error al guardar tema: ' + error.error, 'error');
            }
            
        } catch (error) {
            console.error('Error guardando tema:', error);
            this.mostrarMensaje('Error al guardar tema', 'error');
        }
    }

    /**
     * Descartar previsualización y volver al tema original
     */
    descartarPrevisualizacion() {
        this.isPreviewMode = false;
        this.currentPreviewTheme = null;
        
        // Aplicar tema original
        this.aplicarTema(this.currentTheme);
        
        // Quitar indicador
        this.quitarIndicadorPrevisualizacion();
        
        // Limpiar timeout de auto-guardado
        if (this.previewTimeout) {
            clearTimeout(this.previewTimeout);
            this.previewTimeout = null;
        }
        
        this.mostrarMensaje('Cambios descartados', 'info');
        console.log('Previsualización descartada, tema restaurado:', this.currentTheme);
    }

    /**
     * Configurar auto-guardado después de 30 segundos
     */
    configurarAutoGuardado() {
        if (this.previewTimeout) {
            clearTimeout(this.previewTimeout);
        }
        
        this.previewTimeout = setTimeout(() => {
            if (this.isPreviewMode && this.currentPreviewTheme) {
                this.guardarTema(this.currentPreviewTheme);
            }
        }, 30000); // 30 segundos
    }

    /**
     * Actualizar estado visual de las tarjetas de tema
     */
    actualizarEstadoTarjetas(activeTheme) {
        document.querySelectorAll('.theme-card').forEach(card => {
            const themeName = card.getAttribute('data-theme');
            
            // Quitar todas las clases de estado
            card.classList.remove('active', 'previewing');
            
            // Agregar clase correspondiente
            if (themeName === this.currentTheme && !this.isPreviewMode) {
                card.classList.add('active');
            } else if (themeName === this.currentPreviewTheme && this.isPreviewMode) {
                card.classList.add('previewing');
            }
        });
    }

    /**
     * Mostrar mensaje al usuario
     */
    mostrarMensaje(mensaje, tipo = 'success') {
        // Crear toast de notificación
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${tipo === 'success' ? 'success' : 'danger'} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${mensaje}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;

        // Agregar al contenedor de toasts o crear uno
        let container = document.querySelector('.toast-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            document.body.appendChild(container);
        }

        container.appendChild(toast);

        // Mostrar toast
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();

        // Remover después de ocultar
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    }

    /**
     * Obtener resumen para debugging
     */
    obtenerResumen() {
        return {
            currentTheme: this.currentTheme,
            isPreviewMode: this.isPreviewMode,
            previewTheme: this.currentPreviewTheme,
            availableThemes: Object.keys(this.themePresets),
            totalThemes: Object.keys(this.themePresets).length
        };
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    // Solo inicializar si hay selector de temas en la página
    if (document.querySelector('.theme-selector') || document.querySelector('[data-theme]')) {
        window.themeManager = new ThemeManager();
        
        // Debug en consola
        console.log('Theme Manager inicializado:', window.themeManager.obtenerResumen());
    }
});

// Exportar para uso global
window.ThemeManager = ThemeManager;