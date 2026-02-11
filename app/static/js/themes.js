/**
 * Definición de Paletas de Colores Predefinidas para el Sidebar
 * Cada tema incluye todos los colores necesarios para personalizar la interfaz
 */

const THEME_PRESETS = {
    // Tema Default (Azul actual)
    default: {
        nombre: 'Azul Default',
        descripcion: 'Profesional y moderno - Azul corporativo',
        gradient_start: '#4f46e5',
        gradient_end: '#6366f1',
        text: 'white',
        text_hover: 'rgba(255, 255, 255, 0.9)',
        bg_hover: 'rgba(255, 255, 255, 0.1)',
        bg_active: 'rgba(255, 255, 255, 0.15)',
        border_color: 'rgba(255, 255, 255, 0.2)',
        header_border: 'rgba(255, 255, 255, 0.1)',
        footer_border: 'rgba(255, 255, 255, 0.1)',
        active_indicator: 'white'
    },

    // Océano Azul
    blue_ocean: {
        nombre: 'Océano Azul',
        descripcion: 'Fresco y corporativo - Tonos azules marinos',
        gradient_start: '#0891b2',
        gradient_end: '#06b6d4',
        text: 'white',
        text_hover: 'rgba(255, 255, 255, 0.9)',
        bg_hover: 'rgba(255, 255, 255, 0.1)',
        bg_active: 'rgba(255, 255, 255, 0.15)',
        border_color: 'rgba(255, 255, 255, 0.2)',
        header_border: 'rgba(255, 255, 255, 0.1)',
        footer_border: 'rgba(255, 255, 255, 0.1)',
        active_indicator: 'white'
    },

    // Bosque Verde
    green_forest: {
        nombre: 'Bosque Verde',
        descripcion: 'Natural y eco-friendly - Tonos verdes frescos',
        gradient_start: '#059669',
        gradient_end: '#10b981',
        text: 'white',
        text_hover: 'rgba(255, 255, 255, 0.9)',
        bg_hover: 'rgba(255, 255, 255, 0.1)',
        bg_active: 'rgba(255, 255, 255, 0.15)',
        border_color: 'rgba(255, 255, 255, 0.2)',
        header_border: 'rgba(255, 255, 255, 0.1)',
        footer_border: 'rgba(255, 255, 255, 0.1)',
        active_indicator: 'white'
    },

    // Noche Púrpura
    purple_night: {
        nombre: 'Noche Púrpura',
        descripcion: 'Creativo y moderno - Tonos púrpura elegantes',
        gradient_start: '#7c3aed',
        gradient_end: '#8b5cf6',
        text: 'white',
        text_hover: 'rgba(255, 255, 255, 0.9)',
        bg_hover: 'rgba(255, 255, 255, 0.1)',
        bg_active: 'rgba(255, 255, 255, 0.15)',
        border_color: 'rgba(255, 255, 255, 0.2)',
        header_border: 'rgba(255, 255, 255, 0.1)',
        footer_border: 'rgba(255, 255, 255, 0.1)',
        active_indicator: 'white'
    },

    // Atardecer Naranja
    orange_sunset: {
        nombre: 'Atardecer Naranja',
        descripcion: 'Energético y cálido - Tonos naranja vibrantes',
        gradient_start: '#ea580c',
        gradient_end: '#f97316',
        text: 'white',
        text_hover: 'rgba(255, 255, 255, 0.9)',
        bg_hover: 'rgba(255, 255, 255, 0.1)',
        bg_active: 'rgba(255, 255, 255, 0.15)',
        border_color: 'rgba(255, 255, 255, 0.2)',
        header_border: 'rgba(255, 255, 255, 0.1)',
        footer_border: 'rgba(255, 255, 255, 0.1)',
        active_indicator: 'white'
    },

    // Oscuro Minimalista
    dark_minimal: {
        nombre: 'Oscuro Minimalista',
        descripcion: 'Elegante y profesional - Tonos grises oscuros',
        gradient_start: '#1f2937',
        gradient_end: '#374151',
        text: 'white',
        text_hover: 'rgba(255, 255, 255, 0.9)',
        bg_hover: 'rgba(255, 255, 255, 0.05)',
        bg_active: 'rgba(255, 255, 255, 0.1)',
        border_color: 'rgba(255, 255, 255, 0.1)',
        header_border: 'rgba(255, 255, 255, 0.05)',
        footer_border: 'rgba(255, 255, 255, 0.05)',
        active_indicator: '#6b7280'
    },

    // Rosa Moderno
    rose_modern: {
        nombre: 'Rosa Moderno',
        descripcion: 'Diseño y creatividad - Tonos rosas contemporáneos',
        gradient_start: '#e11d48',
        gradient_end: '#f43f5e',
        text: 'white',
        text_hover: 'rgba(255, 255, 255, 0.9)',
        bg_hover: 'rgba(255, 255, 255, 0.1)',
        bg_active: 'rgba(255, 255, 255, 0.15)',
        border_color: 'rgba(255, 255, 255, 0.2)',
        header_border: 'rgba(255, 255, 255, 0.1)',
        footer_border: 'rgba(255, 255, 255, 0.1)',
        active_indicator: 'white'
    },

    // Cielo Azul Claro
    sky_light: {
        nombre: 'Cielo Azul Claro',
        descripcion: 'Ligero y aéreo - Tonos azules claros',
        gradient_start: '#0284c7',
        gradient_end: '#0ea5e9',
        text: 'white',
        text_hover: 'rgba(255, 255, 255, 0.9)',
        bg_hover: 'rgba(255, 255, 255, 0.1)',
        bg_active: 'rgba(255, 255, 255, 0.15)',
        border_color: 'rgba(255, 255, 255, 0.2)',
        header_border: 'rgba(255, 255, 255, 0.1)',
        footer_border: 'rgba(255, 255, 255, 0.1)',
        active_indicator: 'white'
    }
};

// Exportar para uso en otros módulos
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { THEME_PRESETS };
}

// Disponibilidad global para el navegador
if (typeof window !== 'undefined') {
    window.THEME_PRESETS = THEME_PRESETS;
}