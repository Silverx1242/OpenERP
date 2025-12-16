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
This is the main file that launches the application.
Uses 'pywebview' to create a native desktop window
that loads the frontend from the 'app/ui/' folder.
"""

# The API_BINDING is an object that allows JavaScript
# to call Python functions.
class Api:
    def __init__(self):
        self._window = None
        self._last_excel_file = None

    def set_window(self, window):
        self._window = window

    # --- Inventory API ---

    def load_products(self):
        """
        Called from JS when loading the page.
        Returns all products from the database.
        """
        print("[Python] load_products() called")
        try:
            products = database.get_all_products()
            return {'success': True, 'data': products}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    def add_product(self, name, product_type, stock, min_stock, cost, supplier=None, purchase_date=None, exit_date=None, sku=None, weight=0, stock_unit_type='units', additional_cost=0):
        """
        Called from JS when the user submits the form.
        Includes 'cost', supplier, dates, SKU, weight, stock unit type and additional cost.
        """
        print(f"[Python] add_product() called with: {name}, {product_type}, Cost: {cost}, Supplier: {supplier}, SKU: {sku}, Weight: {weight}, Stock Type: {stock_unit_type}, Additional Cost: {additional_cost}")
        try:
            database.add_product(name, product_type, float(stock), float(min_stock), float(cost), supplier, purchase_date, exit_date, sku, float(weight), stock_unit_type, float(additional_cost))
            return {'success': True, 'message': f'Product {name} added'}
        except Exception as e:
            print(f"Error adding product: {e}")
            return {'success': False, 'message': str(e)}

    def adjust_inventory(self, product_id, quantity_change):
        """
        Called from JS to adjust the stock of an item.
        """
        print(f"[Python] adjust_inventory() called for ID {product_id}, Change: {quantity_change}")
        try:
            database.update_product_stock(product_id, float(quantity_change))
            return {'success': True, 'message': 'Stock updated'}
        except Exception as e:
            print(f"Error adjusting stock: {e}")
            return {'success': False, 'message': str(e)}

    def update_product(self, product_id, name, product_type, stock, min_stock, cost, supplier=None, purchase_date=None, exit_date=None, sku=None, weight=0, stock_unit_type='units', additional_cost=0):
        """Updates an existing product."""
        print(f"[Python] update_product() called for ID {product_id}")
        try:
            database.update_product(product_id, name, product_type, float(stock), float(min_stock), float(cost), supplier, purchase_date, exit_date, sku, float(weight), stock_unit_type, float(additional_cost))
            return {'success': True, 'message': f'Product {name} updated'}
        except Exception as e:
            print(f"Error updating product: {e}")
            return {'success': False, 'message': str(e)}

    def delete_product(self, product_id):
        """Deletes a product."""
        print(f"[Python] delete_product() called for ID {product_id}")
        try:
            database.delete_product(product_id)
            return {'success': True, 'message': 'Product deleted'}
        except Exception as e:
            print(f"Error deleting product: {e}")
            return {'success': False, 'message': str(e)}


    def get_products_by_type(self, product_type):
        """Gets products filtered by type (for populating dropdowns)."""
        print(f"[Python] get_products_by_type({product_type}) called")
        try:
            products = database.get_products_by_type(product_type)
            return {'success': True, 'data': products}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    # --- BOM (Bill of Materials) API ---

    def get_bom(self, parent_product_id):
        """Gets the bill of materials for a product."""
        print(f"[Python] get_bom({parent_product_id}) called")
        try:
            bom_items = database.get_bom_for_product(parent_product_id)
            return {'success': True, 'data': bom_items}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    def add_bom_entry(self, parent_id, child_id, quantity):
        """Adds an entry to the BOM."""
        print(f"[Python] add_bom_entry({parent_id}, {child_id}, {quantity})")
        try:
            database.add_bom_entry(parent_id, child_id, float(quantity))
            return {'success': True, 'message': 'Component added to BOM'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def delete_bom_entry(self, bom_id):
        """Deletes an entry from the BOM."""
        print(f"[Python] delete_bom_entry({bom_id})")
        try:
            database.delete_bom_entry(bom_id)
            return {'success': True, 'message': 'Component removed from BOM'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def calculate_mrp_production(self, product_id):
        """Calculates how many products can be manufactured based on BOM and inventory."""
        print(f"[Python] calculate_mrp_production() called for product ID {product_id}")
        try:
            result = database.calculate_mrp_production(product_id)
            if result:
                return {'success': True, 'data': result}
            return {'success': False, 'message': 'Product not found'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def execute_production(self, product_id, quantity):
        """Executes production: reduces components and increases final product."""
        print(f"[Python] execute_production() called for product ID {product_id}, quantity: {quantity}")
        try:
            result = database.execute_production(product_id, int(quantity))
            return result
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def calculate_bom_cost(self, product_id):
        """Calculates unit cost based on BOM."""
        print(f"[Python] calculate_bom_cost() called for product ID {product_id}")
        try:
            result = database.calculate_bom_cost(product_id)
            if result:
                return {'success': True, 'data': result}
            return {'success': False, 'message': 'Product not found'}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    # --- Finance API ---

    def add_revenue_entry(self, description, amount, date=None):
        """Adds a revenue entry."""
        print(f"[Python] add_revenue_entry: {description}, {amount}, date: {date}")
        try:
            database.add_revenue(description, float(amount), date)
            return {'success': True, 'message': 'Revenue added'}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    def add_cost_entry(self, description, amount, date=None, category='Others'):
        """Adds a cost entry."""
        print(f"[Python] add_cost_entry: {description}, {amount}, category: {category}, date: {date}")
        try:
            database.add_cost(description, float(amount), date, category)
            return {'success': True, 'message': 'Cost added'}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    def get_recent_finances(self):
        """Gets recent finances for the Finance view."""
        print("[Python] get_recent_finances() called")
        try:
            revenue = database.get_recent_revenue()
            costs = database.get_recent_costs()
            return {'success': True, 'data': {'revenue': revenue, 'costs': costs}}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    def get_all_finances(self):
        """Gets all finances for editing."""
        print("[Python] get_all_finances() called")
        try:
            revenue = database.get_all_revenue()
            costs = database.get_all_costs()
            return {'success': True, 'data': {'revenue': revenue, 'costs': costs}}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    def update_revenue_entry(self, revenue_id, description, amount, date=None):
        """Updates a revenue entry."""
        print(f"[Python] update_revenue_entry() called for ID {revenue_id}")
        try:
            database.update_revenue(revenue_id, description, float(amount), date)
            return {'success': True, 'message': 'Revenue updated'}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    def update_cost_entry(self, cost_id, description, amount, date=None, category='Others'):
        """Updates a cost entry."""
        print(f"[Python] update_cost_entry() called for ID {cost_id}")
        try:
            database.update_cost(cost_id, description, float(amount), date, category)
            return {'success': True, 'message': 'Cost updated'}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    def delete_revenue_entry(self, revenue_id):
        """Deletes a revenue entry."""
        print(f"[Python] delete_revenue_entry() called for ID {revenue_id}")
        try:
            database.delete_revenue(revenue_id)
            return {'success': True, 'message': 'Revenue deleted'}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    def delete_cost_entry(self, cost_id):
        """Deletes a cost entry."""
        print(f"[Python] delete_cost_entry() called for ID {cost_id}")
        try:
            database.delete_cost(cost_id)
            return {'success': True, 'message': 'Cost deleted'}
        except Exception as e:
            return {'success': False, 'message': str(e)}


    # --- Dashboard API ---

    def get_kpi_data(self, period='month'):
        """
        This function now calculates all KPIs
        and gets real financial data with support for different periods.
        """
        print(f"[Python] get_kpi_data() called with period: {period}")
        try:
            # 1. Get financial data (Real!) with configurable period
            financial_summary = database.get_financial_summary(period)
            
            # 2. Get inventory data and calculate KPIs
            products = database.get_all_products()
            total_stock_items = 0
            stock_alerts_count = 0
            total_inventory_value = 0
            
            for p in products:
                total_stock_items += p['stock']
                if p['stock'] < p['min_stock']:
                    stock_alerts_count += 1
                total_inventory_value += p['stock'] * p['cost'] # New KPI!

            inventory_kpis = {
                'total_stock_items': total_stock_items,
                'stock_alerts_count': stock_alerts_count,
                'total_inventory_value': round(total_inventory_value, 2) # Round to 2 decimals
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


    # --- Sales API ---
    
    def add_sale(self, product_id, product_name, quantity, unit_price, date=None):
        """Adds a sale to the history."""
        print(f"[Python] add_sale: {product_name}, quantity: {quantity}, price: {unit_price}")
        try:
            database.add_sale(product_id, product_name, float(quantity), float(unit_price), date)
            return {'success': True, 'message': 'Sale registered'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def add_multiple_sales(self, sales_list):
        """Adds multiple sales to the history."""
        print(f"[Python] add_multiple_sales: {len(sales_list)} sales")
        try:
            result = database.add_multiple_sales(sales_list)
            return result
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def get_all_sales(self):
        """Gets all sales."""
        print("[Python] get_all_sales() called")
        try:
            sales = database.get_all_sales()
            return {'success': True, 'data': sales}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def get_recent_sales(self, limit=10):
        """Gets the most recent sales."""
        print(f"[Python] get_recent_sales() called with limit: {limit}")
        try:
            sales = database.get_recent_sales(limit)
            return {'success': True, 'data': sales}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def get_sale_by_id(self, sale_id):
        """Gets a sale by its ID."""
        print(f"[Python] get_sale_by_id() called for ID {sale_id}")
        try:
            sale = database.get_sale_by_id(sale_id)
            if sale:
                return {'success': True, 'data': sale}
            return {'success': False, 'message': 'Sale not found'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def update_sale(self, sale_id, product_id, product_name, quantity, unit_price, date=None):
        """Updates an existing sale."""
        print(f"[Python] update_sale() called for ID {sale_id}")
        try:
            database.update_sale(sale_id, product_id, product_name, float(quantity), float(unit_price), date)
            return {'success': True, 'message': 'Sale updated'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def delete_sale(self, sale_id):
        """Deletes a sale."""
        print(f"[Python] delete_sale() called for ID {sale_id}")
        try:
            database.delete_sale(sale_id)
            return {'success': True, 'message': 'Sale deleted'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def get_sales_by_period(self, period='month'):
        """Gets sales filtered by period."""
        print(f"[Python] get_sales_by_period() called with period: {period}")
        try:
            sales = database.get_sales_by_period(period)
            return {'success': True, 'data': sales}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    # --- Business Intelligence API ---
    
    def get_top_products_by_sales(self, limit=5):
        """Gets the top products by sales."""
        print(f"[Python] get_top_products_by_sales() called with limit: {limit}")
        try:
            products = database.get_top_products_by_sales(limit)
            return {'success': True, 'data': products}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def get_top_products_by_profitability(self, limit=5):
        """Gets the top products by profitability."""
        print(f"[Python] get_top_products_by_profitability() called with limit: {limit}")
        try:
            products = database.get_top_products_by_profitability(limit)
            return {'success': True, 'data': products}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def get_cost_breakdown_by_category(self):
        """Gets the cost breakdown by category."""
        print("[Python] get_cost_breakdown_by_category() called")
        try:
            breakdown = database.get_cost_breakdown_by_category()
            return {'success': True, 'data': breakdown}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def get_products_without_movement(self, days=30):
        """Gets products without movement."""
        print(f"[Python] get_products_without_movement() called with days: {days}")
        try:
            products = database.get_products_without_movement(days)
            return {'success': True, 'data': products}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def get_inventory_valuation_by_category(self):
        """Gets inventory valuation by category."""
        print("[Python] get_inventory_valuation_by_category() called")
        try:
            valuation = database.get_inventory_valuation_by_category()
            return {'success': True, 'data': valuation}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def get_financial_metrics_current_month(self):
        """Gets financial metrics for the current month."""
        print("[Python] get_financial_metrics_current_month() called")
        try:
            metrics = database.get_financial_metrics_current_month()
            return {'success': True, 'data': metrics}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def get_bi_dashboard_data(self):
        """Gets all data for the BI dashboard."""
        print("[Python] get_bi_dashboard_data() called")
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

    # --- Excel Export Functions ---

    def export_to_excel(self):
        """
        Exports all data to an Excel file.
        """
        print("[Python] Exporting to Excel...")
        
        def _export():
            try:
                filepath = excel_export.export_to_excel()
                abs_path = os.path.abspath(filepath)
                self._last_excel_file = abs_path
                print(f"[Python] Export completed: {abs_path}")
                if self._window:
                    self._window.evaluate_js(f"showNotification('Export completed: {abs_path}')")
            except Exception as e:
                print(f"Error exporting: {e}")
                if self._window:
                    error_msg = str(e).replace("'", "\\'")
                    self._window.evaluate_js(f"showNotification('Error exporting: {error_msg}')")

        threading.Thread(target=_export).start()
        return {'success': True, 'message': 'Export started...'}
    
    def export_sales_report(self, period='month'):
        """
        Exports a sales report by period to Excel.
        """
        print(f"[Python] Exporting sales report ({period})...")
        
        def _export():
            try:
                filepath = excel_export.export_sales_report(period)
                abs_path = os.path.abspath(filepath)
                self._last_excel_file = abs_path
                print(f"[Python] Sales report exported: {abs_path}")
                if self._window:
                    self._window.evaluate_js(f"showNotification('Report exported: {abs_path}')")
            except Exception as e:
                print(f"Error exporting report: {e}")
                if self._window:
                    error_msg = str(e).replace("'", "\\'")
                    self._window.evaluate_js(f"showNotification('Error exporting report: {error_msg}')")

        threading.Thread(target=_export).start()
        return {'success': True, 'message': 'Report export started...'}
    
    def open_excel_file(self, filepath=None):
        """
        Opens an Excel file with the system's default application.
        If filepath is not provided, tries to open the last exported file.
        """
        try:
            if filepath is None:
                if hasattr(self, '_last_excel_file') and self._last_excel_file:
                    filepath = self._last_excel_file
                else:
                    # Search for the most recent file in the export directory
                    import glob
                    # Determine the search directory
                    if platform.system() == 'Darwin' and '.app/Contents/MacOS' in sys.executable:
                        # On macOS from .app bundle, search in Documents
                        search_dir = os.path.join(os.path.expanduser('~'), 'Documents', 'OpenERP')
                        os.makedirs(search_dir, exist_ok=True)
                    else:
                        search_dir = os.getcwd()
                    
                    # Search for Excel files
                    pattern1 = os.path.join(search_dir, "export_erp_*.xlsx")
                    pattern2 = os.path.join(search_dir, "sales_report_*.xlsx")
                    excel_files = glob.glob(pattern1) + glob.glob(pattern2)
                    
                    if excel_files:
                        filepath = max(excel_files, key=os.path.getctime)
                    else:
                        return {'success': False, 'message': f'No exported Excel file found in {search_dir}'}
            
            abs_path = os.path.abspath(filepath)
            if not os.path.exists(abs_path):
                return {'success': False, 'message': f'File does not exist: {abs_path}'}
            
            print(f"[Python] Opening Excel file: {abs_path}")
            system = platform.system()
            if system == 'Windows':
                os.startfile(abs_path)
            elif system == 'Darwin':  # macOS
                subprocess.run(['open', abs_path])
            else:  # Linux
                subprocess.run(['xdg-open', abs_path])
            
            return {'success': True, 'message': f'File opened: {abs_path}'}
        except Exception as e:
            return {'success': False, 'message': str(e)}


def start_app():
    try:
        # Initialize the database on startup
        print("Starting database...")
        database.init_db()
        print("Database ready.")

        # Detect the correct path for UI files
        # When running from PyInstaller, use sys._MEIPASS
        # When running normally, use the relative path
        if getattr(sys, 'frozen', False):
            # Running from PyInstaller compiled bundle
            # PyInstaller places files in sys._MEIPASS
            base_path = sys._MEIPASS
            html_path = os.path.join(base_path, 'app', 'ui', 'index.html')
            
            # If not there, search in Resources (for macOS bundles)
            if not os.path.exists(html_path):
                # Get the executable path
                if sys.platform == 'darwin' and '.app' in sys.executable:
                    # We're in a macOS .app bundle
                    bundle_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(sys.executable))))
                    resources_path = os.path.join(bundle_path, 'Contents', 'Resources')
                    html_path = os.path.join(resources_path, 'app', 'ui', 'index.html')
        else:
            # Running from source code
            base_path = os.path.dirname(os.path.abspath(__file__))
            html_path = os.path.join(base_path, 'app', 'ui', 'index.html')
        
        # Verify the file exists, with multiple fallbacks
        if not os.path.exists(html_path):
            # Fallback 1: relative path from where it's executed
            html_path = 'app/ui/index.html'
            
        if not os.path.exists(html_path):
            # Fallback 2: search in current directory
            html_path = os.path.abspath('app/ui/index.html')
            
        if not os.path.exists(html_path):
            # Fallback 3: search in script directory
            html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'ui', 'index.html')
        
        # Convert to absolute path
        html_path = os.path.abspath(html_path)
        
        if not os.path.exists(html_path):
            raise FileNotFoundError(f"Could not find app/ui/index.html. Searched in: {html_path}")
        
        print(f"Loading HTML from: {html_path}")
        
        # Convert to file:// URL for webview
        if not html_path.startswith('file://'):
            html_path = f"file://{html_path}"

        api = Api()
        window = webview.create_window(
            'OpenERP',
            html_path,  # Loads the main HTML file with corrected path
            js_api=api,           # Exposes the 'Api' class to JavaScript
            width=1280,
            height=800,
            resizable=True,
            min_size=(800, 600)
        )
        api.set_window(window)
        webview.start(debug=False) # debug=False for production (doesn't open DevTools automatically)
    except Exception as e:
        import traceback
        error_msg = f"Error starting application:\n{str(e)}\n\n{traceback.format_exc()}"
        print(error_msg)
        # Show error in a window if possible
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
        print("FATAL ERROR:")
        print(f"{'='*60}")
        print(traceback.format_exc())
        print(f"{'='*60}")
        input("Press Enter to exit...")
        sys.exit(1)