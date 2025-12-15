import sqlite3
import os
import sys

"""
Este módulo maneja toda la interacción con la base de datos local SQLite.
(Versión extendida con Costos de Producto y ajuste de stock)
"""

def get_db_path():
    """
    Obtiene la ruta correcta para el archivo de base de datos.
    En macOS cuando se ejecuta desde .app bundle, usa el directorio del usuario.
    """
    if getattr(sys, 'frozen', False):
        # Ejecutándose desde un ejecutable compilado
        if sys.platform == 'darwin' and '.app' in sys.executable:
            # macOS: usar directorio Documents del usuario
            db_dir = os.path.join(os.path.expanduser('~'), 'Documents', 'OpenPYME_ERP')
            os.makedirs(db_dir, exist_ok=True)
            return os.path.join(db_dir, 'erp_data.db')
        else:
            # Windows/Linux: usar directorio del ejecutable
            if hasattr(sys, '_MEIPASS'):
                # PyInstaller: usar directorio del ejecutable, no _MEIPASS
                base_path = os.path.dirname(sys.executable)
            else:
                base_path = os.path.dirname(os.path.abspath(sys.executable))
            return os.path.join(base_path, 'erp_data.db')
    else:
        # Ejecutándose desde código fuente: usar directorio del proyecto
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, 'erp_data.db')

DB_FILE = get_db_path()

def get_db_connection():
    """Conecta a la base de datos SQLite."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row # Permite acceder a los resultados por nombre de columna
    return conn

def init_db():
    """
    Inicializa la base de datos.
    Crea las tablas si no existen.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # --- Tabla de Productos (Inventario) ---
    # product_type: 'final' (para vender), 'hijo' (insumo), 'padre' (sub-ensamblaje), 'otro' (gastos)
    # ¡NUEVO! Añadido campo 'cost', proveedor, fecha_compra, fecha_salida, SKU
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sku TEXT UNIQUE, -- Código SKU/ID del producto
        name TEXT NOT NULL UNIQUE,
        product_type TEXT NOT NULL CHECK(product_type IN ('final', 'hijo', 'padre', 'otro')),
        stock REAL NOT NULL DEFAULT 0,
        min_stock REAL NOT NULL DEFAULT 0,
        cost REAL NOT NULL DEFAULT 0, -- Costo unitario del producto
        supplier TEXT, -- Proveedor
        purchase_date DATE, -- Fecha de compra
        exit_date DATE, -- Fecha de salida
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    ''')
    
    # Migración: Agregar nuevas columnas si no existen (para bases de datos existentes)
    try:
        cursor.execute('ALTER TABLE products ADD COLUMN cost REAL NOT NULL DEFAULT 0')
    except sqlite3.OperationalError:
        pass  # La columna ya existe
    
    try:
        cursor.execute('ALTER TABLE products ADD COLUMN supplier TEXT')
    except sqlite3.OperationalError:
        pass  # La columna ya existe
    
    try:
        cursor.execute('ALTER TABLE products ADD COLUMN purchase_date DATE')
    except sqlite3.OperationalError:
        pass  # La columna ya existe
    
    try:
        cursor.execute('ALTER TABLE products ADD COLUMN exit_date DATE')
    except sqlite3.OperationalError:
        pass  # La columna ya existe
    
    try:
        cursor.execute('ALTER TABLE products ADD COLUMN sku TEXT')
    except sqlite3.OperationalError:
        pass  # La columna ya existe
    
    try:
        cursor.execute('ALTER TABLE products ADD COLUMN weight REAL DEFAULT 0')
    except sqlite3.OperationalError:
        pass  # La columna ya existe
    
    try:
        cursor.execute('ALTER TABLE products ADD COLUMN stock_unit_type TEXT DEFAULT "units"')
    except sqlite3.OperationalError:
        pass  # La columna ya existe
    
    # Asegurar que stock_unit_type tenga valores válidos
    try:
        cursor.execute('UPDATE products SET stock_unit_type = "units" WHERE stock_unit_type IS NULL OR stock_unit_type NOT IN ("units", "grams")')
    except sqlite3.OperationalError:
        pass
    
    try:
        cursor.execute('ALTER TABLE products ADD COLUMN additional_cost REAL DEFAULT 0')
    except sqlite3.OperationalError:
        pass  # La columna ya existe
    
    conn.commit()

    # --- Tabla de BOM (Bill of Materials) ---
    # Define qué 'hijos' componen un 'padre' o 'final'.
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS bill_of_materials (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        parent_product_id INTEGER NOT NULL, -- ID del producto 'final' o 'padre'
        child_product_id INTEGER NOT NULL,  -- ID del producto 'hijo'
        quantity REAL NOT NULL DEFAULT 1,   -- Cuántos 'hijos' se necesitan
        FOREIGN KEY (parent_product_id) REFERENCES products(id) ON DELETE CASCADE,
        FOREIGN KEY (child_product_id) REFERENCES products(id) ON DELETE CASCADE
    );
    ''')
    
    # --- Tablas de Finanzas ---
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS revenue (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        description TEXT,
        amount REAL NOT NULL,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS costs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        description TEXT,
        amount REAL NOT NULL,
        category TEXT DEFAULT 'Otros',
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    ''')
    
    # --- Tabla de Ventas (Historial de Ventas) ---
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        product_name TEXT NOT NULL,
        quantity REAL NOT NULL,
        unit_price REAL NOT NULL,
        total_amount REAL NOT NULL,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE SET NULL
    );
    ''')
    
    # Migración: Agregar columna category a costs si no existe
    try:
        cursor.execute('ALTER TABLE costs ADD COLUMN category TEXT DEFAULT "Otros"')
    except sqlite3.OperationalError:
        pass  # La columna ya existe

    conn.commit()
    conn.close()

