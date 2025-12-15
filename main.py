import webview
import threading
import time
import os
import sys
import subprocess
import platform
from app import database
from app import excel_export

"""
Este es el archivo principal que lanza la aplicación.
Utiliza 'pywebview' para crear una ventana de escritorio nativa
que carga el frontend desde la carpeta 'app/ui/'.
"""

# La API_BINDING es un objeto que permite que JavaScript
# llame a funciones de Python.
class Api:
    def __init__(self):
        self._window = None
        self._last_excel_file = None

    def set_window(self, window):
        self._window = window

    # --- API de Inventario (Ejemplos) ---

    def load_products(self):
        """
        Llamado desde JS al cargar la página.
        Devuelve todos los productos de la BD.
        """
        print("[Python] load_products() llamado")
        try:
            products = database.get_all_products()
            return {'success': True, 'data': products}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    def add_product(self, name, product_type, stock, min_stock, cost, supplier=None, purchase_date=None, exit_date=None, sku=None, weight=0, stock_unit_type='units', additional_cost=0):
        """
        Llamado desde JS cuando el usuario envía el formulario.
        Incluye 'cost', proveedor, fechas, SKU, gramaje, tipo de unidad de stock y costo adicional.
        """
        print(f"[Python] add_product() llamado con: {name}, {product_type}, Costo: {cost}, Proveedor: {supplier}, SKU: {sku}, Gramaje: {weight}, Tipo Stock: {stock_unit_type}, Costo Adicional: {additional_cost}")
        try:
            database.add_product(name, product_type, float(stock), float(min_stock), float(cost), supplier, purchase_date, exit_date, sku, float(weight), stock_unit_type, float(additional_cost))
            return {'success': True, 'message': f'Producto {name} añadido'}
        except Exception as e:
            print(f"Error al añadir producto: {e}")
            return {'success': False, 'message': str(e)}

    def adjust_inventory(self, product_id, quantity_change):
        """
        Llamado desde JS para ajustar el stock de un item.
        """
        print(f"[Python] adjust_inventory() llamado para ID {product_id}, Cambio: {quantity_change}")
        try:
            database.update_product_stock(product_id, float(quantity_change))
            return {'success': True, 'message': 'Stock actualizado'}
        except Exception as e:
            print(f"Error al ajustar stock: {e}")
            return {'success': False, 'message': str(e)}

    def update_product(self, product_id, name, product_type, stock, min_stock, cost, supplier=None, purchase_date=None, exit_date=None, sku=None, weight=0, stock_unit_type='units', additional_cost=0):
        """Actualiza un producto existente."""
        print(f"[Python] update_product() llamado para ID {product_id}")
        try:
            database.update_product(product_id, name, product_type, float(stock), float(min_stock), float(cost), supplier, purchase_date, exit_date, sku, float(weight), stock_unit_type, float(additional_cost))
            return {'success': True, 'message': f'Producto {name} actualizado'}
        except Exception as e:
            print(f"Error al actualizar producto: {e}")
            return {'success': False, 'message': str(e)}

    def delete_product(self, product_id):
        """Elimina un producto."""
        print(f"[Python] delete_product() llamado para ID {product_id}")
        try:
            database.delete_product(product_id)
            return {'success': True, 'message': 'Producto eliminado'}
        except Exception as e:
            print(f"Error al eliminar producto: {e}")
            return {'success': False, 'message': str(e)}


    def get_products_by_type(self, product_type):
        """Obtiene productos filtrados por tipo (para rellenar dropdowns)."""
        print(f"[Python] get_products_by_type({product_type}) llamado")
        try:
            products = database.get_products_by_type(product_type)
            return {'success': True, 'data': products}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    # --- API de BOM (Bill of Materials) ---

    def get_bom(self, parent_product_id):
        """Obtiene la lista de materiales para un producto."""
        print(f"[Python] get_bom({parent_product_id}) llamado")
        try:
            bom_items = database.get_bom_for_product(parent_product_id)
            return {'success': True, 'data': bom_items}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    def add_bom_entry(self, parent_id, child_id, quantity):
        """Añade una entrada al BOM."""
        print(f"[Python] add_bom_entry({parent_id}, {child_id}, {quantity})")
        try:
            database.add_bom_entry(parent_id, child_id, float(quantity))
            return {'success': True, 'message': 'Insumo añadido al BOM'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def delete_bom_entry(self, bom_id):
        """Elimina una entrada del BOM."""
        print(f"[Python] delete_bom_entry({bom_id})")
        try:
            database.delete_bom_entry(bom_id)
            return {'success': True, 'message': 'Insumo eliminado del BOM'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def calculate_mrp_production(self, product_id):
        """Calcula cuántos productos se pueden fabricar según el BOM y el inventario."""
        print(f"[Python] calculate_mrp_production() llamado para producto ID {product_id}")
        try:
            result = database.calculate_mrp_production(product_id)
            if result:
                return {'success': True, 'data': result}
            return {'success': False, 'message': 'Producto no encontrado'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def execute_production(self, product_id, quantity):
        """Ejecuta la producción: reduce insumos y aumenta producto final."""
        print(f"[Python] execute_production() llamado para producto ID {product_id}, cantidad: {quantity}")
        try:
            result = database.execute_production(product_id, int(quantity))
            return result
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def calculate_bom_cost(self, product_id):
        """Calcula el costo unitario basado en el BOM."""
        print(f"[Python] calculate_bom_cost() llamado para producto ID {product_id}")
        try:
            result = database.calculate_bom_cost(product_id)
            if result:
                return {'success': True, 'data': result}
            return {'success': False, 'message': 'Producto no encontrado'}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    # --- API de Finanzas ---

    def add_revenue_entry(self, description, amount, date=None):
        """Añade un registro de ingreso."""
        print(f"[Python] add_revenue_entry: {description}, {amount}, fecha: {date}")
        try:
            database.add_revenue(description, float(amount), date)
            return {'success': True, 'message': 'Ingreso añadido'}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    def add_cost_entry(self, description, amount, date=None, category='Otros'):
        """Añade un registro de costo."""
        print(f"[Python] add_cost_entry: {description}, {amount}, categoría: {category}, fecha: {date}")
        try:
            database.add_cost(description, float(amount), date, category)
            return {'success': True, 'message': 'Costo añadido'}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    def get_recent_finances(self):
        """Obtiene finanzas recientes para la vista de Finanzas."""
        print("[Python] get_recent_finances() llamado")
        try:
            revenue = database.get_recent_revenue()
            costs = database.get_recent_costs()
            return {'success': True, 'data': {'revenue': revenue, 'costs': costs}}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    def get_all_finances(self):
        """Obtiene todas las finanzas para edición."""
        print("[Python] get_all_finances() llamado")
        try:
            revenue = database.get_all_revenue()
            costs = database.get_all_costs()
            return {'success': True, 'data': {'revenue': revenue, 'costs': costs}}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    def update_revenue_entry(self, revenue_id, description, amount, date=None):
        """Actualiza un registro de ingreso."""
        print(f"[Python] update_revenue_entry() llamado para ID {revenue_id}")
        try:
            database.update_revenue(revenue_id, description, float(amount), date)
            return {'success': True, 'message': 'Ingreso actualizado'}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    def update_cost_entry(self, cost_id, description, amount, date=None, category='Otros'):
        """Actualiza un registro de costo."""
        print(f"[Python] update_cost_entry() llamado para ID {cost_id}")
        try:
            database.update_cost(cost_id, description, float(amount), date, category)
            return {'success': True, 'message': 'Costo actualizado'}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    def delete_revenue_entry(self, revenue_id):
        """Elimina un registro de ingreso."""
        print(f"[Python] delete_revenue_entry() llamado para ID {revenue_id}")
        try:
            database.delete_revenue(revenue_id)
            return {'success': True, 'message': 'Ingreso eliminado'}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    def delete_cost_entry(self, cost_id):
        """Elimina un registro de costo."""
        print(f"[Python] delete_cost_entry() llamado para ID {cost_id}")
        try:
            database.delete_cost(cost_id)
            return {'success': True, 'message': 'Costo eliminado'}
        except Exception as e:
            return {'success': False, 'message': str(e)}


    # --- API de Dashboard (Ejemplo) ---

    def get_kpi_data(self, period='month'):
        """
        ¡MODIFICADO! Esta función ahora calcula todos los KPIs
        y obtiene los datos financieros reales con soporte para diferentes períodos.
        """
        print(f"[Python] get_kpi_data() llamado con período: {period}")
        try:
            # 1. Obtener datos financieros (¡Reales!) con período configurable
            financial_summary = database.get_financial_summary(period)
            
            # 2. Obtener datos de inventario y calcular KPIs
            products = database.get_all_products()
            total_stock_items = 0
            stock_alerts_count = 0
            total_inventory_value = 0
            
            for p in products:
                total_stock_items += p['stock']
                if p['stock'] < p['min_stock']:
                    stock_alerts_count += 1
                total_inventory_value += p['stock'] * p['cost'] # ¡Nuevo KPI!

            inventory_kpis = {
                'total_stock_items': total_stock_items,
                'stock_alerts_count': stock_alerts_count,
                'total_inventory_value': round(total_inventory_value, 2) # Redondear a 2 decimales
            }

            return {
                'success': True,
                'data': {
                    'financial_summary': financial_summary,
                    'inventory_kpis': inventory_kpis
                }
            }
        except Exception as e:
            print(f"Error en get_kpi_data: {e}")
            return {'success': False, 'message': str(e)}


    # --- API de Ventas ---
    
    def add_sale(self, product_id, product_name, quantity, unit_price, date=None):
        """Añade una venta al historial."""
        print(f"[Python] add_sale: {product_name}, cantidad: {quantity}, precio: {unit_price}")
        try:
            database.add_sale(product_id, product_name, float(quantity), float(unit_price), date)
            return {'success': True, 'message': 'Venta registrada'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def add_multiple_sales(self, sales_list):
        """Añade múltiples ventas al historial."""
        print(f"[Python] add_multiple_sales: {len(sales_list)} ventas")
        try:
            result = database.add_multiple_sales(sales_list)
            return result
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def get_all_sales(self):
        """Obtiene todas las ventas."""
        print("[Python] get_all_sales() llamado")
        try:
            sales = database.get_all_sales()
            return {'success': True, 'data': sales}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def get_recent_sales(self, limit=10):
        """Obtiene las ventas más recientes."""
        print(f"[Python] get_recent_sales() llamado con límite: {limit}")
        try:
            sales = database.get_recent_sales(limit)
            return {'success': True, 'data': sales}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def get_sale_by_id(self, sale_id):
        """Obtiene una venta por su ID."""
        print(f"[Python] get_sale_by_id() llamado para ID {sale_id}")
        try:
            sale = database.get_sale_by_id(sale_id)
            if sale:
                return {'success': True, 'data': sale}
            return {'success': False, 'message': 'Venta no encontrada'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def update_sale(self, sale_id, product_id, product_name, quantity, unit_price, date=None):
        """Actualiza una venta existente."""
        print(f"[Python] update_sale() llamado para ID {sale_id}")
        try:
            database.update_sale(sale_id, product_id, product_name, float(quantity), float(unit_price), date)
            return {'success': True, 'message': 'Venta actualizada'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def delete_sale(self, sale_id):
        """Elimina una venta."""
        print(f"[Python] delete_sale() llamado para ID {sale_id}")
        try:
            database.delete_sale(sale_id)
            return {'success': True, 'message': 'Venta eliminada'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def get_sales_by_period(self, period='month'):
        """Obtiene ventas filtradas por período."""
        print(f"[Python] get_sales_by_period() llamado con período: {period}")
        try:
            sales = database.get_sales_by_period(period)
            return {'success': True, 'data': sales}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    # --- API de Business Intelligence ---
    
    def get_top_products_by_sales(self, limit=5):
        """Obtiene los top productos más vendidos."""
        print(f"[Python] get_top_products_by_sales() llamado con límite: {limit}")
        try:
            products = database.get_top_products_by_sales(limit)
            return {'success': True, 'data': products}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def get_top_products_by_profitability(self, limit=5):
        """Obtiene los top productos más rentables."""
        print(f"[Python] get_top_products_by_profitability() llamado con límite: {limit}")
        try:
            products = database.get_top_products_by_profitability(limit)
            return {'success': True, 'data': products}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def get_cost_breakdown_by_category(self):
        """Obtiene el desglose de costos por categoría."""
        print("[Python] get_cost_breakdown_by_category() llamado")
        try:
            breakdown = database.get_cost_breakdown_by_category()
            return {'success': True, 'data': breakdown}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def get_products_without_movement(self, days=30):
        """Obtiene productos sin movimiento."""
        print(f"[Python] get_products_without_movement() llamado con días: {days}")
        try:
            products = database.get_products_without_movement(days)
            return {'success': True, 'data': products}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def get_inventory_valuation_by_category(self):
        """Obtiene la valorización del inventario por categoría."""
        print("[Python] get_inventory_valuation_by_category() llamado")
        try:
            valuation = database.get_inventory_valuation_by_category()
            return {'success': True, 'data': valuation}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def get_financial_metrics_current_month(self):
        """Obtiene métricas financieras del mes actual."""
        print("[Python] get_financial_metrics_current_month() llamado")
        try:
            metrics = database.get_financial_metrics_current_month()
            return {'success': True, 'data': metrics}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def get_bi_dashboard_data(self):
        """Obtiene todos los datos para el dashboard de BI."""
        print("[Python] get_bi_dashboard_data() llamado")
        try:
            top_sales = database.get_top_products_by_sales(5)
            top_profit = database.get_top_products_by_profitability(5)
            cost_breakdown = database.get_cost_breakdown_by_category()
            products_no_movement = database.get_products_without_movement(30)
            inventory_valuation = database.get_inventory_valuation_by_category()
            financial_metrics = database.get_financial_metrics_current_month()
            
            return {
                'success': True,
                'data': {
                    'top_sales': top_sales,
                    'top_profitability': top_profit,
                    'cost_breakdown': cost_breakdown,
                    'products_no_movement': products_no_movement,
                    'inventory_valuation': inventory_valuation,
                    'financial_metrics': financial_metrics
                }
            }
        except Exception as e:
            return {'success': False, 'message': str(e)}

    # --- Funciones de Exportación a Excel ---

    def export_to_excel(self):
        """
        Exporta todos los datos a un archivo Excel.
        """
        print("[Python] Exportando a Excel...")
        
        def _export():
            try:
                filepath = excel_export.export_to_excel()
                abs_path = os.path.abspath(filepath)
                self._last_excel_file = abs_path
                print(f"[Python] Exportación completada: {abs_path}")
                if self._window:
                    self._window.evaluate_js(f"showNotification('Exportación completada: {abs_path}')")
            except Exception as e:
                print(f"Error al exportar: {e}")
                if self._window:
                    error_msg = str(e).replace("'", "\\'")
                    self._window.evaluate_js(f"showNotification('Error al exportar: {error_msg}')")

        threading.Thread(target=_export).start()
        return {'success': True, 'message': 'Exportación iniciada...'}
    
    def export_sales_report(self, period='month'):
        """
        Exporta un informe de ventas por período a Excel.
        """
        print(f"[Python] Exportando informe de ventas ({period})...")
        
        def _export():
            try:
                filepath = excel_export.export_sales_report(period)
                abs_path = os.path.abspath(filepath)
                self._last_excel_file = abs_path
                print(f"[Python] Informe de ventas exportado: {abs_path}")
                if self._window:
                    self._window.evaluate_js(f"showNotification('Informe exportado: {abs_path}')")
            except Exception as e:
                print(f"Error al exportar informe: {e}")
                if self._window:
                    error_msg = str(e).replace("'", "\\'")
                    self._window.evaluate_js(f"showNotification('Error al exportar informe: {error_msg}')")

        threading.Thread(target=_export).start()
        return {'success': True, 'message': 'Exportación de informe iniciada...'}
    
    def open_excel_file(self, filepath=None):
        """
        Abre un archivo Excel con la aplicación predeterminada del sistema.
        Si no se proporciona filepath, intenta abrir el último archivo exportado.
        """
        try:
            if filepath is None:
                if hasattr(self, '_last_excel_file') and self._last_excel_file:
                    filepath = self._last_excel_file
                else:
                    # Buscar el archivo más reciente en el directorio de exportación
                    import glob
                    # Determinar el directorio de búsqueda
                    if platform.system() == 'Darwin' and '.app/Contents/MacOS' in sys.executable:
                        # En macOS desde .app bundle, buscar en Documents
                        search_dir = os.path.join(os.path.expanduser('~'), 'Documents', 'OpenPYME_ERP')
                        os.makedirs(search_dir, exist_ok=True)
                    else:
                        search_dir = os.getcwd()
                    
                    # Buscar archivos Excel
                    pattern1 = os.path.join(search_dir, "export_erp_*.xlsx")
                    pattern2 = os.path.join(search_dir, "informe_ventas_*.xlsx")
                    excel_files = glob.glob(pattern1) + glob.glob(pattern2)
                    
                    if excel_files:
                        filepath = max(excel_files, key=os.path.getctime)
                    else:
                        return {'success': False, 'message': f'No se encontró ningún archivo Excel exportado en {search_dir}'}
            
            abs_path = os.path.abspath(filepath)
            if not os.path.exists(abs_path):
                return {'success': False, 'message': f'El archivo no existe: {abs_path}'}
            
            print(f"[Python] Abriendo archivo Excel: {abs_path}")
            system = platform.system()
            if system == 'Windows':
                os.startfile(abs_path)
            elif system == 'Darwin':  # macOS
                subprocess.run(['open', abs_path])
            else:  # Linux
                subprocess.run(['xdg-open', abs_path])
            
            return {'success': True, 'message': f'Archivo abierto: {abs_path}'}
        except Exception as e:
            return {'success': False, 'message': str(e)}


def start_app():
    try:
        # Inicializar la base de datos al arrancar
        print("Iniciando la base de datos...")
        database.init_db()
        print("Base de datos lista.")

        # Detectar la ruta correcta para los archivos UI
        # Cuando se ejecuta desde PyInstaller, usar sys._MEIPASS
        # Cuando se ejecuta normalmente, usar la ruta relativa
        if getattr(sys, 'frozen', False):
            # Ejecutándose desde el bundle compilado de PyInstaller
            # PyInstaller coloca los archivos en sys._MEIPASS
            base_path = sys._MEIPASS
            html_path = os.path.join(base_path, 'app', 'ui', 'index.html')
            
            # Si no está ahí, buscar en Resources (para bundles macOS)
            if not os.path.exists(html_path):
                # Obtener la ruta del ejecutable
                if sys.platform == 'darwin' and '.app' in sys.executable:
                    # Estamos en un .app bundle de macOS
                    bundle_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(sys.executable))))
                    resources_path = os.path.join(bundle_path, 'Contents', 'Resources')
                    html_path = os.path.join(resources_path, 'app', 'ui', 'index.html')
        else:
            # Ejecutándose desde código fuente
            base_path = os.path.dirname(os.path.abspath(__file__))
            html_path = os.path.join(base_path, 'app', 'ui', 'index.html')
        
        # Verificar que el archivo existe, con múltiples fallbacks
        if not os.path.exists(html_path):
            # Fallback 1: ruta relativa desde donde se ejecuta
            html_path = 'app/ui/index.html'
            
        if not os.path.exists(html_path):
            # Fallback 2: buscar en el directorio actual
            html_path = os.path.abspath('app/ui/index.html')
            
        if not os.path.exists(html_path):
            # Fallback 3: buscar en el directorio del script
            html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'ui', 'index.html')
        
        # Convertir a ruta absoluta
        html_path = os.path.abspath(html_path)
        
        if not os.path.exists(html_path):
            raise FileNotFoundError(f"No se pudo encontrar app/ui/index.html. Buscado en: {html_path}")
        
        print(f"Cargando HTML desde: {html_path}")
        
        # Convertir a file:// URL para webview
        if not html_path.startswith('file://'):
            html_path = f"file://{html_path}"

        api = Api()
        window = webview.create_window(
            'OpenPYME ERP/CRM',
            html_path,  # Carga el archivo HTML principal con ruta corregida
            js_api=api,           # Expone la clase 'Api' a JavaScript
            width=1280,
            height=800,
            resizable=True,
            min_size=(800, 600)
        )
        api.set_window(window)
        webview.start(debug=False) # debug=False para producción (no abre DevTools automáticamente)
    except Exception as e:
        import traceback
        error_msg = f"Error al iniciar la aplicación:\n{str(e)}\n\n{traceback.format_exc()}"
        print(error_msg)
        # Mostrar error en una ventana si es posible
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Error", error_msg)
        except:
            pass
        raise

if __name__ == '__main__':
    try:
        start_app()
    except Exception as e:
        import traceback
        print(f"\n{'='*60}")
        print("ERROR FATAL:")
        print(f"{'='*60}")
        print(traceback.format_exc())
        print(f"{'='*60}")
        input("Presiona Enter para salir...")
        sys.exit(1)