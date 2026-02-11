/**
 * Gestor de Monedas - Sistema Dinámico de Monedas
 * Maneja cambios de moneda, conversiones y formateo en tiempo real
 */

class CurrencyManager {
    constructor() {
        this.monedaActual = this.obtenerMonedaActual();
        this.tasasDeCambio = {};
        this.isLoading = false;
        
        this.init();
    }

    /**
     * Inicializar el gestor de monedas
     */
    init() {
        this.cargarTasasDeCambio();
        this.bindEventos();
        this.actualizarPreciosEnPagina();
    }

    /**
     * Obtener moneda actual del usuario
     */
    obtenerMonedaActual() {
        // Intentar obtener del localStorage primero
        const monedaGuardada = localStorage.getItem('userCurrency');
        if (monedaGuardada) {
            return JSON.parse(monedaGuardada);
        }

        // Obtener del meta tag o data attribute
        const monedaMeta = document.querySelector('meta[name="current-currency"]');
        if (monedaMeta) {
            const monedaData = {
                id: monedaMeta.getAttribute('data-currency-id'),
                codigo: monedaMeta.getAttribute('data-currency-code'),
                simbolo: monedaMeta.getAttribute('data-currency-symbol'),
                locale: monedaMeta.getAttribute('data-currency-locale')
            };
            this.guardarMonedaActual(monedaData);
            return monedaData;
        }

        // Moneda por defecto
        return {
            id: '1',
            codigo: 'NIO',
            simbolo: 'C$',
            locale: 'es-NI'
        };
    }

    /**
     * Guardar moneda actual en localStorage
     */
    guardarMonedaActual(moneda) {
        localStorage.setItem('userCurrency', JSON.stringify(moneda));
        this.monedaActual = moneda;
    }

    /**
     * Cargar tasas de cambio desde la API
     */
    async cargarTasasDeCambio() {
        try {
            const response = await fetch('/monedas/api/tasas');
            if (response.ok) {
                const data = await response.json();
                this.tasasDeCambio = data.tasas_cambio || {};
                console.log('Tasas de cambio cargadas:', this.tasasDeCambio);
            }
        } catch (error) {
            console.error('Error cargando tasas de cambio:', error);
            // Usar tasas de respaldo
            this.tasasDeCambio = this.getTasasRespaldo();
        }
    }

    /**
     * Tasas de cambio de respaldo si API falla
     */
    getTasasRespaldo() {
        return {
            'MXN': 2.10,    // 1 NIO = 2.10 MXN
            'USD': 0.0274,   // 1 NIO = 0.0274 USD
            'COP': 117.5     // 1 NIO = 117.5 COP
        };
    }

    /**
     * Bind de eventos
     */
    bindEventos() {
        // Selector de moneda
        document.addEventListener('click', (e) => {
            if (e.target.closest('.currency-option')) {
                e.preventDefault();
                const opcion = e.target.closest('.currency-option');
                this.cambiarMoneda({
                    id: opcion.getAttribute('data-moneda-id'),
                    codigo: opcion.getAttribute('data-moneda-codigo'),
                    simbolo: opcion.getAttribute('data-moneda-simbolo')
                });
            }
        });

        // Auto-recargar tasas cada 5 minutos
        setInterval(() => {
            this.cargarTasasDeCambio();
        }, 5 * 60 * 1000);
    }

