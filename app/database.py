import sqlite3
import os
import sys

"""
This module handles all interaction with the local SQLite database.
(Extended version with Product Costs and stock adjustment)
"""

def get_db_path():
    """
    Gets the correct path for the database file.
    On macOS when running from .app bundle, uses the user's directory.
    """
    if getattr(sys, 'frozen', False):
        # Running from a compiled executable
        if sys.platform == 'darwin' and '.app' in sys.executable:
            # macOS: use user's Documents directory
            db_dir = os.path.join(os.path.expanduser('~'), 'Documents', 'OpenERP')
            os.makedirs(db_dir, exist_ok=True)
            return os.path.join(db_dir, 'erp_data.db')
        else:
            # Windows/Linux: use executable directory
            if hasattr(sys, '_MEIPASS'):
                # PyInstaller: use executable directory, not _MEIPASS
                base_path = os.path.dirname(sys.executable)
            else:
                base_path = os.path.dirname(os.path.abspath(sys.executable))
            return os.path.join(base_path, 'erp_data.db')
    else:
        # Running from source code: use project directory
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, 'erp_data.db')

DB_FILE = get_db_path()

def get_db_connection():
    """Connects to the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row # Allows accessing results by column name
    return conn

def init_db():
    """
    Initializes the database.
    Creates tables if they don't exist.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # --- Products Table (Inventory) ---
    # product_type: 'final' (to sell), 'hijo' (component), 'padre' (sub-assembly), 'otro' (expenses)
    # NEW! Added 'cost' field, supplier, purchase_date, exit_date, SKU
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sku TEXT UNIQUE, -- Product SKU/ID code
        name TEXT NOT NULL UNIQUE,
        product_type TEXT NOT NULL CHECK(product_type IN ('final', 'hijo', 'padre', 'otro')),
        stock REAL NOT NULL DEFAULT 0,
        min_stock REAL NOT NULL DEFAULT 0,
        cost REAL NOT NULL DEFAULT 0, -- Product unit cost
        supplier TEXT, -- Supplier
        purchase_date DATE, -- Purchase date
        exit_date DATE, -- Exit date
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    ''')
    
    # Migration: Add new columns if they don't exist (for existing databases)
    try:
        cursor.execute('ALTER TABLE products ADD COLUMN cost REAL NOT NULL DEFAULT 0')
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    try:
        cursor.execute('ALTER TABLE products ADD COLUMN supplier TEXT')
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    try:
        cursor.execute('ALTER TABLE products ADD COLUMN purchase_date DATE')
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    try:
        cursor.execute('ALTER TABLE products ADD COLUMN exit_date DATE')
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    try:
        cursor.execute('ALTER TABLE products ADD COLUMN sku TEXT')
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    try:
        cursor.execute('ALTER TABLE products ADD COLUMN weight REAL DEFAULT 0')
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    try:
        cursor.execute('ALTER TABLE products ADD COLUMN stock_unit_type TEXT DEFAULT "units"')
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    # Ensure stock_unit_type has valid values
    try:
        cursor.execute('UPDATE products SET stock_unit_type = "units" WHERE stock_unit_type IS NULL OR stock_unit_type NOT IN ("units", "grams")')
    except sqlite3.OperationalError:
        pass
    
    try:
        cursor.execute('ALTER TABLE products ADD COLUMN additional_cost REAL DEFAULT 0')
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    conn.commit()

    # --- BOM (Bill of Materials) Table ---
    # Defines which 'hijos' (children) compose a 'padre' (parent) or 'final'.
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS bill_of_materials (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        parent_product_id INTEGER NOT NULL, -- ID of 'final' or 'padre' product
        child_product_id INTEGER NOT NULL,  -- ID of 'hijo' product
        quantity REAL NOT NULL DEFAULT 1,   -- How many 'hijos' are needed
        FOREIGN KEY (parent_product_id) REFERENCES products(id) ON DELETE CASCADE,
        FOREIGN KEY (child_product_id) REFERENCES products(id) ON DELETE CASCADE
    );
    ''')
    
    # --- Finance Tables ---
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
        category TEXT DEFAULT 'Others',
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    ''')
    
    # --- Sales Table (Sales History) ---
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
    
    # Migration: Add category column to costs if it doesn't exist
    try:
        cursor.execute('ALTER TABLE costs ADD COLUMN category TEXT DEFAULT "Others"')
    except sqlite3.OperationalError:
        pass  # Column already exists

    conn.commit()
    conn.close()

# --- Product CRUD Functions ---

def add_product(name, product_type, stock, min_stock, cost, supplier=None, purchase_date=None, exit_date=None, sku=None, weight=0, stock_unit_type='units', additional_cost=0):
    """Adds a new product to inventory (with cost, supplier, dates, SKU, weight, stock unit type and additional cost)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    # Validate stock_unit_type
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
    NEW! Adjusts a product's stock.
    Uses a relative change (e.g.: +5 or -3).
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
    """Updates an existing product in the database (with cost, supplier, dates, SKU, weight, stock unit type and additional cost)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    # Validate stock_unit_type
    if stock_unit_type not in ('units', 'grams'):
        stock_unit_type = 'units'
    cursor.execute(
        "UPDATE products SET name = ?, product_type = ?, stock = ?, min_stock = ?, cost = ?, supplier = ?, purchase_date = ?, exit_date = ?, sku = ?, weight = ?, stock_unit_type = ?, additional_cost = ? WHERE id = ?",
        (name, product_type, stock, min_stock, cost, supplier, purchase_date, exit_date, sku, weight, stock_unit_type, additional_cost, product_id)
    )
    conn.commit()
    conn.close()

def delete_product(product_id):
    """Deletes a product from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    # Thanks to "ON DELETE CASCADE", this will also delete associated BOM entries.
    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()

def get_product_by_id(product_id):
    """Gets a single product by its ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, sku, name, product_type, stock, min_stock, cost, supplier, purchase_date, exit_date, weight, stock_unit_type, additional_cost FROM products WHERE id = ?", (product_id,))
    product = dict(cursor.fetchone())
    # Calculate total weight
    if product['stock_unit_type'] == 'grams':
        product['total_weight'] = product['stock']  # Already in grams
    else:
        product['total_weight'] = product['stock'] * (product['weight'] or 0)  # units * weight
    # Ensure additional_cost exists
    if 'additional_cost' not in product or product['additional_cost'] is None:
        product['additional_cost'] = 0
    conn.close()
    return product

def get_all_products():
    """Gets all products from inventory (with cost, supplier, dates, SKU, weight, stock unit type and additional cost)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, sku, name, product_type, stock, min_stock, cost, supplier, purchase_date, exit_date, weight, stock_unit_type, additional_cost FROM products ORDER BY name ASC")
    products = [dict(row) for row in cursor.fetchall()]
    # Calculate total weight for each product
    for product in products:
        if product['stock_unit_type'] == 'grams':
            product['total_weight'] = product['stock']  # Already in grams
        else:
            product['total_weight'] = product['stock'] * (product['weight'] or 0)  # units * weight
        # Ensure additional_cost exists
        if 'additional_cost' not in product or product['additional_cost'] is None:
            product['additional_cost'] = 0
    conn.close()
    return products

def get_products_by_type(product_type):
    """Gets products filtered by type (e.g.: 'final', 'hijo')."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM products WHERE product_type = ? ORDER BY name ASC", (product_type,))
    products = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return products

# --- BOM (Bill of Materials) Functions ---

def add_bom_entry(parent_product_id, child_product_id, quantity):
    """Adds a component (child) to a bill of materials (parent)."""
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
    Gets the bill of materials (BOM) for a parent/final product.
    Uses a JOIN to get child product names.
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
    Calculates the unit cost of a product based on its BOM (Bill of Materials).
    Returns the calculated cost, breakdown by component and additional cost.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get the parent product
    cursor.execute("SELECT id, name, cost, additional_cost FROM products WHERE id = ?", (product_id,))
    parent = cursor.fetchone()
    if not parent:
        conn.close()
        return None
    
    parent = dict(parent)
    additional_cost = parent.get('additional_cost', 0) or 0
    
    # Get all BOM components with their costs
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
            'message': 'This product has no components defined in the BOM. Only additional cost applied.'
        }
    
    # Calculate total materials cost
    total_materials_cost = 0
    component_breakdown = []
    
    for comp in components:
        child_cost = comp['child_cost'] or 0
        required_qty = comp['required_quantity']
        child_unit_type = comp['child_stock_unit_type'] or 'units'
        child_weight = comp['child_weight'] or 0
        
        # Calculate component cost
        # If component is measured in units, cost is direct
        # If measured in grams, we need to consider cost per gram
        if child_unit_type == 'units':
            component_cost = child_cost * required_qty
        else:  # grams
            # If cost is per unit but stock is in grams, we need to convert
            # We assume cost is per unit, so we calculate cost per gram
            if child_weight > 0:
                cost_per_gram = child_cost / child_weight
                component_cost = cost_per_gram * required_qty
            else:
                # If no weight defined, we assume cost is already per gram
                component_cost = child_cost * required_qty
        
        total_materials_cost += component_cost
        
        component_breakdown.append({
            'component_name': comp['child_name'],
            'required_quantity': required_qty,
            'unit_type': child_unit_type,
            'unit_cost': child_cost,
            'total_cost': component_cost
        })
    
    # Total cost = materials cost + additional cost
    calculated_cost = total_materials_cost + additional_cost
    
    return {
        'product_id': product_id,
        'product_name': parent['name'],
        'calculated_cost': calculated_cost,
        'materials_cost': total_materials_cost,
        'additional_cost': additional_cost,
        'components': component_breakdown,
        'current_cost': parent.get('cost', 0),
        'message': f'Calculated cost: ${calculated_cost:.2f} (Materials: ${total_materials_cost:.2f} + Additional: ${additional_cost:.2f})'
    }

def delete_bom_entry(bom_id):
    """Deletes a bill of materials entry by its ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM bill_of_materials WHERE id = ?", (bom_id,))
    conn.commit()
    conn.close()

def calculate_mrp_production(product_id):
    """
    Calculates how many products can be manufactured based on BOM and current inventory.
    Handles conversions between discrete and continuous units (grams).
    Returns a dictionary with calculation information.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get the parent product with its unit type
    cursor.execute("SELECT id, name, stock, stock_unit_type FROM products WHERE id = ?", (product_id,))
    parent = cursor.fetchone()
    if not parent:
        conn.close()
        return None
    
    parent = dict(parent)
    
    # Get all BOM components (children) with unit information
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
            'message': 'This product has no components defined in the BOM. Current stock available.'
        }
    
    # Calculate how many can be produced based on the most limiting component
    # Considering conversions between units and grams
    max_production = None
    limiting_component = None
    
    for comp in components:
        child_stock = comp['child_stock']
        child_unit_type = comp['child_stock_unit_type'] or 'units'
        child_weight = comp['child_weight'] or 0
        required_qty = comp['required_quantity']
        
        # Convert available stock to grams if necessary
        # required_quantity is always interpreted in the same unit as child_stock_unit_type
        # If parent requires in units and child is in grams, we need to convert
        
        # Case 1: Both in units - direct calculation
        if child_unit_type == 'units':
            available_units = child_stock
            possible_production = available_units / required_qty if required_qty > 0 else 0
        # Case 2: Child in grams, requirement in grams - direct calculation
        elif child_unit_type == 'grams':
            available_grams = child_stock
            # If required_quantity is in grams, direct calculation
            possible_production = available_grams / required_qty if required_qty > 0 else 0
        else:
            # Fallback
            possible_production = child_stock / required_qty if required_qty > 0 else 0
        
        # Add conversion information to component
        comp['available_in_grams'] = child_stock if child_unit_type == 'grams' else (child_stock * child_weight)
        comp['required_in_grams'] = required_qty if child_unit_type == 'grams' else (required_qty * child_weight)
        comp['conversion_note'] = f"Stock: {child_stock} {child_unit_type}, Required: {required_qty} {child_unit_type}"
        
        if max_production is None or possible_production < max_production:
            max_production = possible_production
            limiting_component = comp
    
    # Round down (can't produce fractions of discrete units)
    # But allow decimals if parent product is measured in grams
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
        'message': f'You can produce {max_production} {"units" if parent.get("stock_unit_type") != "grams" else "grams"} of {parent["name"]} with current inventory.'
    }

def execute_production(product_id, quantity):
    """
    Executes production of a product: reduces component stock and increases final product stock.
    Returns a dictionary with success and message.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get product name
        cursor.execute("SELECT name FROM products WHERE id = ?", (product_id,))
        product_row = cursor.fetchone()
        if not product_row:
            conn.close()
            return {'success': False, 'message': 'Product not found.'}
        product_name = product_row['name']
        
        # Verify that the requested quantity can be produced
        mrp_result = calculate_mrp_production(product_id)
        if not mrp_result or mrp_result['can_produce'] < quantity:
            conn.close()
            return {'success': False, 'message': f'Not enough components. Only {mrp_result["can_produce"] if mrp_result else 0} units can be produced.'}
        
        # Get BOM components
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
            return {'success': False, 'message': 'This product has no components defined in the BOM.'}
        
        # Reduce stock of each component
        for comp in components:
            child_id = comp['child_product_id']
            required_qty = comp['required_quantity'] * quantity
            cursor.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (required_qty, child_id))
        
        # Increase final product stock
        cursor.execute("UPDATE products SET stock = stock + ? WHERE id = ?", (quantity, product_id))
        
        conn.commit()
        conn.close()
        return {'success': True, 'message': f'Production executed: {quantity} units of {product_name} produced.'}
    except Exception as e:
        conn.rollback()
        conn.close()
        return {'success': False, 'message': f'Error executing production: {str(e)}'}

# --- Finance Functions ---

def add_revenue(description, amount, date=None):
    """Adds a revenue entry."""
    conn = get_db_connection()
    cursor = conn.cursor()
    if date:
        cursor.execute("INSERT INTO revenue (description, amount, date) VALUES (?, ?, ?)", (description, amount, date))
    else:
        cursor.execute("INSERT INTO revenue (description, amount) VALUES (?, ?)", (description, amount))
    conn.commit()
    conn.close()

def add_cost(description, amount, date=None, category='Others'):
    """Adds a cost entry."""
    conn = get_db_connection()
    cursor = conn.cursor()
    if date:
        cursor.execute("INSERT INTO costs (description, amount, category, date) VALUES (?, ?, ?, ?)", (description, amount, category, date))
    else:
        cursor.execute("INSERT INTO costs (description, amount, category) VALUES (?, ?, ?)", (description, amount, category))
    conn.commit()
    conn.close()

def get_recent_revenue(limit=10):
    """Gets the most recent revenue entries."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, description, amount, date FROM revenue ORDER BY date DESC LIMIT ?", (limit,))
    revenue_entries = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return revenue_entries

def get_all_revenue():
    """Gets all revenue entries."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, description, amount, date FROM revenue ORDER BY date DESC")
    revenue_entries = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return revenue_entries

def get_recent_costs(limit=10):
    """Gets the most recent cost entries."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, description, amount, category, date FROM costs ORDER BY date DESC LIMIT ?", (limit,))
    cost_entries = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return cost_entries

def get_all_costs():
    """Gets all cost entries."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, description, amount, category, date FROM costs ORDER BY date DESC")
    cost_entries = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return cost_entries

def update_revenue(revenue_id, description, amount, date=None):
    """Updates a revenue entry."""
    conn = get_db_connection()
    cursor = conn.cursor()
    if date:
        cursor.execute("UPDATE revenue SET description = ?, amount = ?, date = ? WHERE id = ?", (description, amount, date, revenue_id))
    else:
        cursor.execute("UPDATE revenue SET description = ?, amount = ? WHERE id = ?", (description, amount, revenue_id))
    conn.commit()
    conn.close()

def update_cost(cost_id, description, amount, date=None, category='Others'):
    """Updates a cost entry."""
    conn = get_db_connection()
    cursor = conn.cursor()
    if date:
        cursor.execute("UPDATE costs SET description = ?, amount = ?, category = ?, date = ? WHERE id = ?", (description, amount, category, date, cost_id))
    else:
        cursor.execute("UPDATE costs SET description = ?, amount = ?, category = ? WHERE id = ?", (description, amount, category, cost_id))
    conn.commit()
    conn.close()

def delete_revenue(revenue_id):
    """Deletes a revenue entry."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM revenue WHERE id = ?", (revenue_id,))
    conn.commit()
    conn.close()

def delete_cost(cost_id):
    """Deletes a cost entry."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM costs WHERE id = ?", (cost_id,))
    conn.commit()
    conn.close()

def get_financial_summary(period='month'):
    """
    Gets a summary of revenue, costs and profits by period.
    period can be: 'day', 'week', 'month', 'year'
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Determine date format according to period
    date_format_map = {
        'day': '%Y-%m-%d',
        'week': '%Y-W%W',
        'month': '%Y-%m',
        'year': '%Y'
    }
    date_format = date_format_map.get(period, '%Y-%m')
    
    # Revenue query
    cursor.execute(f"SELECT strftime('{date_format}', date) as period, SUM(amount) as total FROM revenue GROUP BY period ORDER BY period")
    revenue_data = {row['period']: row['total'] for row in cursor.fetchall()}
    
    # Costs query
    cursor.execute(f"SELECT strftime('{date_format}', date) as period, SUM(amount) as total FROM costs GROUP BY period ORDER BY period")
    costs_data = {row['period']: row['total'] for row in cursor.fetchall()}

    conn.close()
    
    # Combine data
    all_periods = sorted(list(set(revenue_data.keys()) | set(costs_data.keys())))
    
    # Return empty structure if no data
    if not all_periods:
        return {'labels': [], 'revenue': [], 'costs': [], 'profit': []}

    labels = list(all_periods)
    revenue = [revenue_data.get(period, 0) for period in all_periods]
    costs = [costs_data.get(period, 0) for period in all_periods]
    profit = [revenue[i] - costs[i] for i in range(len(labels))]  # Calculate profits

    return {'labels': labels, 'revenue': revenue, 'costs': costs, 'profit': profit}

# --- Sales Functions ---

def add_sale(product_id, product_name, quantity, unit_price, date=None):
    """Adds a sale to the history."""
    conn = get_db_connection()
    cursor = conn.cursor()
    total_amount = float(quantity) * float(unit_price)
    
    # Update product stock
    cursor.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (quantity, product_id))
    
    # Register the sale
    if date:
        cursor.execute("INSERT INTO sales (product_id, product_name, quantity, unit_price, total_amount, date) VALUES (?, ?, ?, ?, ?, ?)",
                      (product_id, product_name, quantity, unit_price, total_amount, date))
    else:
        cursor.execute("INSERT INTO sales (product_id, product_name, quantity, unit_price, total_amount) VALUES (?, ?, ?, ?, ?)",
                      (product_id, product_name, quantity, unit_price, total_amount))
    
    # Also register in revenue
    if date:
        cursor.execute("INSERT INTO revenue (description, amount, date) VALUES (?, ?, ?)",
                      (f"Sale: {product_name} x{quantity}", total_amount, date))
    else:
        cursor.execute("INSERT INTO revenue (description, amount) VALUES (?, ?)",
                      (f"Sale: {product_name} x{quantity}", total_amount))
    
    conn.commit()
    conn.close()

def add_multiple_sales(sales_list):
    """
    Adds multiple sales to the history.
    sales_list is a list of dictionaries with: product_id, product_name, quantity, unit_price, date (optional)
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
            
            # Update product stock
            cursor.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (quantity, product_id))
            
            # Register the sale
            if date:
                cursor.execute("INSERT INTO sales (product_id, product_name, quantity, unit_price, total_amount, date) VALUES (?, ?, ?, ?, ?, ?)",
                              (product_id, product_name, quantity, unit_price, total_amount, date))
            else:
                cursor.execute("INSERT INTO sales (product_id, product_name, quantity, unit_price, total_amount) VALUES (?, ?, ?, ?, ?)",
                              (product_id, product_name, quantity, unit_price, total_amount))
            
            # Also register in revenue
            if date:
                cursor.execute("INSERT INTO revenue (description, amount, date) VALUES (?, ?, ?)",
                              (f"Sale: {product_name} x{quantity}", total_amount, date))
            else:
                cursor.execute("INSERT INTO revenue (description, amount) VALUES (?, ?)",
                              (f"Sale: {product_name} x{quantity}", total_amount))
        
        conn.commit()
        conn.close()
        return {'success': True, 'message': f'{len(sales_list)} sales registered successfully. Total: ${total_revenue:.2f}'}
    except Exception as e:
        conn.rollback()
        conn.close()
        return {'success': False, 'message': f'Error registering sales: {str(e)}'}

def get_all_sales():
    """Gets all sales."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, product_id, product_name, quantity, unit_price, total_amount, date FROM sales ORDER BY date DESC")
    sales = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return sales

def get_recent_sales(limit=10):
    """Gets the most recent sales."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, product_id, product_name, quantity, unit_price, total_amount, date FROM sales ORDER BY date DESC LIMIT ?", (limit,))
    sales = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return sales

def get_sale_by_id(sale_id):
    """Gets a sale by its ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, product_id, product_name, quantity, unit_price, total_amount, date FROM sales WHERE id = ?", (sale_id,))
    sale = cursor.fetchone()
    conn.close()
    if sale:
        return dict(sale)
    return None

def update_sale(sale_id, product_id, product_name, quantity, unit_price, date=None):
    """Updates an existing sale."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get original sale
    original_sale = get_sale_by_id(sale_id)
    if not original_sale:
        conn.close()
        raise ValueError("Sale not found")
    
    # Calculate new total
    new_total = float(quantity) * float(unit_price)
    
    # Adjust stock: restore original and apply new
    quantity_diff = float(quantity) - original_sale['quantity']
    cursor.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (quantity_diff, product_id))
    
    # Update the sale
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
    
    # Update associated revenue (search by similar description and date)
    revenue_description = f"Sale: {product_name} x{quantity}"
    cursor.execute("""
        UPDATE revenue 
        SET description = ?, amount = ?
        WHERE description LIKE ? AND date = (
            SELECT date FROM sales WHERE id = ?
        )
        LIMIT 1
    """, (revenue_description, new_total, f"Sale: {original_sale['product_name']} x%", sale_id))
    
    conn.commit()
    conn.close()

def delete_sale(sale_id):
    """Deletes a sale and its associated revenue."""
    conn = get_db_connection()
    cursor = conn.cursor()
    # Get sale data before deleting
    cursor.execute("SELECT product_id, quantity, total_amount, product_name, date FROM sales WHERE id = ?", (sale_id,))
    sale = cursor.fetchone()
    if sale:
        # Restore stock
        cursor.execute("UPDATE products SET stock = stock + ? WHERE id = ?", (sale['quantity'], sale['product_id']))
        # Delete associated revenue (search by similar description and date)
        cursor.execute("""
            DELETE FROM revenue 
            WHERE description LIKE ? 
            AND amount = ?
            AND date = ?
        """, (f"Sale: {sale['product_name']} x%", sale['total_amount'], sale['date']))
    cursor.execute("DELETE FROM sales WHERE id = ?", (sale_id,))
    conn.commit()
    conn.close()

def get_sales_by_period(period='month'):
    """
    Gets sales filtered by period.
    period can be: 'day', 'week', 'month', 'year'
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

# --- Business Intelligence Functions ---

def get_top_products_by_sales(limit=5):
    """Gets the top products by sales quantity."""
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
    """Gets the top products by profitability (margin * quantity sold)."""
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
    """Gets the cost breakdown by category."""
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
    """Gets products without movement in the last N days."""
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
    """Gets inventory valuation by category (product_type)."""
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
    """Gets financial metrics for the current month."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Sales for the month
    cursor.execute("""
        SELECT 
            COUNT(*) as sales_count,
            SUM(total_amount) as total_sales,
            AVG(total_amount) as avg_ticket
        FROM sales
        WHERE strftime('%Y-%m', date) = strftime('%Y-%m', 'now')
    """)
    sales_metrics = dict(cursor.fetchone() or {})
    
    # Revenue for the month
    cursor.execute("""
        SELECT SUM(amount) as total_revenue
        FROM revenue
        WHERE strftime('%Y-%m', date) = strftime('%Y-%m', 'now')
    """)
    revenue_result = cursor.fetchone()
    total_revenue = revenue_result['total_revenue'] if revenue_result and revenue_result['total_revenue'] else 0
    
    # Costs for the month
    cursor.execute("""
        SELECT SUM(amount) as total_costs
        FROM costs
        WHERE strftime('%Y-%m', date) = strftime('%Y-%m', 'now')
    """)
    costs_result = cursor.fetchone()
    total_costs = costs_result['total_costs'] if costs_result and costs_result['total_costs'] else 0
    
    # Calculate profit margin
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