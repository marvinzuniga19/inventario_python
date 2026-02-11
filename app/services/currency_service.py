from app.models.moneda import Moneda
from app.models.tasa_cambio import TasaCambio
from app import db
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class CurrencyService:
    """Servicio para manejo de conversiones y formateo de monedas"""
    
    @staticmethod
    def convertir_precio(monto, moneda_origen_id, moneda_destino_id):
        """
        Convertir un monto de una moneda a otra usando tasas de cambio
        
        Args:
            monto (float): Monto a convertir
            moneda_origen_id (int): ID de moneda origen
            moneda_destino_id (int): ID de moneda destino
            
        Returns:
            float: Monto convertido
        """
        if moneda_origen_id == moneda_destino_id:
            return float(monto)
        
        # Buscar tasa de cambio directa
        tasa = TasaCambio.get_tasa_actual(moneda_origen_id, moneda_destino_id)
        if tasa:
            return float(monto) * float(tasa.tasa)
        
        # Si no hay tasa directa, intentar conversión a través de NIO (moneda base)
        moneda_nio = Moneda.get_by_codigo('NIO')
        if moneda_nio:
            # Convertir origen -> NIO
            tasa_origen_nio = TasaCambio.get_tasa_actual(moneda_origen_id, moneda_nio.id)
            if tasa_origen_nio:
                monto_en_nio = float(monto) * float(tasa_origen_nio.tasa)
                
                # Convertir NIO -> destino
                if moneda_destino_id == moneda_nio.id:
                    return monto_en_nio
                
                tasa_nio_destino = TasaCambio.get_tasa_actual(moneda_nio.id, moneda_destino_id)
                if tasa_nio_destino:
                    return monto_en_nio * float(tasa_nio_destino.tasa)
        
        # Si no se puede convertir, retornar monto original
        logger.warning(f"No se encontró tasa de conversión de {moneda_origen_id} a {moneda_destino_id}")
        return float(monto)
    
    @staticmethod
    def formatear_precio(monto, moneda_codigo=None, locale=None):
        """
        Formatear un monto según la moneda y locale especificados
        
        Args:
            monto (float): Monto a formatear
            moneda_codigo (str): Código de moneda (NIO, MXN, USD)
            locale (str): Locale específico (opcional)
            
        Returns:
            str: Monto formateado con símbolo de moneda
        """
        if moneda_codigo is None:
            moneda = Moneda.get_default()
        else:
            moneda = Moneda.get_by_codigo(moneda_codigo)
        
        if not moneda:
            # Formateo genérico si no se encuentra la moneda
            return f"${float(monto):,.2f}"
        
        # Usar locale de la moneda si no se especifica uno
        if locale is None:
            locale = moneda.locale
        
        # Formateo específico por locale
        if locale == 'es-NI':  # Nicaragua
            return f"C${float(monto):,.2f}"
        elif locale == 'es-MX':  # México
            return f"${float(monto):,.2f} MXN"
        elif locale == 'en-US':  # Estados Unidos
            return f"${float(monto):,.2f} USD"
        elif locale == 'es-CO':  # Colombia
            return f"${float(monto):,.0f}"
        else:
            # Formateo genérico con símbolo de la moneda
            return f"{moneda.simbolo}{float(monto):,.2f}"
    
    @staticmethod
    def obtener_todas_monedas_activas():
        """Obtener todas las monedas activas"""
        return Moneda.query.filter_by(activo=True).all()
    
    @staticmethod
    def obtener_tasas_cambio(moneda_base_codigo='NIO'):
        """
        Obtener todas las tasas de cambio desde una moneda base
        
        Args:
            moneda_base_codigo (str): Código de moneda base (default: NIO)
            
        Returns:
            dict: Diccionario con tasas de cambio
        """
        moneda_base = Moneda.get_by_codigo(moneda_base_codigo)
        if not moneda_base:
            return {}
        
        tasas = TasaCambio.obtener_todas_tasas(moneda_base.id)
        resultado = {}
        
        for tasa in tasas:
            resultado[tasa.moneda_destino.codigo] = {
                'tasa': float(tasa.tasa),
                'fecha_actualizacion': tasa.fecha_actualizacion.isoformat(),
                'moneda_destino': tasa.moneda_destino.to_dict()
            }
        
        return resultado
    
    @staticmethod
    def actualizar_tasas_desde_api(tasas_api, moneda_base_codigo='NIO'):
        """
        Actualizar tasas de cambio desde datos de API
        
        Args:
            tasas_api (dict): Tasas desde API externa
            moneda_base_codigo (str): Código de moneda base
            
        Returns:
            int: Número de tasas actualizadas
        """
        moneda_base = Moneda.get_by_codigo(moneda_base_codigo)
        if not moneda_base:
            logger.error(f"No se encontró moneda base: {moneda_base_codigo}")
            return 0
        
        actualizadas = 0
        
        for codigo_destino, tasa_valor in tasas_api.items():
            if codigo_destino == moneda_base_codigo:
                continue
                
            moneda_destino = Moneda.get_by_codigo(codigo_destino)
            if moneda_destino:
                TasaCambio.actualizar_tasa(
                    moneda_base.id, 
                    moneda_destino.id, 
                    tasa_valor
                )
                actualizadas += 1
                logger.info(f"Tasa actualizada: {moneda_base_codigo} -> {codigo_destino} = {tasa_valor}")
        
        return actualizadas
    
    @staticmethod
    def validar_monto(monto):
        """
        Validar que un monto sea numérico y positivo
        
        Args:
            monto: Valor a validar
            
        Returns:
            tuple: (es_valido, monto_convertido, mensaje_error)
        """
        try:
            monto_float = float(monto)
            if monto_float < 0:
                return False, 0, "El monto no puede ser negativo"
            return True, monto_float, ""
        except (ValueError, TypeError):
            return False, 0, "El monto debe ser un número válido"
    
    @staticmethod
    def obtener_resumen_monedas():
        """
        Obtener resumen de todas las monedas con sus tasas
        
        Returns:
            dict: Información de monedas y tasas
        """
        monedas = CurrencyService.obtener_todas_monedas_activas()
        moneda_default = Moneda.get_default()
        
        resultado = {
            'monedas': [moneda.to_dict() for moneda in monedas],
            'moneda_default': moneda_default.to_dict() if moneda_default else None,
            'tasas_cambio': CurrencyService.obtener_tasas_cambio()
        }
        
        return resultado