# --- Funciones CRUD de Productos ---

def add_product(name, product_type, stock, min_stock, cost, supplier=None, purchase_date=None, exit_date=None, sku=None, weight=0, stock_unit_type='units', additional_cost=0):
    """Añade un nuevo producto al inventario (con costo, proveedor, fechas, SKU, gramaje, tipo de unidad de stock y costo adicional)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    # Validar stock_unit_type
    if stock_unit_type not in ('units', 'grams'):
        stock_unit_type = 'units'
    cursor.execute(
        "INSERT INTO products (name, product_type, stock, min_stock, cost, supplier, purchase_date, exit_date, sku, weight, stock_unit_type, additional_cost) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (name, product_type, stock, min_stock, cost, supplier, purchase_date, exit_date, sku, weight, stock_unit_type, additional_cost)
    )
    conn.commit()
    conn.close()

def update_product_stock(product_id, quantity_change):
    """
    ¡NUEVO! Ajusta el stock de un producto.
    Usa un cambio relativo (ej: +5 o -3).
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE products SET stock = stock + ? WHERE id = ?",
        (quantity_change, product_id)
    )
    conn.commit()
    conn.close()


def update_product(product_id, name, product_type, stock, min_stock, cost, supplier=None, purchase_date=None, exit_date=None, sku=None, weight=0, stock_unit_type='units', additional_cost=0):
    """Actualiza un producto existente en la base de datos (con costo, proveedor, fechas, SKU, gramaje, tipo de unidad de stock y costo adicional)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    # Validar stock_unit_type
    if stock_unit_type not in ('units', 'grams'):
        stock_unit_type = 'units'
    cursor.execute(
        "UPDATE products SET name = ?, product_type = ?, stock = ?, min_stock = ?, cost = ?, supplier = ?, purchase_date = ?, exit_date = ?, sku = ?, weight = ?, stock_unit_type = ?, additional_cost = ? WHERE id = ?",
        (name, product_type, stock, min_stock, cost, supplier, purchase_date, exit_date, sku, weight, stock_unit_type, additional_cost, product_id)
    )
    conn.commit()
    conn.close()

def delete_product(product_id):
    """Elimina un producto de la base de datos."""
    conn = get_db_connection()
    cursor = conn.cursor()
    # Gracias a "ON DELETE CASCADE", esto también eliminará las entradas de BOM asociadas.
    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()

def get_product_by_id(product_id):
    """Obtiene un solo producto por su ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, sku, name, product_type, stock, min_stock, cost, supplier, purchase_date, exit_date, weight, stock_unit_type, additional_cost FROM products WHERE id = ?", (product_id,))
    product = dict(cursor.fetchone())
    # Calcular peso total
    if product['stock_unit_type'] == 'grams':
        product['total_weight'] = product['stock']  # Ya está en gramos
    else:
        product['total_weight'] = product['stock'] * (product['weight'] or 0)  # unidades * gramaje
    # Asegurar que additional_cost existe
    if 'additional_cost' not in product or product['additional_cost'] is None:
        product['additional_cost'] = 0
    conn.close()
    return product

