"""
main.py — Entry point for the Shopping Cart System
"""

from product import Product, ProductNotFoundError, OutOfStockError
from cart import Cart, CartEmptyError
from file_handler import load_products, save_products, save_order, print_bill, load_users, save_users, load_orders_csv
from utils import get_int, get_positive_int, confirm, print_header, pause, clear_screen, safe_input


# ─────────────────────────────────────────────────────────────────────────────
# HELPER — Product Search
# ─────────────────────────────────────────────────────────────────────────────
def search_products(products: dict, query: str, in_stock_only: bool = False) -> dict:
    """
    Case-insensitive partial-name search across the product catalog.

    Args:
        products (dict): Full product catalog {id: Product}.
        query (str): Search term. Empty string returns all.
        in_stock_only (bool): If True, exclude out-of-stock items.

    Returns:
        dict: Filtered subset of products matching the query.
    """
    q = query.strip().lower()
    return {
        pid: p for pid, p in products.items()
        if (q in p.name.lower())
        and (p.stock > 0 if in_stock_only else True)
    }


def _print_product_table(subset: dict, show_stock_status: bool = False):
    """Print a compact product table for a given subset."""
    if not subset:
        print("  No products found.")
        return
    print(f"  {'ID':>5}  {'Product':<22}  {'Price':>10}  {'Stock':>6}")
    print("  " + "-" * 50)
    for p in subset.values():
        stock_tag = "" if not show_stock_status else (" ✔" if p.stock > 0 else " ✘ Out")
        print(f"  [{p.product_id:>4}]  {p.name:<22}  Rs.{p.price:>8,.2f}  {max(0,p.stock):>6}{stock_tag}")


# ─────────────────────────────────────────────────────────────────────────────
# FEATURE A — View Products
# ─────────────────────────────────────────────────────────────────────────────
def view_products(products: dict):
    """Display all products in the catalog."""
    print_header("📦  PRODUCT CATALOG")
    if not products:
        print("  No products available.")
        pause()
        return

    print(f"  {'ID':>5}  {'Product Name':<22}  {'Unit Price':>12}  {'Stock':>8}")
    print("  " + "-" * 56)
    for product in products.values():
        product.display()
    pause()


# ─────────────────────────────────────────────────────────────────────────────
# FEATURE B — Add to Cart
# ─────────────────────────────────────────────────────────────────────────────
def add_to_cart(products: dict, cart: Cart):
    """Let the user search/select a product and quantity to add to the cart."""
    print_header("➕  ADD TO CART")

    if not products:
        print("  No products available to add.")
        pause()
        return

    while True:   # search-then-select loop
        # ── Search bar ─────────────────────────────────────────────────
        query = safe_input("  🔍 Search product (Enter to show all): ").strip()
        subset = search_products(products, query, in_stock_only=True)

        print()
        if query:
            print(f"  Results for \"{query}\" ({len(subset)} found):")
        else:
            print(f"  All in-stock products ({len(subset)}):")

        _print_product_table(subset)
        print()

        if not subset:
            if not confirm("  No results. Search again?"):
                return
            print()
            continue

        # ── Pick product ID ─────────────────────────────────────────────────
        try:
            pid = get_int("  Enter Product ID (0 to search again): ", min_val=0)
            if pid == 0:
                print()
                continue     # back to search

            if pid not in products:
                raise ProductNotFoundError(f"Product ID {pid} does not exist.")

            product = products[pid]
            if product.stock <= 0:
                print(f"\n  [!] '{product.name}' is out of stock.")
                pause()
                return

            qty = get_positive_int(f"  Enter quantity (max {product.stock}): ")
            cart.add_item(product, qty)

        except ProductNotFoundError as e:
            print(f"\n  [!] {e}")
        except OutOfStockError as e:
            print(f"\n  [!] {e}")
        except ValueError as e:
            print(f"\n  [!] {e}")

        break   # exit loop after one add (success or error)

    pause()


