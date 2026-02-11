import requests
import logging
from datetime import datetime
from app.services.currency_service import CurrencyService
from app.models.moneda import Moneda

logger = logging.getLogger(__name__)

class ExchangeRateAPI:
    """Servicio para integración con APIs externas de tasas de cambio"""
    
    # APIs soportadas
    APIS = {
        'exchangerate_api': {
            'base_url': 'https://api.exchangerate-api.com/v4/latest/',
            'free_tier_requests': 2000,
            'documentation': 'https://www.exchangerate-api.com/docs/free'
        },
        'fixer': {
            'base_url': 'http://data.fixer.io/api/latest',
            'free_tier_requests': 1000,
            'documentation': 'https://fixer.io/documentation/'
        }
    }
    
    def __init__(self, api_provider='exchangerate_api', api_key=None):
        """
        Inicializar servicio de API
        
        Args:
            api_provider (str): Proveedor de API ('exchangerate_api', 'fixer')
            api_key (str): API key (opcional para exchangerate-api)
        """
        self.api_provider = api_provider
        self.api_key = api_key
        self.base_url = self.APIS[api_provider]['base_url']
    
    def obtener_tasas_actuales(self, moneda_base='USD'):
        """
        Obtener tasas de cambio actuales desde API externa
        
        Args:
            moneda_base (str): Moneda base para la API (default: USD)
            
        Returns:
            dict: Tasas de cambio o None si hay error
        """
        try:
            if self.api_provider == 'exchangerate_api':
                return self._obtener_tasas_exchangerate_api(moneda_base)
            elif self.api_provider == 'fixer':
                return self._obtener_tasas_fixer(moneda_base)
            else:
                logger.error(f"Proveedor de API no soportado: {self.api_provider}")
                return None
                
        except Exception as e:
            logger.error(f"Error obteniendo tasas de cambio: {str(e)}")
            return None
    
    def _obtener_tasas_exchangerate_api(self, moneda_base='USD'):
        """Obtener tasas desde exchangerate-api.com"""
        url = f"{self.base_url}{moneda_base}"
        
        headers = {
            'User-Agent': 'Sistema-Inventario/1.0',
            'Accept': 'application/json'
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('success', True):
                logger.info(f"Tasas obtenidas exitosamente desde {self.api_provider}")
                return {
                    'moneda_base': data.get('base', moneda_base),
                    'tasas': data.get('rates', {}),
                    'fecha': data.get('date', datetime.now().strftime('%Y-%m-%d')),
                    'proveedor': self.api_provider
                }
            else:
                logger.error(f"Error en API: {data.get('error', 'Error desconocido')}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error de conexión con {self.api_provider}: {str(e)}")
            return None
    
    def _obtener_tasas_fixer(self, moneda_base='EUR'):
        """Obtener tasas desde fixer.io"""
        if not self.api_key:
            logger.error("Se requiere API key para Fixer.io")
            return None
        
        url = f"{self.base_url}"
        params = {
            'access_key': self.api_key,
            'base': moneda_base
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('success', False):
                logger.info(f"Tasas obtenidas exitosamente desde Fixer.io")
                return {
                    'moneda_base': data.get('base', moneda_base),
                    'tasas': data.get('rates', {}),
                    'fecha': data.get('date', datetime.now().strftime('%Y-%m-%d')),
                    'proveedor': 'fixer'
                }
            else:
                logger.error(f"Error en Fixer API: {data.get('error', {}).get('info', 'Error desconocido')}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error de conexión con Fixer.io: {str(e)}")
            return None
    
    def guardar_tasas_en_bd(self, tasas_api, moneda_base_codigo='NIO'):
        """
        Guardar tasas de cambio en la base de datos
        
        Args:
            tasas_api (dict): Tasas desde API
            moneda_base_codigo (str): Código de moneda base del sistema
            
        Returns:
            int: Número de tasas actualizadas
        """
        if not tasas_api:
            return 0
        
        # Obtener moneda base del sistema
        moneda_base_sistema = Moneda.get_by_codigo(moneda_base_codigo)
        if not moneda_base_sistema:
            logger.error(f"No se encontró moneda base del sistema: {moneda_base_codigo}")
            return 0
        
        # Moneda base de la API
        moneda_base_api = tasas_api['moneda_base']
        tasas = tasas_api['tasas']
        
        actualizadas = 0
        
        # Si la moneda base de la API es diferente a la del sistema,
        # necesitamos hacer conversiones
        if moneda_base_api != moneda_base_codigo:
            # Buscar tasa de conversión entre monedas base
            if moneda_base_codigo in tasas:
                # Convertir todas las tasas a la moneda base del sistema
                tasa_base_a_sistema = tasas[moneda_base_codigo]
                
                for codigo_destino, tasa_valor in tasas.items():
                    if codigo_destino == moneda_base_codigo:
                        continue
                    
                    # Convertir tasa: API_base -> destino = (API_base -> sistema) / (destino -> sistema)
                    tasa_convertida = tasa_valor / tasa_base_a_sistema
                    
                    moneda_destino = Moneda.get_by_codigo(codigo_destino)
                    if moneda_destino:
                        from app.models.tasa_cambio import TasaCambio
                        TasaCambio.actualizar_tasa(
                            moneda_base_sistema.id,
                            moneda_destino.id,
                            tasa_convertida
                        )
                        actualizadas += 1
        else:
            # Las tasas ya están en la moneda base correcta
            actualizadas = CurrencyService.actualizar_tasas_desde_api(
                tasas, 
                moneda_base_codigo
            )
        
        logger.info(f"Se actualizaron {actualizadas} tasas de cambio en la base de datos")
        return actualizadas
    
    def actualizar_tasas_sistema(self, moneda_base_codigo='NIO'):
        """
        Método completo para actualizar tasas del sistema
        
        Args:
            moneda_base_codigo (str): Moneda base del sistema
            
        Returns:
            dict: Resultado de la actualización
        """
        resultado = {
            'exito': False,
            'tasas_obtenidas': 0,
            'tasas_actualizadas': 0,
            'mensaje': '',
            'proveedor': self.api_provider
        }
        
        # Obtener tasas desde API
        tasas_api = self.obtener_tasas_actuales()
        
        if not tasas_api:
            resultado['mensaje'] = 'No se pudieron obtener las tasas de cambio'
            return resultado
        
        resultado['tasas_obtenidas'] = len(tasas_api['tasas'])
        
        # Guardar en base de datos
        actualizadas = self.guardar_tasas_en_bd(tasas_api, moneda_base_codigo)
        resultado['tasas_actualizadas'] = actualizadas
        
        if actualizadas > 0:
            resultado['exito'] = True
            resultado['mensaje'] = f'Se actualizaron exitosamente {actualizadas} tasas de cambio'
        else:
            resultado['mensaje'] = 'No se actualizaron tasas (posiblemente ya estaban actualizadas)'
        
        return resultado
    
    @staticmethod
    def obtener_tasas_fallback():
        """
        Obtener tasas de cambio de respaldo (valores fijos)
        Útil cuando las APIs no están disponibles
        """
        # Tasas aproximadas (valores de ejemplo, deberían actualizarse)
        return {
            'USD': 0.0274,  # 1 NIO = 0.0274 USD
            'MXN': 0.48,     # 1 NIO = 0.48 MXN
            'COP': 117.5,    # 1 NIO = 117.5 COP
            'EUR': 0.0253    # 1 NIO = 0.0253 EUR
        }