def get_all_products():
    """Obtiene todos los productos del inventario (con costo, proveedor, fechas, SKU, gramaje, tipo de unidad de stock y costo adicional)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, sku, name, product_type, stock, min_stock, cost, supplier, purchase_date, exit_date, weight, stock_unit_type, additional_cost FROM products ORDER BY name ASC")
    products = [dict(row) for row in cursor.fetchall()]
    # Calcular peso total para cada producto
    for product in products:
        if product['stock_unit_type'] == 'grams':
            product['total_weight'] = product['stock']  # Ya está en gramos
        else:
            product['total_weight'] = product['stock'] * (product['weight'] or 0)  # unidades * gramaje
        # Asegurar que additional_cost existe
        if 'additional_cost' not in product or product['additional_cost'] is None:
            product['additional_cost'] = 0
    conn.close()
    return products

def get_products_by_type(product_type):
    """Obtiene productos filtrados por tipo (ej: 'final', 'hijo')."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM products WHERE product_type = ? ORDER BY name ASC", (product_type,))
    products = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return products

# --- Funciones de BOM (Bill of Materials) ---

def add_bom_entry(parent_product_id, child_product_id, quantity):
    """Añade un insumo (hijo) a una lista de materiales (padre)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO bill_of_materials (parent_product_id, child_product_id, quantity) VALUES (?, ?, ?)",
        (parent_product_id, child_product_id, quantity)
    )
    conn.commit()
    conn.close()

def get_bom_for_product(parent_product_id):
    """
    Obtiene la lista de materiales (BOM) para un producto padre/final.
    Utiliza un JOIN para obtener los nombres de los productos hijos.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
    SELECT 
        bom.id as bom_id, 
        p.id as child_product_id,
        p.name as child_product_name, 
        bom.quantity
    FROM bill_of_materials AS bom
    JOIN products AS p ON bom.child_product_id = p.id
    WHERE bom.parent_product_id = ?
    """
    cursor.execute(query, (parent_product_id,))
    bom_items = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return bom_items

def calculate_bom_cost(product_id):
    """
    Calcula el costo unitario de un producto basándose en su BOM (Bill of Materials).
    Retorna el costo calculado, el desglose por componente y el costo adicional.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Obtener el producto padre
    cursor.execute("SELECT id, name, cost, additional_cost FROM products WHERE id = ?", (product_id,))
    parent = cursor.fetchone()
    if not parent:
        conn.close()
        return None
    
    parent = dict(parent)
    additional_cost = parent.get('additional_cost', 0) or 0
    
    # Obtener todos los componentes del BOM con sus costos
    cursor.execute("""
        SELECT 
            bom.id as bom_id,
            bom.quantity as required_quantity,
            p.id as child_id,
            p.name as child_name,
            p.cost as child_cost,
            p.stock_unit_type as child_stock_unit_type,
            p.weight as child_weight
        FROM bill_of_materials bom
        JOIN products p ON bom.child_product_id = p.id
        WHERE bom.parent_product_id = ?
    """, (product_id,))
    
    components = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    if not components:
        return {
            'product_id': product_id,
            'product_name': parent['name'],
            'calculated_cost': additional_cost,
            'materials_cost': 0,
            'additional_cost': additional_cost,
            'components': [],
            'message': 'Este producto no tiene componentes definidos en el BOM. Solo costo adicional aplicado.'
        }
    
    # Calcular el costo total de materiales
    total_materials_cost = 0
    component_breakdown = []
    
    for comp in components:
        child_cost = comp['child_cost'] or 0
        required_qty = comp['required_quantity']
        child_unit_type = comp['child_stock_unit_type'] or 'units'
        child_weight = comp['child_weight'] or 0
        
        # Calcular costo del componente
        # Si el componente se mide en unidades, el costo es directo
        # Si se mide en gramos, necesitamos considerar el costo por gramo
        if child_unit_type == 'units':
            component_cost = child_cost * required_qty
        else:  # grams
            # Si el costo está por unidad pero el stock está en gramos, necesitamos convertir
            # Asumimos que el costo está por unidad, así que calculamos costo por gramo
            if child_weight > 0:
                cost_per_gram = child_cost / child_weight
                component_cost = cost_per_gram * required_qty
            else:
                # Si no hay peso definido, asumimos que el costo ya está por gramo
                component_cost = child_cost * required_qty
        
        total_materials_cost += component_cost
        
        component_breakdown.append({
            'component_name': comp['child_name'],
            'required_quantity': required_qty,
            'unit_type': child_unit_type,
            'unit_cost': child_cost,
            'total_cost': component_cost
        })
    
    # Costo total = costo de materiales + costo adicional
    calculated_cost = total_materials_cost + additional_cost
    
    return {
        'product_id': product_id,
        'product_name': parent['name'],
        'calculated_cost': calculated_cost,
        'materials_cost': total_materials_cost,
        'additional_cost': additional_cost,
        'components': component_breakdown,
        'current_cost': parent.get('cost', 0),
        'message': f'Costo calculado: ${calculated_cost:.2f} (Materiales: ${total_materials_cost:.2f} + Adicional: ${additional_cost:.2f})'
    }

