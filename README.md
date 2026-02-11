# Sistema de Gestión de Inventario

Una aplicación web moderna y responsiva para la gestión de inventario de pequeños negocios, desarrollada con Python Flask y Bootstrap 5.

## 🚀 Características

### 🔐 Autenticación y Seguridad
- Sistema de registro y login de usuarios
- Roles de usuario (Administrador/Empleado)
- Contraseñas encriptadas con Werkzeug
- Sesiones seguras

### 📊 Dashboard Principal
- Estadísticas en tiempo real del inventario
- Valor total del stock
- Alertas de productos con bajo stock
- Actividad reciente de movimientos
- Interfaz moderna con tarjetas informativas

### 📦 Gestión de Productos
- **CRUD completo** de productos
- Campos: Nombre, SKU, Categoría, Precio, Stock, Umbral mínimo, Descripción, Imagen
- Subida de imágenes para productos
- Búsqueda y filtros avanzados
- Estados de stock visual (Normal/Bajo/Sin stock)
- Paginación de resultados
- Validación de SKU único

### 🏷️ Gestión de Categorías
- Crear y gestionar categorías
- Asignar colores personalizados a categorías
- Organización de productos por categorías

### 📋 Movimientos de Stock
- Registro de entradas y salidas
- Historial completo de movimientos
- Actualización automática del stock
- Referencia de documentos (facturas, órdenes de compra)

### 🎨 Interfaz de Usuario
- **Sidebar responsivo** con navegación intuitiva
- **Diseño moderno** con Bootstrap 5
- **Totalmente en español**
- **Completamente responsiva** para móviles y tabletas
- Indicadores visuales de alertas
- Animaciones y transiciones suaves
- Tema profesional y corporativo

### ⚡ Sistema de Alertas
- Alertas en sidebar para productos bajo stock
- Notificaciones visuales en tiempo real
- Contadores de elementos críticos
- Priorización por niveles de urgencia

## 🛠️ Stack Tecnológico

### Backend
- **Python 3.8+** (compatible con 3.14.2) con **Flask** como framework principal
- **Flask-SQLAlchemy** para ORM y gestión de base de datos
- **Flask-Login** para autenticación
- **Flask-WTF** para formularios seguros
- **Flask-Migrate** para migraciones de base de datos
- **SQLite** para base de datos ligera y portable

### Frontend
- **Bootstrap 5** para diseño responsivo
- **Bootstrap Icons** para iconos modernos
- **JavaScript vanilla** para interactividad
- **Jinja2** para templates dinámicos

## 📦 Instalación

### Prerrequisitos
- Python 3.8 o superior (probado con Python 3.14.2)
- pip (gestor de paquetes de Python)

### Pasos de Instalación

1. **Clonar o descargar el proyecto**

2. **Crear y activar entorno virtual:**
   
   **Linux/macOS:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
   
   **Windows:**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Inicializar base de datos:**
   ```bash
   python init_db.py
   ```

5. **Iniciar aplicación:**
   ```bash
   python run.py
   ```

6. **Acceder a la aplicación:**
   - URL: `http://localhost:5000`
   - Email: `admin@inventario.com`
   - Contraseña: `admin123`

### 📋 Notas Importantes

- **Compatibilidad:** El proyecto es compatible con Python 3.8+ y ha sido probado exitosamente con Python 3.14.2
- **Entorno virtual:** Es obligatorio usar un entorno virtual para evitar conflictos de dependencias
- **Instalación automática:** Se recomienda usar `pip install -r requirements.txt` para instalar todas las dependencias con las versiones correctas
- **Base de datos:** Se crea automáticamente la primera vez que se ejecuta `init_db.py`

## 📁 Estructura del Proyecto

```
inventario_app/
├── app/
│   ├── __init__.py              # Inicialización de Flask
│   ├── config.py                # Configuración de la aplicación
│   ├── models/                  # Modelos de base de datos
│   │   ├── usuario.py          # Modelo de usuarios
│   │   ├── producto.py         # Modelo de productos
│   │   ├── categoria.py        # Modelo de categorías
│   │   └── movimiento.py       # Modelo de movimientos
│   ├── routes/                  # Rutas de la aplicación
│   │   ├── auth.py             # Autenticación
│   │   ├── main.py             # Dashboard principal
│   │   ├── productos.py        # CRUD de productos
│   │   ├── categorias.py       # CRUD de categorías
│   │   └── movimientos.py      # Movimientos de stock
│   ├── forms/                   # Formularios WTForms
│   │   ├── auth_forms.py       # Formularios de autenticación
│   │   └── producto_forms.py   # Formularios de productos
│   ├── templates/               # Plantillas HTML
│   │   ├── base.html          # Layout principal
│   │   ├── auth/              # Templates de autenticación
│   │   ├── dashboard/         # Templates del dashboard
│   │   ├── productos/         # Templates de productos
│   │   ├── categorias/        # Templates de categorías
│   │   └── movimientos/       # Templates de movimientos
│   └── static/                 # Archivos estáticos
│       ├── css/               # Estilos CSS
│       ├── js/                # JavaScript
│       └── uploads/           # Imágenes de productos
├── migrations/                 # Migraciones de base de datos
├── requirements.txt            # Dependencias Python
├── init_db.py                 # Script de inicialización
├── run.py                     # Punto de entrada de la aplicación
└── README.md                  # Este archivo
```

