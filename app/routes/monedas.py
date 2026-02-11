from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from app import db
from app.models.moneda import Moneda
from app.models.tasa_cambio import TasaCambio
from app.services.currency_service import CurrencyService
from app.services.exchange_rate_api import ExchangeRateAPI
import logging

logger = logging.getLogger(__name__)

monedas = Blueprint('monedas', __name__, url_prefix='/monedas')

@monedas.route('/configuracion')
@login_required
def configuracion():
    """Vista de configuración de monedas"""
    monedas = CurrencyService.obtener_todas_monedas_activas()
    moneda_default = Moneda.get_default()
    tasas_cambio = CurrencyService.obtener_tasas_cambio()
    
    return render_template('monedas/configuracion.html', 
                         monedas=monedas,
                         moneda_default=moneda_default,
                         tasas_cambio=tasas_cambio)

@monedas.route('/api/tasas')
@login_required
def api_tasas():
    """API endpoint para obtener tasas de cambio actuales"""
    try:
        resumen = CurrencyService.obtener_resumen_monedas()
        return jsonify(resumen)
    except Exception as e:
        logger.error(f"Error obteniendo tasas: {str(e)}")
        return jsonify({'error': 'Error obteniendo tasas de cambio'}), 500

@monedas.route('/actualizar-tasas', methods=['POST'])
@login_required
def actualizar_tasas():
    """Actualizar tasas de cambio desde API externa"""
    if current_user.rol != 'admin':
        flash('No tienes permisos para realizar esta acción', 'error')
        return redirect(url_for('monedas.configuracion'))
    
    try:
        # Inicializar servicio de API
        api_service = ExchangeRateAPI(
            api_provider=current_app.config['API_TASAS_PROVIDER'],
            api_key=current_app.config.get('API_TASAS_KEY')
        )
        
        # Actualizar tasas
        resultado = api_service.actualizar_tasas_sistema(
            moneda_base_codigo=current_app.config['MONEDA_DEFAULT']
        )
        
        if resultado['exito']:
            flash(f"Se actualizaron exitosamente {resultado['tasas_actualizadas']} tasas de cambio", 'success')
        else:
            flash(f"Error actualizando tasas: {resultado['mensaje']}", 'error')
            
    except Exception as e:
        logger.error(f"Error actualizando tasas: {str(e)}")
        flash('Error al actualizar tasas de cambio', 'error')
    
    return redirect(url_for('monedas.configuracion'))

@monedas.route('/cambiar-moneda', methods=['POST'])
@login_required
def cambiar_moneda_usuario():
    """Cambiar la moneda preferida del usuario"""
    moneda_id = request.form.get('moneda_id')
    
    if not moneda_id:
        return jsonify({'error': 'ID de moneda no proporcionado'}), 400
    
    try:
        # Validar que la moneda exista y esté activa
        moneda = Moneda.query.filter_by(id=moneda_id, activo=True).first()
        if not moneda:
            return jsonify({'error': 'Moneda no encontrada o inactiva'}), 404
        
        # Actualizar preferencia del usuario
        current_user.moneda_preferida_id = moneda.id
        db.session.commit()
        
        return jsonify({
            'success': True,
            'moneda': moneda.to_dict(),
            'message': f'Moneda preferida cambiada a {moneda.nombre}'
        })
        
    except Exception as e:
        logger.error(f"Error cambiando moneda: {str(e)}")
        return jsonify({'error': 'Error al cambiar moneda preferida'}), 500

@monedas.route('/api/moneda-actual')
@login_required
def api_moneda_actual():
    """API endpoint para obtener la moneda actual del usuario"""
    try:
        moneda_actual = current_user.get_moneda_preferida()
        if not moneda_actual:
            return jsonify({'error': 'No se encontró moneda configurada'}), 404
        
        return jsonify({
            'moneda': moneda_actual.to_dict(),
            'formateo_ejemplo': CurrencyService.formatear_precio(1234.56, moneda_actual.codigo)
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo moneda actual: {str(e)}")
        return jsonify({'error': 'Error obteniendo moneda actual'}), 500

@monedas.route('/api/convertir', methods=['POST'])
@login_required
def api_convertir():
    """API endpoint para convertir montos entre monedas"""
    try:
        data = request.get_json()
        
        monto = data.get('monto')
        moneda_origen = data.get('moneda_origen')
        moneda_destino = data.get('moneda_destino')
        
        if not all([monto, moneda_origen, moneda_destino]):
            return jsonify({'error': 'Faltan parámetros requeridos'}), 400
        
        # Validar monto
        es_valido, monto_convertido, error_msg = CurrencyService.validar_monto(monto)
        if not es_valido:
            return jsonify({'error': error_msg}), 400
        
        # Obtener IDs de monedas
        mon_orig = Moneda.get_by_codigo(moneda_origen)
        mon_dest = Moneda.get_by_codigo(moneda_destino)
        
        if not mon_orig or not mon_dest:
            return jsonify({'error': 'Moneda no válida'}), 400
        
        # Convertir
        resultado = CurrencyService.convertir_precio(
            monto_convertido,
            mon_orig.id,
            mon_dest.id
        )
        
        # Formatear resultado
        resultado_formateado = CurrencyService.formatear_precio(resultado, moneda_destino)
        
        return jsonify({
            'monto_original': monto_convertido,
            'moneda_origen': moneda_origen,
            'moneda_destino': moneda_destino,
            'monto_convertido': resultado,
            'resultado_formateado': resultado_formateado
        })
        
    except Exception as e:
        logger.error(f"Error en conversión: {str(e)}")
        return jsonify({'error': 'Error en la conversión'}), 500

@monedas.route('/estadisticas')
@login_required
def estadisticas():
    """Vista de estadísticas de monedas y tasas"""
    if current_user.rol != 'admin':
        flash('No tienes permisos para ver esta página', 'error')
        return redirect(url_for('main.dashboard'))
    
    try:
        resumen = CurrencyService.obtener_resumen_monedas()
        
        # Estadísticas adicionales
        total_monedas = len(resumen['monedas'])
        total_tasas = len(resumen['tasas_cambio'])
        
        return render_template('monedas/estadisticas.html',
                             resumen=resumen,
                             total_monedas=total_monedas,
                             total_tasas=total_tasas)
                             
    except Exception as e:
        logger.error(f"Error en estadísticas: {str(e)}")
        flash('Error al cargar estadísticas de monedas', 'error')
        return redirect(url_for('main.dashboard'))