def delete_bom_entry(bom_id):
    """Elimina una entrada de la lista de materiales por su ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM bill_of_materials WHERE id = ?", (bom_id,))
    conn.commit()
    conn.close()

def calculate_mrp_production(product_id):
    """
    Calcula cuántos productos se pueden fabricar basándose en el BOM y el inventario actual.
    Maneja conversiones entre unidades discretas y continuas (gramos).
    Retorna un diccionario con la información del cálculo.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Obtener el producto padre con su tipo de unidad
    cursor.execute("SELECT id, name, stock, stock_unit_type FROM products WHERE id = ?", (product_id,))
    parent = cursor.fetchone()
    if not parent:
        conn.close()
        return None
    
    parent = dict(parent)
    
    # Obtener todos los componentes (hijos) del BOM con información de unidades
    cursor.execute("""
        SELECT 
            bom.id as bom_id,
            bom.quantity as required_quantity,
            p.id as child_id,
            p.name as child_name,
            p.stock as child_stock,
            p.stock_unit_type as child_stock_unit_type,
            p.weight as child_weight,
            p.sku as child_sku
        FROM bill_of_materials bom
        JOIN products p ON bom.child_product_id = p.id
        WHERE bom.parent_product_id = ?
    """, (product_id,))
    
    components = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    if not components:
        return {
            'product_id': product_id,
            'product_name': parent['name'],
            'can_produce': parent['stock'],
            'components': [],
            'message': 'Este producto no tiene componentes definidos en el BOM. Stock actual disponible.'
        }
    
    # Calcular cuántos se pueden producir basándose en el componente más limitante
    # Considerando conversiones entre unidades y gramos
    max_production = None
    limiting_component = None
    
    for comp in components:
        child_stock = comp['child_stock']
        child_unit_type = comp['child_stock_unit_type'] or 'units'
        child_weight = comp['child_weight'] or 0
        required_qty = comp['required_quantity']
        
        # Convertir el stock disponible a gramos si es necesario
        # El required_quantity siempre se interpreta en la misma unidad que el child_stock_unit_type
        # Si el padre requiere en unidades y el hijo está en gramos, necesitamos convertir
        
        # Caso 1: Ambos en unidades - cálculo directo
        if child_unit_type == 'units':
            available_units = child_stock
            possible_production = available_units / required_qty if required_qty > 0 else 0
        # Caso 2: Hijo en gramos, requerimiento en gramos - cálculo directo
        elif child_unit_type == 'grams':
            available_grams = child_stock
            # Si required_quantity está en gramos, cálculo directo
            possible_production = available_grams / required_qty if required_qty > 0 else 0
        else:
            # Fallback
            possible_production = child_stock / required_qty if required_qty > 0 else 0
        
        # Agregar información de conversión al componente
        comp['available_in_grams'] = child_stock if child_unit_type == 'grams' else (child_stock * child_weight)
        comp['required_in_grams'] = required_qty if child_unit_type == 'grams' else (required_qty * child_weight)
        comp['conversion_note'] = f"Stock: {child_stock} {child_unit_type}, Requerido: {required_qty} {child_unit_type}"
        
        if max_production is None or possible_production < max_production:
            max_production = possible_production
            limiting_component = comp
    
    # Redondear hacia abajo (no se pueden producir fracciones de unidades discretas)
    # Pero permitir decimales si el producto padre se mide en gramos
    if parent.get('stock_unit_type') == 'grams':
        max_production = max_production if max_production else 0
    else:
        max_production = int(max_production) if max_production else 0
    
    return {
        'product_id': product_id,
        'product_name': parent['name'],
        'current_stock': parent['stock'],
        'can_produce': max_production,
        'components': components,
        'limiting_component': limiting_component,
        'message': f'Puedes producir {max_production} {"unidades" if parent.get("stock_unit_type") != "grams" else "gramos"} de {parent["name"]} con el inventario actual.'
    }

