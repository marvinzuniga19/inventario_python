#!/usr/bin/env python3
"""
Script de migración para convertir el sistema de moneda de COP a NIO
y agregar soporte para múltiples monedas.

Este script:
1. Crea las tablas de monedas y tasas de cambio
2. Puebla las monedas iniciales (NIO, MXN, USD, COP)
3. Convierte todos los precios existentes de COP a NIO
4. Actualiza los modelos de productos y usuarios
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.moneda import Moneda
from app.models.tasa_cambio import TasaCambio
from app.models.producto import Producto
from app.models.usuario import Usuario
from app.services.currency_service import CurrencyService
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def crear_monedas_iniciales():
    """Crear las monedas iniciales en la base de datos"""
    logger.info("Creando monedas iniciales...")
    
    monedas_data = [
        {
            'codigo': 'NIO',
            'nombre': 'Córdoba Nicaraguense',
            'simbolo': 'C$',
            'locale': 'es-NI',
            'es_default': True,
            'activo': True
        },
        {
            'codigo': 'MXN',
            'nombre': 'Peso Mexicano',
            'simbolo': '$',
            'locale': 'es-MX',
            'es_default': False,
            'activo': True
        },
        {
            'codigo': 'USD',
            'nombre': 'Dólar Americano',
            'simbolo': '$',
            'locale': 'en-US',
            'es_default': False,
            'activo': True
        },
        {
            'codigo': 'COP',
            'nombre': 'Peso Colombiano',
            'simbolo': '$',
            'locale': 'es-CO',
            'es_default': False,
            'activo': True
        }
    ]
    
    for moneda_data in monedas_data:
        # Verificar si ya existe
        moneda_existente = Moneda.get_by_codigo(moneda_data['codigo'])
        if moneda_existente:
            logger.info(f"Moneda {moneda_data['codigo']} ya existe, omitiendo...")
            continue
        
        # Crear nueva moneda
        moneda = Moneda(**moneda_data)
        db.session.add(moneda)
        logger.info(f"Creada moneda: {moneda.codigo} - {moneda.nombre}")
    
    db.session.commit()
    logger.info("Monedas iniciales creadas exitosamente")

def crear_tasas_cambio_iniciales():
    """Crear tasas de cambio iniciales"""
    logger.info("Creando tasas de cambio iniciales...")
    
    # Obtener monedas
    nio = Moneda.get_by_codigo('NIO')
    mxn = Moneda.get_by_codigo('MXN')
    usd = Moneda.get_by_codigo('USD')
    cop = Moneda.get_by_codigo('COP')
    
    if not all([nio, mxn, usd, cop]):
        logger.error("No se encontraron todas las monedas necesarias")
        return False
    
    # Tasas de cambio iniciales (valores aproximados)
    tasas_iniciales = [
        # NIO como moneda base
        {'origen': nio, 'destino': mxn, 'tasa': 2.10},    # 1 NIO = 2.10 MXN
        {'origen': nio, 'destino': usd, 'tasa': 0.0274},   # 1 NIO = 0.0274 USD
        {'origen': nio, 'destino': cop, 'tasa': 117.5},   # 1 NIO = 117.5 COP
        
        # Tasas inversas
        {'origen': mxn, 'destino': nio, 'tasa': 0.476},    # 1 MXN = 0.476 NIO
        {'origen': usd, 'destino': nio, 'tasa': 36.50},    # 1 USD = 36.50 NIO
        {'origen': cop, 'destino': nio, 'tasa': 0.0085},    # 1 COP = 0.0085 NIO
    ]
    
    for tasa_data in tasas_iniciales:
        # Verificar si ya existe
        tasa_existente = TasaCambio.get_tasa_actual(
            tasa_data['origen'].id, 
            tasa_data['destino'].id
        )
        
        if tasa_existente:
            logger.info(f"Tasa {tasa_data['origen'].codigo}->{tasa_data['destino'].codigo} ya existe")
            continue
        
        # Crear nueva tasa
        tasa = TasaCambio(
            moneda_origen_id=tasa_data['origen'].id,
            moneda_destino_id=tasa_data['destino'].id,
            tasa=tasa_data['tasa']
        )
        db.session.add(tasa)
        logger.info(f"Creada tasa: {tasa_data['origen'].codigo} -> {tasa_data['destino'].codigo} = {tasa_data['tasa']}")
    
    db.session.commit()
    logger.info("Tasas de cambio iniciales creadas exitosamente")
    return True

def convertir_precios_productos():
    """Convertir precios de productos de COP a NIO"""
    logger.info("Convirtiendo precios de productos...")
    
    # Obtener monedas
    nio = Moneda.get_by_codigo('NIO')
    cop = Moneda.get_by_codigo('COP')
    
    if not nio or not cop:
        logger.error("No se encontraron monedas NIO o COP")
        return False
    
    # Obtener tasa de conversión COP -> NIO
    tasa_cop_nio = TasaCambio.get_tasa_actual(cop.id, nio.id)
    if not tasa_cop_nio:
        logger.error("No se encontró tasa de conversión COP -> NIO")
        return False
    
    tasa_conversion = float(tasa_cop_nio.tasa)
    logger.info(f"Usando tasa de conversión COP -> NIO: {tasa_conversion}")
    
    # Convertir productos
    productos = Producto.query.all()
    convertidos = 0
    
    for producto in productos:
        try:
            # Guardar precio original
            if not hasattr(producto, 'precio_original') or producto.precio_original is None:
                producto.precio_original = producto.precio_base or producto.precio
            
            # Convertir a NIO
            precio_en_nio = float(producto.precio_original) * tasa_conversion
            
            # Actualizar campos
            producto.precio_base = precio_en_nio
            producto.moneda_original_id = cop.id
            
            convertidos += 1
            
            if convertidos % 100 == 0:
                logger.info(f"Convertidos {convertidos} productos...")
                
        except Exception as e:
            logger.error(f"Error convirtiendo producto {producto.id}: {str(e)}")
            continue
    
    db.session.commit()
    logger.info(f"Se convirtieron {convertidos} productos de COP a NIO")
    return True

def actualizar_usuarios():
    """Actualizar preferencias de moneda de usuarios"""
    logger.info("Actualizando preferencias de usuarios...")
    
    # Obtener moneda default (NIO)
    nio = Moneda.get_by_codigo('NIO')
    if not nio:
        logger.error("No se encontró moneda NIO")
        return False
    
    # Actualizar todos los usuarios para que usen NIO como preferencia
    usuarios = Usuario.query.all()
    actualizados = 0
    
    for usuario in usuarios:
        try:
            if usuario.moneda_preferida_id is None:
                usuario.moneda_preferida_id = nio.id
                actualizados += 1
        except Exception as e:
            logger.error(f"Error actualizando usuario {usuario.id}: {str(e)}")
            continue
    
    db.session.commit()
    logger.info(f"Se actualizaron {actualizados} usuarios con moneda preferida NIO")
    return True

def verificar_migracion():
    """Verificar que la migración se completó correctamente"""
    logger.info("Verificando migración...")
    
    # Verificar monedas
    monedas = Moneda.query.filter_by(activo=True).all()
    logger.info(f"Total monedas activas: {len(monedas)}")
    
    for moneda in monedas:
        logger.info(f"  - {moneda.codigo}: {moneda.nombre} (Default: {moneda.es_default})")
    
    # Verificar tasas
    tasas = TasaCambio.query.all()
    logger.info(f"Total tasas de cambio: {len(tasas)}")
    
    # Verificar productos
    productos_con_moneda = Producto.query.filter(Producto.moneda_original_id.isnot(None)).count()
    total_productos = Producto.query.count()
    logger.info(f"Productos con moneda original: {productos_con_moneda}/{total_productos}")
    
    # Verificar usuarios
    usuarios_con_moneda = Usuario.query.filter(Usuario.moneda_preferida_id.isnot(None)).count()
    total_usuarios = Usuario.query.count()
    logger.info(f"Usuarios con moneda preferida: {usuarios_con_moneda}/{total_usuarios}")
    
    return True

def main():
    """Función principal de migración"""
    logger.info("Iniciando migración de monedas...")
    
    try:
        # Crear aplicación y contexto
        app = create_app()
        with app.app_context():
            # Crear todas las tablas necesarias
            logger.info("Creando tablas de base de datos...")
            db.create_all()
            logger.info("Tablas creadas exitosamente")
            
            # 1. Crear monedas iniciales
            crear_monedas_iniciales()
            
            # 2. Crear tasas de cambio iniciales
            if not crear_tasas_cambio_iniciales():
                logger.error("Error creando tasas de cambio iniciales")
                return False
            
            # 3. Convertir precios de productos
            if not convertir_precios_productos():
                logger.error("Error convirtiendo precios de productos")
                return False
            
            # 4. Actualizar usuarios
            if not actualizar_usuarios():
                logger.error("Error actualizando usuarios")
                return False
            
            # 5. Verificar migración
            if not verificar_migracion():
                logger.error("Error en verificación de migración")
                return False
            
            logger.info("Migración completada exitosamente!")
            return True
            
    except Exception as e:
        logger.error(f"Error en migración: {str(e)}")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)