    /**
     * Cambiar moneda del usuario
     */
    async cambiarMoneda(nuevaMoneda) {
        if (this.isLoading || nuevaMoneda.codigo === this.monedaActual.codigo) {
            return;
        }

        this.mostrarLoading(true);

        try {
            // Enviar cambio al servidor
            const response = await fetch('/monedas/cambiar-moneda', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `moneda_id=${nuevaMoneda.id}`
            });

            if (response.ok) {
                const data = await response.json();
                
                // Actualizar moneda actual
                this.guardarMonedaActual(nuevaMoneda);
                
                // Actualizar UI
                this.actualizarUIMoneda(nuevaMoneda);
                this.actualizarPreciosEnPagina();
                
                // Mostrar mensaje de éxito
                this.mostrarMensaje(data.message, 'success');
                
                // Recargar página para actualizaciones completas
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            } else {
                const error = await response.json();
                this.mostrarMensaje(error.error, 'error');
            }
        } catch (error) {
            console.error('Error cambiando moneda:', error);
            this.mostrarMensaje('Error al cambiar moneda', 'error');
        } finally {
            this.mostrarLoading(false);
        }
    }

    /**
     * Actualizar UI con nueva moneda
     */
    actualizarUIMoneda(moneda) {
        // Actualizar selector
        const symbolEl = document.querySelector('.currency-symbol');
        const codeEl = document.querySelector('.currency-code');
        
        if (symbolEl) symbolEl.textContent = moneda.simbolo;
        if (codeEl) codeEl.textContent = moneda.codigo;

        // Actualizar meta tags
        const metaTag = document.querySelector('meta[name="current-currency"]');
        if (metaTag) {
            metaTag.setAttribute('data-currency-code', moneda.codigo);
            metaTag.setAttribute('data-currency-symbol', moneda.simbolo);
        }
    }

    /**
     * Actualizar todos los precios en la página
     */
    actualizarPreciosEnPagina() {
        // Precios de productos
        document.querySelectorAll('.precio-moneda').forEach(el => {
            this.actualizarPrecioProducto(el);
        });

        // Valores totales
        document.querySelectorAll('.valor-total-moneda, .valor-inventario-moneda').forEach(el => {
            this.actualizarValorTotal(el);
        });
    }

    /**
     * Actualizar precio de un producto
     */
    actualizarPrecioProducto(el) {
        const precioBase = parseFloat(el.getAttribute('data-precio-base'));
        const monedaOrigen = el.getAttribute('data-moneda-origen') || 'NIO';
        
        if (isNaN(precioBase)) return;

        const precioConvertido = this.convertirPrecio(precioBase, monedaOrigen, this.monedaActual.codigo);
        const precioFormateado = this.formatearPrecio(precioConvertido, this.monedaActual.locale);
        
        el.textContent = precioFormateado;
        el.setAttribute('data-precio-actual', precioConvertido);
    }

    /**
     * Actualizar valor total
     */
    actualizarValorTotal(el) {
        const valorBase = parseFloat(el.getAttribute('data-valor-base'));
        
        if (isNaN(valorBase)) return;

        // Asumimos que los valores totales ya están en NIO
        let valorConvertido = valorBase;
        
        if (this.monedaActual.codigo !== 'NIO') {
            valorConvertido = this.convertirPrecio(valorBase, 'NIO', this.monedaActual.codigo);
        }
        
        const valorFormateado = this.formatearPrecio(valorConvertido, this.monedaActual.locale);
        el.textContent = valorFormateado;
    }

    /**
     * Convertir precio entre monedas
     */
    convertirPrecio(monto, monedaOrigen, monedaDestino) {
        if (monedaOrigen === monedaDestino) {
            return monto;
        }

        // Buscar tasa directa
        const tasaDirecta = this.tasasDeCambio[monedaDestino];
        if (tasaDirecta && monedaOrigen === 'NIO') {
            return monto * tasaDirecta.tasa;
        }

        // Intentar conversión inversa
        const tasaInversa = this.tasasDeCambio[monedaOrigen];
        if (tasaInversa && monedaDestino === 'NIO') {
            return monto / tasaInversa.tasa;
        }

        // Usar tasas de respaldo si no hay tasas de API
        const tasasRespaldo = this.getTasasRespaldo();
        if (monedaOrigen === 'NIO' && tasasRespaldo[monedaDestino]) {
            return monto * tasasRespaldo[monedaDestino];
        }
        if (monedaDestino === 'NIO' && tasasRespaldo[monedaOrigen]) {
            return monto / tasasRespaldo[monedaOrigen];
        }

        return monto; // Retornar original si no se puede convertir
    }

    /**
     * Formatear precio según locale
     */
    formatearPrecio(monto, locale) {
        try {
            switch (locale) {
                case 'es-NI':  // Nicaragua
                    return `C$${monto.toLocaleString('es-NI', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
                case 'es-MX':  // México
                    return `$${monto.toLocaleString('es-MX', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} MXN`;
                case 'en-US':  // Estados Unidos
                    return `$${monto.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} USD`;
                case 'es-CO':  // Colombia
                    return `$${monto.toLocaleString('es-CO', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`;
                default:
                    return `$${monto.toLocaleString('es-NI', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
            }
        } catch (error) {
            return `$${monto.toFixed(2)}`;
        }
    }

    /**
     * Mostrar/ocultar loading
     */
    mostrarLoading(mostrar) {
        this.isLoading = mostrar;
        const loadingEl = document.getElementById('currencyLoading');
        if (loadingEl) {
            loadingEl.style.display = mostrar ? 'flex' : 'none';
        }
    }

    /**
     * Mostrar mensaje al usuario
     */
    mostrarMensaje(mensaje, tipo) {
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
     * Obtener resumen de monedas para debugging
     */
    obtenerResumen() {
        return {
            monedaActual: this.monedaActual,
            totalTasas: Object.keys(this.tasasDeCambio).length,
            preciosActualizados: document.querySelectorAll('.precio-moneda[data-precio-actual]').length
        };
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    // Solo inicializar si hay selector de moneda en la página
    if (document.querySelector('.currency-selector')) {
        window.currencyManager = new CurrencyManager();
        
        // Debug en consola
        console.log('Currency Manager inicializado:', window.currencyManager.obtenerResumen());
    }
});

// Exportar para uso global
window.CurrencyManager = CurrencyManager;