def execute_production(product_id, quantity):
    """
    Ejecuta la producción de un producto: reduce el stock de los insumos y aumenta el stock del producto final.
    Retorna un diccionario con success y message.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Obtener el nombre del producto
        cursor.execute("SELECT name FROM products WHERE id = ?", (product_id,))
        product_row = cursor.fetchone()
        if not product_row:
            conn.close()
            return {'success': False, 'message': 'Producto no encontrado.'}
        product_name = product_row['name']
        
        # Verificar que se pueden producir la cantidad solicitada
        mrp_result = calculate_mrp_production(product_id)
        if not mrp_result or mrp_result['can_produce'] < quantity:
            conn.close()
            return {'success': False, 'message': f'No hay suficientes insumos. Solo se pueden producir {mrp_result["can_produce"] if mrp_result else 0} unidades.'}
        
        # Obtener los componentes del BOM
        cursor.execute("""
            SELECT 
                bom.child_product_id,
                bom.quantity as required_quantity
            FROM bill_of_materials bom
            WHERE bom.parent_product_id = ?
        """, (product_id,))
        
        components = [dict(row) for row in cursor.fetchall()]
        
        if not components:
            conn.close()
            return {'success': False, 'message': 'Este producto no tiene componentes definidos en el BOM.'}
        
        # Reducir stock de cada insumo
        for comp in components:
            child_id = comp['child_product_id']
            required_qty = comp['required_quantity'] * quantity
            cursor.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (required_qty, child_id))
        
        # Aumentar stock del producto final
        cursor.execute("UPDATE products SET stock = stock + ? WHERE id = ?", (quantity, product_id))
        
        conn.commit()
        conn.close()
        return {'success': True, 'message': f'Producción ejecutada: {quantity} unidades de {product_name} producidas.'}
    except Exception as e:
        conn.rollback()
        conn.close()
        return {'success': False, 'message': f'Error al ejecutar producción: {str(e)}'}

# --- Funciones de Finanzas ---

def add_revenue(description, amount, date=None):
    """Añade un registro de ingreso."""
    conn = get_db_connection()
    cursor = conn.cursor()
    if date:
        cursor.execute("INSERT INTO revenue (description, amount, date) VALUES (?, ?, ?)", (description, amount, date))
    else:
        cursor.execute("INSERT INTO revenue (description, amount) VALUES (?, ?)", (description, amount))
    conn.commit()
    conn.close()

def add_cost(description, amount, date=None, category='Otros'):
    """Añade un registro de costo."""
    conn = get_db_connection()
    cursor = conn.cursor()
    if date:
        cursor.execute("INSERT INTO costs (description, amount, category, date) VALUES (?, ?, ?, ?)", (description, amount, category, date))
    else:
        cursor.execute("INSERT INTO costs (description, amount, category) VALUES (?, ?, ?)", (description, amount, category))
    conn.commit()
    conn.close()

def get_recent_revenue(limit=10):
    """Obtiene las entradas de ingresos más recientes."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, description, amount, date FROM revenue ORDER BY date DESC LIMIT ?", (limit,))
    revenue_entries = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return revenue_entries

def get_all_revenue():
    """Obtiene todas las entradas de ingresos."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, description, amount, date FROM revenue ORDER BY date DESC")
    revenue_entries = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return revenue_entries

def get_recent_costs(limit=10):
    """Obtiene las entradas de costos más recientes."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, description, amount, category, date FROM costs ORDER BY date DESC LIMIT ?", (limit,))
    cost_entries = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return cost_entries

def get_all_costs():
    """Obtiene todas las entradas de costos."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, description, amount, category, date FROM costs ORDER BY date DESC")
    cost_entries = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return cost_entries

def update_revenue(revenue_id, description, amount, date=None):
    """Actualiza un registro de ingreso."""
    conn = get_db_connection()
    cursor = conn.cursor()
    if date:
        cursor.execute("UPDATE revenue SET description = ?, amount = ?, date = ? WHERE id = ?", (description, amount, date, revenue_id))
    else:
        cursor.execute("UPDATE revenue SET description = ?, amount = ? WHERE id = ?", (description, amount, revenue_id))
    conn.commit()
    conn.close()

def update_cost(cost_id, description, amount, date=None, category='Otros'):
    """Actualiza un registro de costo."""
    conn = get_db_connection()
    cursor = conn.cursor()
    if date:
        cursor.execute("UPDATE costs SET description = ?, amount = ?, category = ?, date = ? WHERE id = ?", (description, amount, category, date, cost_id))
    else:
        cursor.execute("UPDATE costs SET description = ?, amount = ?, category = ? WHERE id = ?", (description, amount, category, cost_id))
    conn.commit()
    conn.close()

def delete_revenue(revenue_id):
    """Elimina un registro de ingreso."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM revenue WHERE id = ?", (revenue_id,))
    conn.commit()
    conn.close()

