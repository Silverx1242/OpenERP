import gspread
from app import database
import time

"""
Este módulo maneja la sincronización con Google Sheets.

IMPORTANTE:
Para que esto funcione, el usuario debe:
1. Ir a Google Cloud Console.
2. Crear un proyecto.
3. Habilitar la API de Google Sheets y la API de Google Drive.
4. Crear una Cuenta de Servicio (Service Account).
5. Descargar el archivo JSON de credenciales y guardarlo como 'service_account.json'
   en el mismo directorio.
6. Compartir la Google Sheet (por email) con el email de la cuenta de servicio.
"""

SERVICE_ACCOUNT_FILE = 'service_account.json'
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# ID de la Google Sheet (de la URL)
# Ejemplo: https://docs.google.com/spreadsheets/d/ESTE_ES_EL_ID/edit
GOOGLE_SHEET_ID = 'TU_GOOGLE_SHEET_ID_AQUI' 

def get_gspread_client():
    """Autentica y devuelve el cliente de gspread."""
    try:
        gc = gspread.service_account(filename=SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        return gc
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{SERVICE_ACCOUNT_FILE}'.")
        print("Por favor, sigue las instrucciones en 'g_sheets.py' para configurarlo.")
        return None
    except Exception as e:
        print(f"Error al autenticar con Google: {e}")
        return None

def export_all_data():
    """
    Exporta los datos de la base de datos local (SQLite) a Google Sheets.
    Esto sobrescribe las hojas.
    """
    gc = get_gspread_client()
    if not gc:
        return

    try:
        # Abrir el workbook (archivo)
        workbook = gc.open_by_key(GOOGLE_SHEET_ID)

        # 1. Exportar Productos
        products_sheet = workbook.worksheet('Inventario') # Asume que la hoja se llama 'Inventario'
        products_data = database.get_all_products()
        
        # Preparar los datos (encabezados + filas)
        # ¡ACTUALIZADO! Añadido 'Costo'
        export_data = [['ID', 'Nombre', 'Tipo', 'Stock', 'Min_Stock', 'Costo']]
        for p in products_data:
            export_data.append([p['id'], p['name'], p['product_type'], p['stock'], p['min_stock'], p['cost']])
        
        products_sheet.clear()
        products_sheet.update(export_data, 'A1')
        print("Exportación de inventario a Google Sheets completada.")
        time.sleep(1) # Pequeña pausa para no saturar la API

        # 2. Exportar BOM (Lista de Materiales)
        bom_sheet = workbook.worksheet('BOM') # Asume hoja 'BOM'
        
        # Necesitamos los nombres, no solo los IDs
        all_products = {p['id']: p['name'] for p in products_data}
        conn = database.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT parent_product_id, child_product_id, quantity FROM bill_of_materials")
        bom_data = cursor.fetchall()
        conn.close()

        export_data_bom = [['Producto Padre (Nombre)', 'Insumo Hijo (Nombre)', 'Cantidad']]
        for bom_entry in bom_data:
            parent_name = all_products.get(bom_entry['parent_product_id'], 'ID Desconocido')
            child_name = all_products.get(bom_entry['child_product_id'], 'ID Desconocido')
            export_data_bom.append([parent_name, child_name, bom_entry['quantity']])
        
        bom_sheet.clear()
        bom_sheet.update(export_data_bom, 'A1')
        print("Exportación de BOM a Google Sheets completada.")
        time.sleep(1)

        # 3. Exportar Finanzas (Revenue y Costs)
        # (Se podrían exportar a hojas separadas o combinadas)
        # ... (Lógica similar para revenue y costs) ...

    except gspread.exceptions.SpreadsheetNotFound:
        print(f"Error: No se encontró la Google Sheet con ID: {GOOGLE_SHEET_ID}")
    except gspread.exceptions.WorksheetNotFound:
        print("Error: No se encontraron las hojas requeridas (ej: 'Inventario', 'BOM') en la Google Sheet.")
    except Exception as e:
        print(f"Error durante la exportación a Google Sheets: {e}")

# --- Funciones de IMPORTACIÓN ---

def import_all_data():
    """
    Importa datos desde Google Sheets a la base de datos local.
    Esta es una operación destructiva (borra y reemplaza).
    """
    gc = get_gspread_client()
    if not gc:
        return

    try:
        workbook = gc.open_by_key(GOOGLE_SHEET_ID)

        # 1. Importar Productos
        products_sheet = workbook.worksheet('Inventario')
        # get_all_records() convierte la hoja en una lista de diccionarios
        products_from_sheet = products_sheet.get_all_records()
        
        conn = database.get_db_connection()
        cursor = conn.cursor()
        
        # Limpiar la tabla local primero
        cursor.execute("DELETE FROM products")
        print("Tabla 'products' local limpiada.")

        # Insertar los nuevos datos
        # ¡ACTUALIZADO! Añadido 'Costo'
        for p in products_from_sheet:
            cursor.execute(
                "INSERT INTO products (name, product_type, stock, min_stock, cost) VALUES (?, ?, ?, ?, ?)",
                (p['Nombre'], p['Tipo'], p['Stock'], p['Min_Stock'], p.get('Costo', 0)) # Usar .get() para retrocompatibilidad
            )
        conn.commit()
        print(f"Importados {len(products_from_sheet)} productos desde Google Sheets.")
        time.sleep(1)

        # 2. Importar BOM
        # (Esto debe hacerse DESPUÉS de importar productos para tener los IDs)
        
        # Crear un mapa de Nombre -> ID de los productos que acabamos de insertar
        cursor.execute("SELECT id, name FROM products")
        product_name_to_id = {row['name']: row['id'] for row in cursor.fetchall()}

        bom_sheet = workbook.worksheet('BOM')
        bom_from_sheet = bom_sheet.get_all_records()

        # Limpiar BOM local
        cursor.execute("DELETE FROM bill_of_materials")
        print("Tabla 'bill_of_materials' local limpiada.")
        
        for bom_entry in bom_from_sheet:
            parent_id = product_name_to_id.get(bom_entry['Producto Padre (Nombre)'])
            child_id = product_name_to_id.get(bom_entry['Insumo Hijo (Nombre)'])
            
            if parent_id and child_id:
                cursor.execute(
                    "INSERT INTO bill_of_materials (parent_product_id, child_product_id, quantity) VALUES (?, ?, ?)",
                    (parent_id, child_id, bom_entry['Cantidad'])
                )
            else:
                print(f"Error al importar BOM: No se encontró el producto '{bom_entry['Producto Padre (Nombre)']}' o '{bom_entry['Insumo Hijo (Nombre)']}'")
        
        conn.commit()
        print(f"Importadas {len(bom_from_sheet)} entradas de BOM desde Google Sheets.")
        
        conn.close()

        # 3. Importar Finanzas (Revenue y Costs)
        # ... (Lógica similar) ...

    except Exception as e:
        print(f"Error durante la importación desde Google Sheets: {e}")
        # Re-lanzar la excepción para que el hilo en main.py la capture
        raise e