# ─────────────────────────────────────────────────────────────────────────────
# FEATURE C — Remove from Cart
# ─────────────────────────────────────────────────────────────────────────────
def remove_from_cart(cart: Cart):
    """Let the user remove an item (fully or partially) from the cart."""
    print_header("➖  REMOVE FROM CART")

    if cart.is_empty():
        print("  Your cart is empty. Nothing to remove.")
        pause()
        return

    cart.view_cart()
    print()

    try:
        max_serial = len(cart.items)
        serial = get_int(f"  Enter item # to remove (1–{max_serial}, 0 to cancel): ", min_val=0, max_val=max_serial)
        if serial == 0:
            return

        pid = list(cart.items.keys())[serial - 1]

        current_qty = cart.items[pid]['qty']
        product_name = cart.items[pid]['product'].name

        print(f"\n  You have {current_qty} unit(s) of '{product_name}' in your cart.")

        if current_qty > 1:
            choice = get_int(
                "  Remove: 1) All units   2) Some units   (0 to cancel): ",
                min_val=0, max_val=2
            )
            if choice == 0:
                return
            elif choice == 1:
                cart.remove_item(pid)
            else:
                qty = get_int(
                    f"  How many to remove? (1–{current_qty}): ",
                    min_val=1, max_val=current_qty
                )
                cart.remove_item(pid, qty)
        else:
            if confirm(f"  Remove '{product_name}' from cart?"):
                cart.remove_item(pid)

    except ProductNotFoundError as e:
        print(f"\n  [!] {e}")
    except ValueError as e:
        print(f"\n  [!] {e}")

    pause()


# ─────────────────────────────────────────────────────────────────────────────
# FEATURE D + E — Checkout & Bill Generation
# ─────────────────────────────────────────────────────────────────────────────
def checkout(products: dict, cart: Cart):
    """Process checkout: collect address, show bill, update stock, save order, clear cart."""
    print_header("💳  CHECKOUT")

    try:
        # Validate and get order summary from cart
        order_items, grand_total = cart.checkout()

        # ── Collect Delivery Address ───────────────────────────────────────
        print("  📍 Enter Delivery Address")
        print("  " + "-" * 50)

        while True:
            name = safe_input("  Full Name      : ").strip()
            if name:
                break
            print("  [!] Name cannot be empty.")

        while True:
            street = safe_input("  Street / Area  : ").strip()
            if street:
                break
            print("  [!] Street cannot be empty.")

        while True:
            city = safe_input("  City           : ").strip()
            if city:
                break
            print("  [!] City cannot be empty.")

        while True:
            pincode = safe_input("  Pincode        : ").strip()
            if pincode.isdigit() and len(pincode) == 6:
                break
            print("  [!] Please enter a valid 6-digit pincode.")

        state = safe_input("  State (optional): ").strip()

        # Build formatted address string
        address_parts = [name, street, city]
        if state:
            address_parts.append(state)
        address_parts.append(f"PIN: {pincode}")
        address = ", ".join(address_parts)

        # ── Select Payment Method ──────────────────────────────────────────
        print("\n  💳 Select Payment Method")
        print("  " + "-" * 50)
        print("    1.  Cash on Delivery (COD)")
        print("    2.  Online Payment   (UPI / Card)")
        print()

        pay_choice = get_int("  Enter choice (1 or 2): ", min_val=1, max_val=2)

        if pay_choice == 1:
            payment_method = "Cash on Delivery (COD)"
            print("\n  ✔ Payment: Cash on Delivery selected.")

        else:
            # Simulated online payment flow
            print("\n  ── Online Payment ──────────────────────────────")
            print("    1. UPI")
            print("    2. Credit / Debit Card")
            sub_choice = get_int("  Select (1 or 2): ", min_val=1, max_val=2)

            if sub_choice == 1:
                while True:
                    upi_id = safe_input("  Enter UPI ID (e.g. name@upi): ").strip()
                    if "@" in upi_id and len(upi_id) > 3:
                        break
                    print("  [!] Invalid UPI ID. Must contain '@'.")
                payment_method = f"Online — UPI ({upi_id})"
                print(f"\n  ✔ UPI ID '{upi_id}' accepted. Payment simulated successfully.")

            else:
                while True:
                    card = safe_input("  Enter last 4 digits of card: ").strip()
                    if card.isdigit() and len(card) == 4:
                        break
                    print("  [!] Please enter exactly 4 digits.")
                payment_method = f"Online — Card (****{card})"
                print(f"\n  ✔ Card ****{card} accepted. Payment simulated successfully.")

        # ── Show Bill ──────────────────────────────────────────────────────
        print_bill(order_items, grand_total, address, payment_method)

        # Confirm purchase
        print()
        if not confirm("  Confirm purchase?"):
            print("\n  Checkout cancelled. Your cart is unchanged.")
            pause()
            return

        # Deduct stock from products (CRUD: Update)
        for item in order_items:
            products[item['product_id']].update_stock(item['qty'])

        # Save order to file with address + payment method
        save_order(order_items, grand_total, address, payment_method)

        # Save updated stock to file
        save_products(products)

        # Clear cart
        cart.clear()

        print("\n  ✔ Purchase successful! Thank you for shopping at MyShop! 🎉")

    except CartEmptyError as e:
        print(f"\n  [!] {e}")
    except OutOfStockError as e:
        print(f"\n  [!] Stock changed during session: {e}")

    pause()