def delete_cost(cost_id):
    """Elimina un registro de costo."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM costs WHERE id = ?", (cost_id,))
    conn.commit()
    conn.close()

def get_financial_summary(period='month'):
    """
    Obtiene un resumen de ingresos, costos y utilidades por período.
    period puede ser: 'day', 'week', 'month', 'year'
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Determinar formato de fecha según el período
    date_format_map = {
        'day': '%Y-%m-%d',
        'week': '%Y-W%W',
        'month': '%Y-%m',
        'year': '%Y'
    }
    date_format = date_format_map.get(period, '%Y-%m')
    
    # Query de ingresos
    cursor.execute(f"SELECT strftime('{date_format}', date) as period, SUM(amount) as total FROM revenue GROUP BY period ORDER BY period")
    revenue_data = {row['period']: row['total'] for row in cursor.fetchall()}
    
    # Query de costos
    cursor.execute(f"SELECT strftime('{date_format}', date) as period, SUM(amount) as total FROM costs GROUP BY period ORDER BY period")
    costs_data = {row['period']: row['total'] for row in cursor.fetchall()}

    conn.close()
    
    # Combinar datos
    all_periods = sorted(list(set(revenue_data.keys()) | set(costs_data.keys())))
    
    # Devolver estructura vacía si no hay datos
    if not all_periods:
        return {'labels': [], 'revenue': [], 'costs': [], 'profit': []}

    labels = list(all_periods)
    revenue = [revenue_data.get(period, 0) for period in all_periods]
    costs = [costs_data.get(period, 0) for period in all_periods]
    profit = [revenue[i] - costs[i] for i in range(len(labels))]  # Calcular utilidades

    return {'labels': labels, 'revenue': revenue, 'costs': costs, 'profit': profit}

# --- Funciones de Ventas ---

def add_sale(product_id, product_name, quantity, unit_price, date=None):
    """Añade una venta al historial."""
    conn = get_db_connection()
    cursor = conn.cursor()
    total_amount = float(quantity) * float(unit_price)
    
    # Actualizar stock del producto
    cursor.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (quantity, product_id))
    
    # Registrar la venta
    if date:
        cursor.execute("INSERT INTO sales (product_id, product_name, quantity, unit_price, total_amount, date) VALUES (?, ?, ?, ?, ?, ?)",
                      (product_id, product_name, quantity, unit_price, total_amount, date))
    else:
        cursor.execute("INSERT INTO sales (product_id, product_name, quantity, unit_price, total_amount) VALUES (?, ?, ?, ?, ?)",
                      (product_id, product_name, quantity, unit_price, total_amount))
    
    # Registrar también en revenue
    if date:
        cursor.execute("INSERT INTO revenue (description, amount, date) VALUES (?, ?, ?)",
                      (f"Venta: {product_name} x{quantity}", total_amount, date))
    else:
        cursor.execute("INSERT INTO revenue (description, amount) VALUES (?, ?)",
                      (f"Venta: {product_name} x{quantity}", total_amount))
    
    conn.commit()
    conn.close()

def add_multiple_sales(sales_list):
    """
    Añade múltiples ventas al historial.
    sales_list es una lista de diccionarios con: product_id, product_name, quantity, unit_price, date (opcional)
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        total_revenue = 0
        for sale in sales_list:
            product_id = sale['product_id']
            product_name = sale['product_name']
            quantity = float(sale['quantity'])
            unit_price = float(sale['unit_price'])
            date = sale.get('date', None)
            total_amount = quantity * unit_price
            total_revenue += total_amount
            
            # Actualizar stock del producto
            cursor.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (quantity, product_id))
            
            # Registrar la venta
            if date:
                cursor.execute("INSERT INTO sales (product_id, product_name, quantity, unit_price, total_amount, date) VALUES (?, ?, ?, ?, ?, ?)",
                              (product_id, product_name, quantity, unit_price, total_amount, date))
            else:
                cursor.execute("INSERT INTO sales (product_id, product_name, quantity, unit_price, total_amount) VALUES (?, ?, ?, ?, ?)",
                              (product_id, product_name, quantity, unit_price, total_amount))
            
            # Registrar también en revenue
            if date:
                cursor.execute("INSERT INTO revenue (description, amount, date) VALUES (?, ?, ?)",
                              (f"Venta: {product_name} x{quantity}", total_amount, date))
            else:
                cursor.execute("INSERT INTO revenue (description, amount) VALUES (?, ?)",
                              (f"Venta: {product_name} x{quantity}", total_amount))
        
        conn.commit()
        conn.close()
        return {'success': True, 'message': f'{len(sales_list)} ventas registradas correctamente. Total: ${total_revenue:.2f}'}
    except Exception as e:
        conn.rollback()
        conn.close()
        return {'success': False, 'message': f'Error al registrar ventas: {str(e)}'}

def get_all_sales():
    """Obtiene todas las ventas."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, product_id, product_name, quantity, unit_price, total_amount, date FROM sales ORDER BY date DESC")
    sales = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return sales

