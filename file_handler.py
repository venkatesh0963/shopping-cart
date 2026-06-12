"""
file_handler.py — File I/O operations for the Shopping Cart System
"""

import os
from datetime import datetime
from product import Product

# ── Paths ─────────────────────────────────────────────────────────────────────
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
PRODUCTS_FILE = os.path.join(DATA_DIR, "products.txt")
ORDERS_FILE   = os.path.join(DATA_DIR, "orders.txt")
ORDERS_CSV    = os.path.join(DATA_DIR, "orders.csv")
USERS_FILE    = os.path.join(DATA_DIR, "users.txt")


def _ensure_data_dir():
    """Create the data/ directory if it doesn't exist."""
    os.makedirs(DATA_DIR, exist_ok=True)


# ── Product File Operations ────────────────────────────────────────────────────

def load_products() -> dict:
    """
    Read products from products.txt and return a dict of {product_id: Product}.

    Returns:
        dict: {int product_id: Product object}

    Raises:
        FileNotFoundError: Handled internally; returns empty dict if file missing.
    """
    _ensure_data_dir()
    products = {}
    try:
        with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, start=1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue  # skip blanks and comments
                try:
                    parts = line.split("|")
                    if len(parts) != 4:
                        raise ValueError(f"Expected 4 fields, got {len(parts)}")
                    pid, name, price, stock = parts
                    p = Product(
                        product_id=int(pid),
                        name=name,
                        price=float(price),
                        stock=max(0, int(stock))   # guard: never load negative stock
                    )
                    products[p.product_id] = p
                except (ValueError, TypeError) as e:
                    print(f"  [Warning] Skipping malformed line {line_num}: {e}")
    except FileNotFoundError:
        print("  [Info] products.txt not found. Starting with empty catalog.")
    return products


def save_products(products: dict):
    """
    Write all products back to products.txt (overwrites existing file).

    Args:
        products (dict): {product_id: Product}
    """
    _ensure_data_dir()
    try:
        with open(PRODUCTS_FILE, "w", encoding="utf-8") as f:
            f.write("# Shopping Cart — Product Catalog\n")
            f.write("# Format: product_id|name|price|stock\n")
            for product in products.values():
                f.write(product.to_file_line() + "\n")
    except IOError as e:
        print(f"  [Error] Could not save products: {e}")


# ── User File Operations ───────────────────────────────────────────────────────

def load_users() -> dict:
    """
    Read user credentials from users.txt and return a dict of {username: {'password': pwd, 'role': role}}.

    Returns:
        dict: User dictionary. Default admin account is returned if file does not exist.
    """
    _ensure_data_dir()
    users = {}
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, start=1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split("|")
                if len(parts) == 3:
                    username, pwd, role = parts
                    users[username] = {'password': pwd, 'role': role}
    except FileNotFoundError:
        # Provide default fallback
        users = {'admin': {'password': 'admin', 'role': 'admin'}}

    return users

def save_users(users: dict):
    """
    Write user dictionary back to users.txt.

    Args:
        users (dict): {username: {'password': pwd, 'role': role}}
    """
    _ensure_data_dir()
    try:
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            f.write("# Shopping Cart — Users \n")
            f.write("# Format: username|password|role\n")
            for username, details in users.items():
                f.write(f"{username}|{details['password']}|{details['role']}\n")
    except IOError as e:
        print(f"  [Error] Could not save users: {e}")


# ── Order File Operations ──────────────────────────────────────────────────────

