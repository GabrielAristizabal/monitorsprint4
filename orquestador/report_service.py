"""
Servicio para generar reportes combinando datos de GestorPedidos y ruta_optima
"""
import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from calendar import monthrange
from .service_client import ServiceClient
import random

class ReportService:
    """Servicio para generar reportes de rutas optimizadas"""
    
    def __init__(self):
        self.client = ServiceClient()
    
    def generate_route_report(self, month: str) -> Dict:
        """
        Genera reporte de rutas optimizadas para los últimos 10 pedidos del mes anterior.
        Identifica stands donde no se estima correctamente el tiempo de preparación.
        
        Args:
            month: Mes en formato YYYY-MM (ej: "2025-11")
        
        Returns:
            Dict con el reporte completo
        """
        start_time = time.time()
        
        try:
            # 1. Obtener últimos 10 pedidos del mes anterior desde GestorPedidos
            orders = self._get_last_10_orders_from_previous_month(month)
            
            if not orders or len(orders) == 0:
                return {
                    'month': month,
                    'orders_count': 0,
                    'stands_con_problema': [],
                    'processing_time_ms': round((time.time() - start_time) * 1000, 2)
                }
            
            # 2. Para cada pedido, obtener su ruta calculada desde ruta_optima
            orders_with_routes = []
            for order in orders:
                route_data = self._get_route_for_order(order.get('erp_order_id'))
                if route_data:
                    orders_with_routes.append({
                        'order': order,
                        'route': route_data
                    })
            
            # 3. Calcular tiempos reales (aleatorios) y guardarlos en el pedido
            orders_with_real_times = self._calculate_and_save_real_times(orders_with_routes)
            
            # 4. Comparar tiempos estimados vs reales por stand
            stands_analysis = self._analyze_stand_deviations(orders_with_real_times)
            
            # 5. Identificar stands con problemas
            problematic_stands = self._identify_problematic_stands(stands_analysis)
            
            processing_time = (time.time() - start_time) * 1000
            
            return {
                'month': month,
                'orders_count': len(orders_with_routes),
                'stands_con_problema': problematic_stands,
                'processing_time_ms': round(processing_time, 2),
                'orders_analyzed': len(orders_with_routes)
            }
            
        except Exception as e:
            print(f"Error generando reporte: {e}")
            return {
                'month': month,
                'orders_count': 0,
                'stands_con_problema': [],
                'error': str(e),
                'processing_time_ms': round((time.time() - start_time) * 1000, 2)
            }
    
    def get_orders_with_routes_detailed(self, month: str) -> Dict:
        """
        Obtiene los últimos 10 pedidos del mes anterior con toda su información
        y las rutas optimizadas calculadas para cada uno.
        
        Args:
            month: Mes en formato YYYY-MM (ej: "2025-11")
        
        Returns:
            Dict con la información completa de pedidos y rutas
        """
        start_time = time.time()
        
        try:
            # 1. Obtener últimos 10 pedidos del mes anterior
            orders = self._get_last_10_orders_from_previous_month(month)
            
            if not orders or len(orders) == 0:
                return {
                    'month': month,
                    'orders_count': 0,
                    'orders': [],
                    'processing_time_ms': round((time.time() - start_time) * 1000, 2)
                }
            
            # 2. Para cada pedido, obtener su ruta calculada
            orders_with_routes = []
            for order in orders:
                erp_order_id = order.get('erp_order_id')
                order_id = order.get('id')
                print(f"🔍 Buscando ruta para pedido - erp_order_id: {erp_order_id}, id: {order_id}")
                
                # Intentar primero con erp_order_id
                route_data = self._get_route_for_order(erp_order_id)
                
                # Si no se encuentra, intentar con el id de MongoDB
                if not route_data and order_id:
                    print(f"⚠️ No se encontró ruta con erp_order_id, intentando con id: {order_id}")
                    route_data = self._get_route_for_order(order_id)
                
                # Calcular tiempos reales para este pedido
                items_with_real_times = []
                for item in order.get('items', []):
                    tiempo_estimado = item.get('tiempo_estimado_pick', 5.0)
                    # Generar tiempo real aleatorio (80% a 150% del estimado)
                    variacion = random.uniform(0.8, 1.5)
                    tiempo_real = round(tiempo_estimado * variacion, 2)
                    
                    items_with_real_times.append({
                        **item,
                        'tiempo_real_pick': tiempo_real
                    })
                
                # Calcular tiempo total real
                tiempo_total_real = round(sum(item.get('tiempo_real_pick', 0) for item in items_with_real_times), 2)
                
                order_detail = {
                    'order_id': order.get('id'),
                    'erp_order_id': order.get('erp_order_id'),
                    'status': order.get('status'),
                    'created_at': order.get('created_at'),
                    'items': items_with_real_times,
                    'tiempo_total_estimado': sum(item.get('tiempo_estimado_pick', 0) for item in items_with_real_times),
                    'tiempo_total_real': tiempo_total_real
                }
                
                if route_data:
                    order_detail['ruta_optimizada'] = {
                        'ruta': route_data.get('ruta', []),
                        'distancia_m': route_data.get('distancia_m', 0),
                        'tiempo_caminar_seg': route_data.get('tiempo_caminar_seg', 0),
                        'tiempo_picking_seg': route_data.get('tiempo_picking_seg', 0),
                        'tiempo_total_seg': route_data.get('tiempo_total_seg', 0),
                        'tiempo_total_min': route_data.get('tiempo_total_min', 0),
                        'items_recogidos': route_data.get('items_recogidos', 0),
                        'velocidad_usada_m_s': route_data.get('velocidad_usada_m_s', 2.5)
                    }
                else:
                    order_detail['ruta_optimizada'] = None
                
                orders_with_routes.append(order_detail)
            
            processing_time = (time.time() - start_time) * 1000
            
            return {
                'month': month,
                'orders_count': len(orders_with_routes),
                'orders': orders_with_routes,
                'processing_time_ms': round(processing_time, 2)
            }
            
        except Exception as e:
            print(f"Error obteniendo pedidos con rutas: {e}")
            return {
                'month': month,
                'orders_count': 0,
                'orders': [],
                'error': str(e),
                'processing_time_ms': round((time.time() - start_time) * 1000, 2)
            }
    
    def _get_last_10_orders_from_previous_month(self, month: str) -> List[Dict]:
        """Obtiene los últimos 10 pedidos del mes anterior desde GestorPedidos"""
        try:
            # Llamar al nuevo endpoint del gestor
            response = self.client.call_gestor_pedidos(
                f'/orders/last-10-previous-month?month={month}',
                method='GET'
            )
            
            if response and response.get('status') == 'success':
                return response.get('orders', [])
            
            return []
            
        except Exception as e:
            print(f"Error obteniendo pedidos: {e}")
            return []
    
    def _get_route_for_order(self, order_id: str) -> Optional[Dict]:
        """Obtiene la ruta calculada para un pedido desde ruta_optima"""
        try:
            # Llamar al endpoint de ruta_optima
            response = self.client.call_ruta_optima(
                f'/ruta/{order_id}/',
                method='GET'
            )
            
            if response:
                if response.get('status') == 'OK':
                    return response.get('ruta')
                elif response.get('status') == 'NOT_FOUND':
                    print(f"⚠️ Ruta no encontrada para pedido {order_id}: {response.get('mensaje', 'Sin mensaje')}")
                    return None
                else:
                    print(f"⚠️ Respuesta inesperada de ruta_optima para pedido {order_id}: {response}")
                    return None
            
            print(f"⚠️ No se recibió respuesta de ruta_optima para pedido {order_id}")
            return None
            
        except Exception as e:
            print(f"❌ Error obteniendo ruta para pedido {order_id}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _calculate_and_save_real_times(self, orders_with_routes: List[Dict]) -> List[Dict]:
        """
        Calcula tiempos reales aleatorios y los guarda en los pedidos del gestor.
        Los tiempos reales se generan con una variación del 80% al 150% del tiempo estimado.
        """
        result = []
        
        for item in orders_with_routes:
            order = item['order']
            route = item['route']
            
            # Generar tiempos reales para cada item del pedido
            items_with_real_times = []
            total_real_time = 0
            
            for order_item in order.get('items', []):
                tiempo_estimado = order_item.get('tiempo_estimado_pick', 5.0)
                
                # Generar tiempo real aleatorio (80% a 150% del estimado)
                variacion = random.uniform(0.8, 1.5)
                tiempo_real = round(tiempo_estimado * variacion, 2)
                
                items_with_real_times.append({
                    **order_item,
                    'tiempo_real_pick': tiempo_real
                })
                
                total_real_time += tiempo_real
            
            # Actualizar el pedido con tiempos reales
            order['items'] = items_with_real_times
            order['tiempo_total_real'] = round(total_real_time, 2)
            order['tiempo_total_estimado'] = route.get('tiempo_picking_seg', 0)
            
            # Guardar tiempos reales en el gestor
            try:
                self.client.call_gestor_pedidos(
                    f'/orders/{order.get("erp_order_id")}/real-times',
                    method='PUT',
                    json=items_with_real_times
                )
            except Exception as e:
                print(f"Error guardando tiempos reales para pedido {order.get('erp_order_id')}: {e}")
            
            result.append({
                'order': order,
                'route': route
            })
        
        return result
    
    def _analyze_stand_deviations(self, orders_with_real_times: List[Dict]) -> Dict[str, Dict]:
        """
        Analiza las desviaciones de tiempo por stand
        
        Returns:
            Dict con análisis por stand_id
        """
        stand_stats = {}
        
        for item in orders_with_real_times:
            order = item['order']
            
            for order_item in order.get('items', []):
                stand_id = order_item.get('stand_id_estimada', 'UNKNOWN')
                tiempo_estimado = order_item.get('tiempo_estimado_pick', 0)
                tiempo_real = order_item.get('tiempo_real_pick', tiempo_estimado)
                
                if stand_id not in stand_stats:
                    stand_stats[stand_id] = {
                        'tiempos_estimados': [],
                        'tiempos_reales': [],
                        'count': 0
                    }
                
                stand_stats[stand_id]['tiempos_estimados'].append(tiempo_estimado)
                stand_stats[stand_id]['tiempos_reales'].append(tiempo_real)
                stand_stats[stand_id]['count'] += 1
        
        # Calcular promedios y desviaciones
        analysis = {}
        for stand_id, stats in stand_stats.items():
            if len(stats['tiempos_estimados']) > 0:
                tiempo_estimado_promedio = sum(stats['tiempos_estimados']) / len(stats['tiempos_estimados'])
                tiempo_real_promedio = sum(stats['tiempos_reales']) / len(stats['tiempos_reales'])
                desviacion_promedio = tiempo_real_promedio - tiempo_estimado_promedio
                desviacion_porcentual = (desviacion_promedio / tiempo_estimado_promedio * 100) if tiempo_estimado_promedio > 0 else 0
                
                analysis[stand_id] = {
                    'tiempo_estimado_promedio': round(tiempo_estimado_promedio, 2),
                    'tiempo_real_promedio': round(tiempo_real_promedio, 2),
                    'desviacion_promedio': round(desviacion_promedio, 2),
                    'desviacion_porcentual': round(desviacion_porcentual, 2),
                    'count': stats['count']
                }
        
        return analysis
    
    def _identify_problematic_stands(self, stands_analysis: Dict[str, Dict]) -> List[Dict]:
        """
        Identifica stands con problemas significativos.
        Un stand tiene problemas si la desviación porcentual es > 15%
        """
        problematic = []
        
        for stand_id, analysis in stands_analysis.items():
            desviacion_porcentual = abs(analysis['desviacion_porcentual'])
            
            # Stand problemático si desviación > 15%
            if desviacion_porcentual > 15:
                problematic.append({
                    'stand_id': stand_id,
                    'tiempo_estimado_promedio': analysis['tiempo_estimado_promedio'],
                    'tiempo_real_promedio': analysis['tiempo_real_promedio'],
                    'desviacion_promedio': analysis['desviacion_promedio'],
                    'desviacion_porcentual': analysis['desviacion_porcentual'],
                    'pedidos_analizados': analysis['count']
                })
        
        # Ordenar por desviación descendente
        problematic.sort(key=lambda x: abs(x['desviacion_porcentual']), reverse=True)
        
        return problematic