def get_recent_sales(limit=10):
    """Obtiene las ventas más recientes."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, product_id, product_name, quantity, unit_price, total_amount, date FROM sales ORDER BY date DESC LIMIT ?", (limit,))
    sales = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return sales

def get_sale_by_id(sale_id):
    """Obtiene una venta por su ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, product_id, product_name, quantity, unit_price, total_amount, date FROM sales WHERE id = ?", (sale_id,))
    sale = cursor.fetchone()
    conn.close()
    if sale:
        return dict(sale)
    return None

def update_sale(sale_id, product_id, product_name, quantity, unit_price, date=None):
    """Actualiza una venta existente."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Obtener la venta original
    original_sale = get_sale_by_id(sale_id)
    if not original_sale:
        conn.close()
        raise ValueError("Venta no encontrada")
    
    # Calcular nuevo total
    new_total = float(quantity) * float(unit_price)
    
    # Ajustar stock: restaurar el original y aplicar el nuevo
    quantity_diff = float(quantity) - original_sale['quantity']
    cursor.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (quantity_diff, product_id))
    
    # Actualizar la venta
    if date:
        cursor.execute("""
            UPDATE sales 
            SET product_id = ?, product_name = ?, quantity = ?, unit_price = ?, total_amount = ?, date = ?
            WHERE id = ?
        """, (product_id, product_name, quantity, unit_price, new_total, date, sale_id))
    else:
        cursor.execute("""
            UPDATE sales 
            SET product_id = ?, product_name = ?, quantity = ?, unit_price = ?, total_amount = ?
            WHERE id = ?
        """, (product_id, product_name, quantity, unit_price, new_total, sale_id))
    
    # Actualizar el ingreso asociado (buscar por descripción similar y fecha)
    revenue_description = f"Venta: {product_name} x{quantity}"
    cursor.execute("""
        UPDATE revenue 
        SET description = ?, amount = ?
        WHERE description LIKE ? AND date = (
            SELECT date FROM sales WHERE id = ?
        )
        LIMIT 1
    """, (revenue_description, new_total, f"Venta: {original_sale['product_name']} x%", sale_id))
    
    conn.commit()
    conn.close()

def delete_sale(sale_id):
    """Elimina una venta y su ingreso asociado."""
    conn = get_db_connection()
    cursor = conn.cursor()
    # Obtener datos de la venta antes de eliminar
    cursor.execute("SELECT product_id, quantity, total_amount, product_name, date FROM sales WHERE id = ?", (sale_id,))
    sale = cursor.fetchone()
    if sale:
        # Restaurar stock
        cursor.execute("UPDATE products SET stock = stock + ? WHERE id = ?", (sale['quantity'], sale['product_id']))
        # Eliminar el ingreso asociado (buscar por descripción similar y fecha)
        cursor.execute("""
            DELETE FROM revenue 
            WHERE description LIKE ? 
            AND amount = ?
            AND date = ?
        """, (f"Venta: {sale['product_name']} x%", sale['total_amount'], sale['date']))
    cursor.execute("DELETE FROM sales WHERE id = ?", (sale_id,))
    conn.commit()
    conn.close()

def get_sales_by_period(period='month'):
    """
    Obtiene ventas filtradas por período.
    period puede ser: 'day', 'week', 'month', 'year'
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if period == 'day':
        cursor.execute("""
            SELECT id, product_id, product_name, quantity, unit_price, total_amount, date
            FROM sales
            WHERE strftime('%Y-%m-%d', date) = strftime('%Y-%m-%d', 'now')
            ORDER BY date DESC
        """)
    elif period == 'week':
        cursor.execute("""
            SELECT id, product_id, product_name, quantity, unit_price, total_amount, date
            FROM sales
            WHERE strftime('%Y-W%W', date) = strftime('%Y-W%W', 'now')
            ORDER BY date DESC
        """)
    elif period == 'month':
        cursor.execute("""
            SELECT id, product_id, product_name, quantity, unit_price, total_amount, date
            FROM sales
            WHERE strftime('%Y-%m', date) = strftime('%Y-%m', 'now')
            ORDER BY date DESC
        """)
    elif period == 'year':
        cursor.execute("""
            SELECT id, product_id, product_name, quantity, unit_price, total_amount, date
            FROM sales
            WHERE strftime('%Y', date) = strftime('%Y', 'now')
            ORDER BY date DESC
        """)
    else:
        cursor.execute("SELECT id, product_id, product_name, quantity, unit_price, total_amount, date FROM sales ORDER BY date DESC")
    
    sales = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return sales