# ─────────────────────────────────────────────────────────────────────────────
# USER MENU LOOP
# ─────────────────────────────────────────────────────────────────────────────
def user_menu(products: dict, username: str, cart: Cart):
    """Shopping loop for a regular user."""
    while True:
        try:
            clear_screen()
            print("=" * 62)
            print(f"            🛒  USER PORTAL — Welcome, {username}!")
            print("=" * 62)
            print(f"  Cart: {cart.item_count()} item(s)\n")
            print("    1.  View Products")
            print("    2.  Add to Cart")
            print("    3.  View Cart")
            print("    4.  Remove from Cart")
            print("    5.  Checkout & Generate Bill")
            print("    6.  Logout")
            print("=" * 62)

            choice = get_int("  Enter your choice (1–6): ", min_val=1, max_val=6)

            if choice == 1:
                view_products(products)
            elif choice == 2:
                add_to_cart(products, cart)
            elif choice == 3:
                print_header("🛒  CART SUMMARY")
                if cart.is_empty():
                    print("\n  Your cart is empty.")
                    pause()
                else:
                    query = safe_input("  🔍 Filter cart by name (Enter to show all): ").strip()
                    if query:
                        q = query.lower()
                        matching = {
                            pid: entry for pid, entry in cart.items.items()
                            if q in entry['product'].name.lower()
                        }
                        if not matching:
                            print(f"\n  No cart items matching \"{query}\".")
                        else:
                            print(f"\n  Showing {len(matching)} of {len(cart.items)} item(s) matching \"{query}\":\n")
                            print(f"  {'#':<4} {'Product':<22} {'Qty':>5} {'Price':>10} {'Subtotal':>10}")
                            print("  " + "-" * 58)
                            total = 0.0
                            for idx, (pid, entry) in enumerate(matching.items(), 1):
                                p = entry['product']
                                qty = entry['qty']
                                sub = p.price * qty
                                total += sub
                                print(f"  {idx:<4} {p.name:<22} {qty:>5} Rs.{p.price:>8,.2f}  Rs.{sub:>8,.2f}")
                            print("  " + "-" * 58)
                            print(f"  {'Subtotal (filtered)':<45} Rs.{total:>8,.2f}")
                    else:
                        cart.view_cart()
                    pause()
            elif choice == 4:
                remove_from_cart(cart)
            elif choice == 5:
                checkout(products, cart)
            elif choice == 6:
                if confirm("\n  Are you sure you want to logout?"):
                    save_products(products)
                    print(f"\n  👋 Logging out, {username}...\n")
                    break

        except KeyboardInterrupt:
            print("\n")
            print("  " + "-" * 50)
            print("  ⚠️  Ctrl+C detected.")
            try:
                answer = safe_input("  Do you want to logout? (y/n): ").strip().lower()
            except KeyboardInterrupt:
                answer = "y"
            if answer in ("y", "yes"):
                save_products(products)
                print(f"\n  👋 Logging out, {username}...\n")
                break
            else:
                print("  Returning to menu...")