## 🎯 Uso de la Aplicación

### Primeros Pasos
1. Inicia sesión con las credenciales de administrador
2. Explora el dashboard para ver las estadísticas iniciales
3. Navega por el menú lateral para gestionar productos, categorías y movimientos

### Gestión de Productos
- **Crear productos:** Complete todos los campos obligatorios
- **Editar productos:** Modifique precios, stock, descripciones
- **Buscar productos:** Use el buscador y filtros por categoría/estado
- **Estados de stock:** La aplicación alerta automáticamente sobre stock bajo

### Gestión de Categorías
- **Crear categorías:** Asigne nombres y colores para mejor organización
- **Asignar productos:** Vincule productos a categorías existentes

### Movimientos de Stock
- **Registrar entradas:** Añada stock por compras, devoluciones, etc.
- **Registrar salidas:** Registre ventas, pérdidas, ajustes
- **Historial completo:** Consulte todos los movimientos con detalles

## 🔧 Características Técnicas

### 🔧 Configuración del Entorno
- **Entorno virtual:** El proyecto incluye un entorno virtual configurado (`venv/`) con todas las dependencias necesarias
- **Gestión de dependencias:** `requirements.txt` con versiones específicas para garantizar compatibilidad
- **Sistema operativo:** Compatible con Windows, macOS y Linux

### Base de Datos
- **SQLite** por defecto (fácil para pequeñas empresas)
- **Modelos relacionales** con SQLAlchemy
- **Migraciones automáticas** con Flask-Migrate
- **Integridad referencial** garantizada

### Seguridad
- **CSRF Protection** en todos los formularios
- **Contraseñas hasheadas** con bcrypt
- **Validación de entrada** en todos los campos
- **Sesiones seguras** con Flask-Login

### Rendimiento
- **Consultas optimizadas** con SQLAlchemy
- **Paginación** para grandes listados
- **Carga diferida** de relaciones
- **Caching básico** para datos frecuentes

## 🚀 Despliegue

Para desplegar en producción:

### Opción 1: Heroku
1. Crear archivo `Procfile`
2. Configurar variables de entorno
3. Usar PostgreSQL como base de datos

### Opción 2: PythonAnywhere
1. Subir archivos vía FTP o Git
2. Configurar virtualenv
3. Configurar aplicación web

### Opción 3: Docker
1. Crear `Dockerfile`
2. Construir imagen
3. Ejecutar contenedor

## 🔄 Actualizaciones Futuras

### Funcionalidades Planeadas
- [ ] **Sistema de reportes** con gráficos y exportación PDF
- [ ] **Gestión de proveedores** con catálogo de productos
- [ ] **Notificaciones por email** para alertas críticas
- [ ] **API REST** para integración con sistemas externos
- [ ] **Modo offline** con sincronización automática
- [ ] **Código de barras/QR** para escaneo rápido
- [ ] **Multi-almacén** con transferencias entre ubicaciones
- [ ] **Backup automático** y restauración de datos

### Mejoras Técnicas
- [ ] **Tests unitarios** con pytest
- [ ] **CI/CD** automatizado
- [ ] **Monitoreo** y logging avanzado
- [ ] **Optimización** de consultas
- [ ] **Caching** con Redis

## 🤝 Contribución

1. Fork del proyecto
2. Crear feature branch
3. Commits descriptivos
4. Pull request con descripción clara

## 📄 Licencia

Este proyecto está licenciado bajo MIT License.

## 📞 Soporte

Para soporte técnico:
- **Issues de GitHub:** Reportar bugs y solicitudes
- **Documentación:** Revisar sección de Uso
- **Email:** Contactar al desarrollador

---

**Desarrollado con ❤️ para facilitar la gestión de inventarios en pequeñas empresas**