# --- Funciones de Business Intelligence ---

def get_top_products_by_sales(limit=5):
    """Obtiene los top productos más vendidos por cantidad."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT product_name, SUM(quantity) as total_quantity, SUM(total_amount) as total_revenue
        FROM sales
        GROUP BY product_name
        ORDER BY total_quantity DESC
        LIMIT ?
    """, (limit,))
    products = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return products

def get_top_products_by_profitability(limit=5):
    """Obtiene los top productos más rentables (margen * cantidad vendida)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            s.product_name,
            s.product_id,
            SUM(s.quantity) as total_quantity,
            SUM(s.total_amount) as total_revenue,
            p.cost as unit_cost,
            SUM((s.unit_price - COALESCE(p.cost, 0)) * s.quantity) as total_profit
        FROM sales s
        LEFT JOIN products p ON s.product_id = p.id
        GROUP BY s.product_name, s.product_id, p.cost
        ORDER BY total_profit DESC
        LIMIT ?
    """, (limit,))
    products = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return products

def get_cost_breakdown_by_category():
    """Obtiene el desglose de costos por categoría."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT category, SUM(amount) as total
        FROM costs
        GROUP BY category
        ORDER BY total DESC
    """)
    breakdown = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return breakdown

def get_products_without_movement(days=30):
    """Obtiene productos sin movimiento en los últimos N días."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.id, p.name, p.product_type, p.stock, p.cost, p.stock * p.cost as total_value
        FROM products p
        WHERE p.id NOT IN (
            SELECT DISTINCT product_id 
            FROM sales 
            WHERE date >= datetime('now', '-' || ? || ' days')
        )
        AND p.product_type IN ('final', 'padre')
        ORDER BY p.name
    """, (days,))
    products = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return products

def get_inventory_valuation_by_category():
    """Obtiene la valorización del inventario por categoría (product_type)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            product_type, 
            COUNT(*) as product_count,
            SUM(stock * cost) as total_value,
            SUM(stock) as total_quantity
        FROM products
        GROUP BY product_type
        ORDER BY total_value DESC
    """)
    valuation = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return valuation

def get_financial_metrics_current_month():
    """Obtiene métricas financieras del mes actual."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Ventas del mes
    cursor.execute("""
        SELECT 
            COUNT(*) as sales_count,
            SUM(total_amount) as total_sales,
            AVG(total_amount) as avg_ticket
        FROM sales
        WHERE strftime('%Y-%m', date) = strftime('%Y-%m', 'now')
    """)
    sales_metrics = dict(cursor.fetchone() or {})
    
    # Ingresos del mes
    cursor.execute("""
        SELECT SUM(amount) as total_revenue
        FROM revenue
        WHERE strftime('%Y-%m', date) = strftime('%Y-%m', 'now')
    """)
    revenue_result = cursor.fetchone()
    total_revenue = revenue_result['total_revenue'] if revenue_result and revenue_result['total_revenue'] else 0
    
    # Costos del mes
    cursor.execute("""
        SELECT SUM(amount) as total_costs
        FROM costs
        WHERE strftime('%Y-%m', date) = strftime('%Y-%m', 'now')
    """)
    costs_result = cursor.fetchone()
    total_costs = costs_result['total_costs'] if costs_result and costs_result['total_costs'] else 0
    
    # Calcular margen de ganancia
    profit = total_revenue - total_costs
    profit_margin = (profit / total_revenue * 100) if total_revenue > 0 else 0
    
    conn.close()
    
    return {
        'sales_count': sales_metrics.get('sales_count', 0) or 0,
        'total_sales': sales_metrics.get('total_sales', 0) or 0,
        'avg_ticket': sales_metrics.get('avg_ticket', 0) or 0,
        'total_revenue': total_revenue,
        'total_costs': total_costs,
        'profit': profit,
        'profit_margin': round(profit_margin, 2)
    }