# ─────────────────────────────────────────────────────────────────────────────
# ADMIN MENU LOOP
# ─────────────────────────────────────────────────────────────────────────────
def admin_menu(products: dict, username: str):
    """Admin portal to manage products."""
    while True:
        try:
            clear_screen()
            print("=" * 62)
            print(f"           🛠️  ADMIN PORTAL — Logged in as {username}")
            print("=" * 62)
            print("    1.  View All Products")
            print("    2.  Add New Product")
            print("    3.  Update Product")
            print("    4.  Remove Product")
            print("    5.  View Orders")
            print("    6.  Logout")
            print("=" * 62)

            choice = get_int("  Enter your choice (1–6): ", min_val=1, max_val=6)

            if choice == 1:
                view_products(products)
            elif choice == 2:
                print_header("➕  ADD NEW PRODUCT")
                pid = get_int("  Product ID: ", min_val=1)
                if pid in products:
                    print(f"  [!] Product ID {pid} already exists.")
                    pause()
                    continue
                name = safe_input("  Product Name: ").strip()
                if not name:
                    name = "Unnamed Product"
                price = None
                while price is None:
                    try:
                        price = float(safe_input("  Price: "))
                        if price < 0:
                            print("  [!] Price cannot be negative.")
                            price = None
                    except ValueError:
                        print("  [!] Invalid input. Enter a numeric value.")
                stock = get_int("  Stock: ", min_val=0)
                
                products[pid] = Product(pid, name, price, stock)
                save_products(products)
                print(f"\n  ✔ Product '{name}' added successfully.")
                pause()
            elif choice == 3:
                print_header("✏️  UPDATE PRODUCT")
                pid = get_int("  Enter Product ID to update (0 to cancel): ", min_val=0)
                if pid == 0:
                    continue
                if pid not in products:
                    print(f"  [!] Product ID {pid} not found.")
                else:
                    p = products[pid]
                    print(f"  Updating: {p.name} (Price: Rs.{p.price:.2f}, Stock: {p.stock})")
                    new_price_str = safe_input("  New Price (Leave blank to keep existing): ").strip()
                    if new_price_str:
                        try:
                            p.price = float(new_price_str)
                        except ValueError:
                            print("  [!] Invalid price entered.")
                    new_stock_str = safe_input("  New Stock (Leave blank to keep existing): ").strip()
                    if new_stock_str:
                        try:
                            p.stock = int(new_stock_str)
                        except ValueError:
                            print("  [!] Invalid stock entered.")
                    save_products(products)
                    print(f"\n  ✔ Product '{p.name}' updated successfully.")
                pause()
            elif choice == 4:
                print_header("➖  REMOVE PRODUCT")
                pid = get_int("  Enter Product ID to remove (0 to cancel): ", min_val=0)
                if pid == 0:
                    continue
                if pid not in products:
                    print(f"  [!] Product ID {pid} not found.")
                else:
                    p = products[pid]
                    if confirm(f"  Delete '{p.name}'?"):
                        del products[pid]
                        save_products(products)
                        print(f"\n  ✔ Product '{p.name}' removed completely.")
                pause()
            elif choice == 5:
                print_header("📋  VIEW ORDERS")
                
                orders = load_orders_csv()
                if not orders:
                    print("  No orders have been placed yet.")
                    pause()
                    continue
                
                query = safe_input("  🔍 Filter orders (by Customer, Product, Date... or Enter to view all): ").strip().lower()
                
                # Match query across any value in the row
                matching_orders = []
                for row in orders:
                    row_values_str = " ".join([str(v).lower() for v in row.values()])
                    if query in row_values_str:
                        matching_orders.append(row)
                
                if not matching_orders:
                    print(f"\n  [!] No orders found matching '{query}'.")
                else:
                    print(f"\n  Showing {len(matching_orders)} of {len(orders)} order records")
                    print("  " + "-" * 115)
                    print(f"  {'Order Date':<18} | {'Customer':<20} | {'Method':<12} | {'Product':<20} | {'Qty':>3} | {'Total':>10}")
                    print("  " + "-" * 115)
                    
                    for row in matching_orders:
                        # Extract first 20 chars of customer formatting and keep it readable
                        cust = str(row.get('Customer Address', ''))[:18] + '..' if len(row.get('Customer Address', '')) > 20 else row.get('Customer Address', '')
                        prod = str(row.get('Product', ''))[:18] + '..' if len(row.get('Product', '')) > 20 else row.get('Product', '')
                        date = str(row.get('Order Date', ''))[:16]
                        method = str(row.get('Payment Method', ''))[:10] + '..' if len(row.get('Payment Method', '')) > 12 else row.get('Payment Method', '')
                        qty = row.get('Qty', '')
                        total = row.get('Grand Total (Rs.)', '') or row.get('Subtotal (Rs.)', '') # Use subtotal if grand total is blank for sub-items
                        
                        print(f"  {date:<18} | {cust:<20} | {method:<12} | {prod:<20} | {qty:>3} | Rs.{total:>7}")
                    print("  " + "-" * 115)
                pause()
                
            elif choice == 6:
                if confirm("\n  Are you sure you want to logout?"):
                    save_products(products)
                    print(f"\n  👋 Logging out Admin {username}...\n")
                    break

        except KeyboardInterrupt:
            print("\n")
            print("  " + "-" * 50)
            print("  ⚠️  Ctrl+C detected.")
            try:
                answer = safe_input("  Do you want to logout? (y/n): ").strip().lower()
            except KeyboardInterrupt:
                answer = "y"
            if answer in ("y", "yes"):
                save_products(products)
                print(f"\n  👋 Logging out Admin {username}...\n")
                break
            else:
                print("  Returning to admin menu...")