def save_order(order_items: list, grand_total: float,
               address: str = "", payment_method: str = "Cash on Delivery"):
    """
    Append the bill for a completed order to orders.txt AND orders.xlsx.

    Args:
        order_items (list): List of dicts with keys: name, qty, price, subtotal.
        grand_total (float): Total bill amount.
        address (str): Delivery address.
        payment_method (str): Payment method chosen by customer.
    """
    _ensure_data_dir()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    separator = "=" * 55
    thin_sep = "-" * 55

    bill_lines = [
        "",
        separator,
        "             🛒  MyShop — Order Receipt",
        f"  Date & Time : {now}",
        separator,
    ]

    if address:
        bill_lines.append(f"  Deliver To   : {address}")
    bill_lines.append(f"  Payment      : {payment_method}")
    bill_lines.append("  " + thin_sep)

    bill_lines += [
        f"  {'#':<4} {'Product':<22} {'Qty':>5} {'Price':>8} {'Subtotal':>9}",
        "  " + thin_sep,
    ]

    for idx, item in enumerate(order_items, start=1):
        bill_lines.append(
            f"  {idx:<4} {item['name']:<22} {item['qty']:>5} "
            f"Rs.{item['price']:>6,.2f}  Rs.{item['subtotal']:>7,.2f}"
        )

    bill_lines += [
        "  " + thin_sep,
        f"  {'Grand Total':<42} Rs.{grand_total:>7,.2f}",
        separator,
        "        Thank you for shopping at MyShop! 🙏",
        separator,
        "",
    ]

    try:
        with open(ORDERS_FILE, "a", encoding="utf-8") as f:
            f.write("\n".join(bill_lines) + "\n")
        print(f"  ✔ Order saved to  → {ORDERS_FILE}")
    except IOError as e:
        print(f"  [Error] Could not save order to txt: {e}")

    # Also save to CSV
    save_order_csv(order_items, grand_total, address, payment_method, now)


def print_bill(order_items: list, grand_total: float,
               address: str = "", payment_method: str = "Cash on Delivery"):
    """
    Print the formatted bill to the console.

    Args:
        order_items (list): List of dicts with order line details.
        grand_total (float): Total amount.
        address (str): Delivery address entered by the customer.
        payment_method (str): Payment method chosen by the customer.
    """
    now = datetime.now().strftime("%Y-%m-%d  %H:%M")
    separator = "=" * 62
    thin_sep = "-" * 62

    print("\n" + separator)
    print("                   🛒  MyShop — BILL RECEIPT")
    print(f"                   Date & Time : {now}")
    print(separator)

    if address:
        print(f"  📍 Deliver To  : {address}")
    print(f"  💳 Payment     : {payment_method}")
    print("  " + thin_sep)

    print(f"  {'#':<4} {'Product':<22} {'Qty':>5} {'Unit Price':>11} {'Subtotal':>11}")
    print("  " + thin_sep)

    for idx, item in enumerate(order_items, start=1):
        print(
            f"  {idx:<4} {item['name']:<22} {item['qty']:>5} "
            f"Rs.{item['price']:>9,.2f}  Rs.{item['subtotal']:>9,.2f}"
        )

    print("  " + thin_sep)
    print(f"  {'GRAND TOTAL':<49} Rs.{grand_total:>9,.2f}")
    print(separator)
    print("          Thank you for shopping at MyShop! 🙏")
    print(separator)


# ── CSV Export ───────────────────────────────────────────────────────────────

import csv

def save_order_csv(order_items: list, grand_total: float,
                   address: str, payment_method: str, timestamp: str):
    """
    Append the order as new rows in orders.csv.
    Writes the header row automatically if the file doesn't exist yet.

    Columns:
        Order Date, Customer Address, Payment Method,
        S.No, Product, Qty, Unit Price (Rs.), Subtotal (Rs.), Grand Total (Rs.)
    """
    _ensure_data_dir()
    file_exists = os.path.exists(ORDERS_CSV)

    try:
        with open(ORDERS_CSV, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

            # Write header only on first run
            if not file_exists:
                writer.writerow([
                    "Order Date", "Customer Address", "Payment Method",
                    "S.No", "Product", "Qty",
                    "Unit Price (Rs.)", "Subtotal (Rs.)", "Grand Total (Rs.)"
                ])

            for idx, item in enumerate(order_items, start=1):
                writer.writerow([
                    timestamp       if idx == 1 else "",
                    address         if idx == 1 else "",
                    payment_method  if idx == 1 else "",
                    idx,
                    item['name'],
                    item['qty'],
                    f"{item['price']:.2f}",
                    f"{item['subtotal']:.2f}",
                    f"{grand_total:.2f}" if idx == 1 else "",
                ])

        print(f"  ✔ Order saved to  → {ORDERS_CSV}")

    except IOError as e:
        print(f"  [Error] Could not save CSV: {e}")


def load_orders_csv() -> list:
    """
    Read the orders from orders.csv and return it as a list of dicts.
    Returns:
        list of dicts containing row data mapped by header names.
    """
    if not os.path.exists(ORDERS_CSV):
        return []
    
    rows = []
    try:
        with open(ORDERS_CSV, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)
    except IOError as e:
        print(f"  [Error] Could not load orders CSV: {e}")
        
    return rows

