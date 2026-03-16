#!/usr/bin/env python3
"""
Script para inicializar la base de datos con datos iniciales
"""

import sys
import os
from dotenv import load_dotenv

load_dotenv()

# Agregar el directorio actual al path para poder importar los módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.usuario import Usuario
from app.models.categoria import Categoria
from app.models.producto import Producto
from app.models.moneda import Moneda


def init_db():
    """Inicializar la base de datos con datos de ejemplo"""
    app = create_app()

    with app.app_context():
        # Crear todas las tablas
        db.create_all()

        # Crear monedas de ejemplo
        monedas_data = [
            ("NIO", "Córdoba Nicaraguense", "C$", "es-NI", True),
            ("USD", "Dólar Estadounidense", "$", "en-US", False),
            ("MXN", "Peso Mexicano", "$", "es-MX", False),
            ("COP", "Peso Colombiano", "$", "es-CO", False),
        ]

        for codigo, nombre, simbolo, locale, es_default in monedas_data:
            moneda = Moneda.query.filter_by(codigo=codigo).first()
            if not moneda:
                moneda = Moneda(
                    codigo=codigo,
                    nombre=nombre,
                    simbolo=simbolo,
                    locale=locale,
                    es_default=es_default,
                )
                db.session.add(moneda)

        print("✓ Monedas de ejemplo creadas")

        # Commit de monedas para que estén disponibles para foreign keys
        db.session.commit()

        # Crear usuario administrador si no existe
        admin = Usuario.query.filter_by(email="admin@inventario.com").first()
        if not admin:
            admin = Usuario(
                email="admin@inventario.com",
                nombre="Administrador",
                apellido="Sistema",
                rol="admin",
                moneda_preferida_id=None,  # Se asignará la default después del commit
            )
            admin.set_password("admin123")
            db.session.add(admin)
            print("✓ Usuario administrador creado")

        # Crear categorías de ejemplo
        categorias_data = [
            ("Electrónica", "#007bff", "Dispositivos electrónicos y accesorios"),
            ("Ropa", "#28a745", "Prendas de vestir y textiles"),
            ("Alimentos", "#ffc107", "Productos alimenticios y bebidas"),
            ("Herramientas", "#dc3545", "Herramientas y equipo de trabajo"),
            ("Oficina", "#6f42c1", "Artículos de oficina y papelería"),
        ]

        for nombre, color, descripcion in categorias_data:
            categoria = Categoria.query.filter_by(nombre=nombre).first()
            if not categoria:
                categoria = Categoria(
                    nombre=nombre, color=color, descripcion=descripcion
                )
                db.session.add(categoria)

        print("✓ Categorías de ejemplo creadas")

        # Commit de categorías para que estén disponibles para foreign keys
        db.session.commit()

        # Crear productos de ejemplo
        productos_data = [
            (
                "Laptop Pro 15",
                "LP-001",
                "Electrónica",
                1500000,
                5,
                10,
                "Laptop de alto rendimiento",
            ),
            (
                "Mouse Inalámbrico",
                "MOU-001",
                "Electrónica",
                25000,
                15,
                5,
                "Mouse ergonómico inalámbrico",
            ),
            (
                "Teclado Mecánico",
                "TEC-001",
                "Electrónica",
                80000,
                8,
                10,
                "Teclado mecánico RGB",
            ),
            (
                'Monitor 24"',
                "MON-001",
                "Electrónica",
                300000,
                3,
                5,
                "Monitor LED 24 pulgadas",
            ),
            (
                "Camisa Formal",
                "CAM-001",
                "Ropa",
                50000,
                20,
                15,
                "Camisa de vestir blanca",
            ),
            ("Jeans Clásico", "JEA-001", "Ropa", 80000, 12, 20, "Pantalón jeans azul"),
            (
                "Café Premium",
                "CAF-001",
                "Alimentos",
                15000,
                50,
                25,
                "Café en grano premium",
            ),
            ("Arroz Blanco", "ARR-001", "Alimentos", 2500, 100, 50, "Arroz blanco 1kg"),
            (
                "Taladro Eléctrico",
                "TAL-001",
                "Herramientas",
                120000,
                2,
                3,
                "Taladro eléctrico profesional",
            ),
            ("Cuaderno A4", "CUA-001", "Oficina", 3000, 100, 50, "Cuaderno espiral A4"),
        ]

        for nombre, sku, cat_nombre, precio, stock, umbral, desc in productos_data:
            producto = Producto.query.filter_by(sku=sku).first()
            if not producto:
                categoria = Categoria.query.filter_by(nombre=cat_nombre).first()
                moneda = Moneda.query.filter_by(codigo="NIO").first()
                producto = Producto(
                    nombre=nombre,
                    sku=sku,
                    id_categoria=categoria.id if categoria else None,
                    moneda_original_id=moneda.id if moneda else None,
                    precio_original=precio,
                    precio_base=precio,
                    cantidad_stock=stock,
                    umbral_minimo=umbral,
                    descripcion=desc,
                )
                db.session.add(producto)

        print("✓ Productos de ejemplo creados")

        # Confirmar cambios
        db.session.commit()
        print("✓ Base de datos inicializada exitosamente")

        print("\n📋 Datos de acceso:")
        print("Email: admin@inventario.com")
        print("Contraseña: admin123")
        print("\n🚀 Ejecuta 'python run.py' para iniciar la aplicación")


if __name__ == "__main__":
    init_db()
