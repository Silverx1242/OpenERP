import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
from datetime import datetime
import os
import sys
from app import database

"""
Módulo para exportar datos de la base de datos a archivos Excel.
"""

def get_export_directory():
    """
    Obtiene el directorio adecuado para guardar archivos exportados.
    En macOS, cuando se ejecuta desde un .app bundle, usa el directorio del usuario.
    """
    # Si estamos ejecutando desde un .app bundle en macOS
    if sys.platform == 'darwin' and '.app/Contents/MacOS' in sys.executable:
        # Usar el directorio del usuario o Documents
        home_dir = os.path.expanduser('~')
        documents_dir = os.path.join(home_dir, 'Documents', 'OpenPYME_ERP')
        # Crear el directorio si no existe
        os.makedirs(documents_dir, exist_ok=True)
        return documents_dir
    else:
        # Para Windows/Linux o ejecución normal, usar el directorio actual
        return os.getcwd()

def export_to_excel(filepath=None):
    """
    Exporta todos los datos de la base de datos a un archivo Excel.
    Crea múltiples hojas: Inventario, Ventas, Ingresos, Costos, BOM
    """
    if filepath is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"export_erp_{timestamp}.xlsx"
        export_dir = get_export_directory()
        filepath = os.path.join(export_dir, filename)
    else:
        # Si se proporciona una ruta relativa, usar el directorio de exportación
        if not os.path.isabs(filepath):
            export_dir = get_export_directory()
            filepath = os.path.join(export_dir, os.path.basename(filepath))
    
    wb = openpyxl.Workbook()
    
    # Eliminar hoja por defecto
    if 'Sheet' in wb.sheetnames:
        wb.remove(wb['Sheet'])
    
    # 1. Hoja de Inventario
    sheet_inventory = wb.create_sheet("Inventario")
    products = database.get_all_products()
    
    headers_inv = ['ID', 'SKU', 'Nombre', 'Tipo', 'Stock', 'Stock Mínimo', 'Costo Unitario', 
                   'Proveedor', 'Fecha Compra', 'Fecha Salida', 'Valor Total']
    sheet_inventory.append(headers_inv)
    
    # Estilo para encabezados
    header_fill = PatternFill(start_color="4285f4", end_color="4285f4", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF")
    
    for cell in sheet_inventory[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center")
    
    for p in products:
        total_value = p['stock'] * (p['cost'] or 0)
        sheet_inventory.append([
            p['id'],
            p.get('sku', '') or '',
            p['name'],
            p['product_type'],
            p['stock'],
            p['min_stock'],
            p['cost'] or 0,
            p['supplier'] or '',
            p['purchase_date'] or '',
            p['exit_date'] or '',
            total_value
        ])
    
    # Ajustar ancho de columnas
    for col in range(1, len(headers_inv) + 1):
        sheet_inventory.column_dimensions[get_column_letter(col)].width = 15
    
    # 2. Hoja de Ventas
    sheet_sales = wb.create_sheet("Ventas")
    sales = database.get_all_sales()
    
    headers_sales = ['ID', 'Producto', 'Cantidad', 'Precio Unitario', 'Total', 'Fecha']
    sheet_sales.append(headers_sales)
    
    for cell in sheet_sales[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center")
    
    for s in sales:
        sheet_sales.append([
            s['id'],
            s['product_name'],
            s['quantity'],
            s['unit_price'],
            s['total_amount'],
            s['date']
        ])
    
    for col in range(1, len(headers_sales) + 1):
        sheet_sales.column_dimensions[get_column_letter(col)].width = 18
    
    # 3. Hoja de Ingresos
    sheet_revenue = wb.create_sheet("Ingresos")
    revenue = database.get_all_revenue()
    
    headers_revenue = ['ID', 'Descripción', 'Monto', 'Fecha']
    sheet_revenue.append(headers_revenue)
    
    for cell in sheet_revenue[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center")
    
    for r in revenue:
        sheet_revenue.append([
            r['id'],
            r['description'],
            r['amount'],
            r['date']
        ])
    
    for col in range(1, len(headers_revenue) + 1):
        sheet_revenue.column_dimensions[get_column_letter(col)].width = 20
    
    # 4. Hoja de Costos
    sheet_costs = wb.create_sheet("Costos")
    costs = database.get_all_costs()
    
    headers_costs = ['ID', 'Descripción', 'Monto', 'Categoría', 'Fecha']
    sheet_costs.append(headers_costs)
    
    for cell in sheet_costs[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center")
    
    for c in costs:
        sheet_costs.append([
            c['id'],
            c['description'],
            c['amount'],
            c.get('category', 'Otros'),
            c['date']
        ])
    
    for col in range(1, len(headers_costs) + 1):
        sheet_costs.column_dimensions[get_column_letter(col)].width = 20
    
    # 5. Hoja de BOM
    sheet_bom = wb.create_sheet("BOM")
    products = database.get_all_products()
    
    headers_bom = ['Producto Padre', 'Insumo Hijo', 'Cantidad']
    sheet_bom.append(headers_bom)
    
    for cell in sheet_bom[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center")
    
    for p in products:
        bom_items = database.get_bom_for_product(p['id'])
        for bom in bom_items:
            sheet_bom.append([
                p['name'],
                bom['child_product_name'],
                bom['quantity']
            ])
    
    for col in range(1, len(headers_bom) + 1):
        sheet_bom.column_dimensions[get_column_letter(col)].width = 25
    
    # Guardar archivo
    wb.save(filepath)
    return filepath

def export_sales_report(period='month', filepath=None):
    """
    Exporta un informe de ventas filtrado por período a Excel.
    period puede ser: 'day', 'week', 'month', 'year'
    """
    if filepath is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        period_names = {'day': 'dia', 'week': 'semana', 'month': 'mes', 'year': 'año'}
        period_name = period_names.get(period, 'mes')
        filename = f"informe_ventas_{period_name}_{timestamp}.xlsx"
        export_dir = get_export_directory()
        filepath = os.path.join(export_dir, filename)
    else:
        # Si se proporciona una ruta relativa, usar el directorio de exportación
        if not os.path.isabs(filepath):
            export_dir = get_export_directory()
            filepath = os.path.join(export_dir, os.path.basename(filepath))
    
    wb = openpyxl.Workbook()
    
    # Eliminar hoja por defecto
    if 'Sheet' in wb.sheetnames:
        wb.remove(wb['Sheet'])
    
    # Obtener ventas del período
    sales = database.get_sales_by_period(period)
    
    # Hoja de Informe de Ventas
    sheet = wb.create_sheet("Informe de Ventas")
    
    # Título
    period_names = {
        'day': 'Día Actual',
        'week': 'Semana Actual',
        'month': 'Mes Actual',
        'year': 'Año Actual'
    }
    title = period_names.get(period, 'Mes Actual')
    sheet.merge_cells('A1:F1')
    title_cell = sheet['A1']
    title_cell.value = f"Informe de Ventas - {title}"
    title_cell.font = Font(bold=True, size=14)
    title_cell.alignment = Alignment(horizontal="center")
    
    # Encabezados
    headers = ['ID', 'Fecha', 'Producto', 'Cantidad', 'Precio Unitario', 'Total']
    sheet.append([])  # Línea en blanco
    sheet.append(headers)
    
    # Estilo para encabezados
    header_fill = PatternFill(start_color="4285f4", end_color="4285f4", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF")
    
    for cell in sheet[3]:  # Fila 3 (después del título y línea en blanco)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center")
    
    # Datos
    total_general = 0
    for s in sales:
        date_str = s['date'] if s['date'] else ''
        if date_str:
            try:
                if isinstance(date_str, str):
                    date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    date_str = date_obj.strftime('%Y-%m-%d %H:%M:%S')
            except:
                pass
        
        sheet.append([
            s['id'],
            date_str,
            s['product_name'],
            s['quantity'],
            s['unit_price'],
            s['total_amount']
        ])
        total_general += s['total_amount']
    
    # Totales
    sheet.append([])
    sheet.append(['', '', '', '', 'TOTAL:', total_general])
    total_row = sheet[sheet.max_row]
    total_row[4].font = Font(bold=True)
    total_row[5].font = Font(bold=True)
    total_row[5].fill = PatternFill(start_color="34a853", end_color="34a853", fill_type="solid")
    total_row[5].font = Font(bold=True, color="FFFFFF")
    
    # Estadísticas
    sheet.append([])
    stats_row = sheet.max_row + 1
    sheet.cell(row=stats_row, column=1).value = 'ESTADÍSTICAS'
    sheet.cell(row=stats_row, column=1).font = Font(bold=True)
    stats_row += 1
    sheet.cell(row=stats_row, column=1).value = 'Total de Ventas:'
    sheet.cell(row=stats_row, column=2).value = len(sales)
    stats_row += 1
    sheet.cell(row=stats_row, column=1).value = 'Total Recaudado:'
    sheet.cell(row=stats_row, column=2).value = f"$ {total_general:.2f}"
    stats_row += 1
    if len(sales) > 0:
        sheet.cell(row=stats_row, column=1).value = 'Ticket Promedio:'
        sheet.cell(row=stats_row, column=2).value = f"$ {total_general / len(sales):.2f}"
    
    # Ajustar ancho de columnas
    sheet.column_dimensions['A'].width = 10
    sheet.column_dimensions['B'].width = 20
    sheet.column_dimensions['C'].width = 30
    sheet.column_dimensions['D'].width = 12
    sheet.column_dimensions['E'].width = 15
    sheet.column_dimensions['F'].width = 15
    
    # Guardar archivo
    wb.save(filepath)
    return filepath