# ─────────────────────────────────────────────────────────────────────────────
# AUTHENTICATION AND ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────
def main():
    """Main entry point: manage users, authenticate, and route to proper portal."""
    print("\n" + "=" * 62)
    print("         Welcome to  🛒  MyShop — Authentication System")
    print("=" * 62)

    users = load_users()
    products = load_products()
    print(f"  📦 {len(products)} product(s) loaded.")
    print(f"  👥 {len(users)} user(s) loaded.")

    # In-memory storage to preserve carts across logins during this session
    active_carts = {}

    while True:
        try:
            clear_screen()
            print("=" * 62)
            print("                    🔐  LOGIN MENU")
            print("=" * 62)
            print("    1.  Login")
            print("    2.  Register")
            print("    3.  Exit System")
            print("=" * 62)

            choice = get_int("  Enter your choice (1–3): ", min_val=1, max_val=3)

            if choice == 1:
                print_header("🔑  LOGIN")
                username = safe_input("  Username: ").strip()
                password = safe_input("  Password: ").strip()

                if username in users and users[username]['password'] == password:
                    role = users[username].get('role', 'user')
                    print(f"\n  ✔ Login successful! Role: {role.capitalize()}")
                    pause()
                    if role == 'admin':
                        admin_menu(products, username)
                    else:
                        if username not in active_carts:
                            active_carts[username] = Cart()
                        user_menu(products, username, active_carts[username])
                else:
                    print("\n  [!] Invalid username or password.")
                    pause()

            elif choice == 2:
                print_header("📝  REGISTER")
                username = safe_input("  Choose Username: ").strip()
                if not username:
                    print("\n  [!] Username cannot be empty.")
                    pause()
                    continue
                if username in users:
                    print("\n  [!] Username already exists. Please choose another.")
                    pause()
                    continue

                password = safe_input("  Choose Password: ").strip()
                if not password:
                    print("\n  [!] Password cannot be empty.")
                    pause()
                    continue

                # Register as a standard user
                users[username] = {'password': password, 'role': 'user'}
                save_users(users)
                print(f"\n  ✔ Registration successful for '{username}'! You can now log in.")
                pause()

            elif choice == 3:
                if confirm("\n  Are you sure you want to stop the system?"):
                    save_products(products)
                    save_users(users)
                    print("\n  👋 Shutting down MyShop. Goodbye!\n")
                    break

        except KeyboardInterrupt:
            print("\n")
            print("  " + "-" * 50)
            print("  ⚠️  Ctrl+C detected.")
            try:
                answer = safe_input("  Do you want to exit the system? (y/n): ").strip().lower()
            except KeyboardInterrupt:
                answer = "y"
            if answer in ("y", "yes"):
                save_products(products)
                save_users(users)
                print("\n  👋 Shutting down MyShop. Goodbye!\n")
                break
            else:
                print("  Returning to auth menu...")

if __name__ == "__main__":
    main()
