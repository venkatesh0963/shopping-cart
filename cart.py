"""
cart.py — Cart class for the Shopping Cart System
"""

from product import Product, OutOfStockError, ProductNotFoundError


class CartEmptyError(Exception):
    """Raised when checkout is attempted with an empty cart."""
    pass


class Cart:
    """
    Represents a user's shopping cart.

    Attributes:
        items (dict): Mapping of product_id -> {'product': Product, 'qty': int}
    """

    def __init__(self):
        self.__items: dict = {}  # { product_id: {'product': Product, 'qty': int} }

    # ── Read ──────────────────────────────────────────────────────────────
    @property
    def items(self) -> dict:
        return self.__items

    def is_empty(self) -> bool:
        """Return True if cart has no items."""
        return len(self.__items) == 0

    def item_count(self) -> int:
        """Return total number of units in cart."""
        return sum(entry['qty'] for entry in self.__items.values())

    # ── Create / Update ───────────────────────────────────────────────────
    def add_item(self, product: Product, quantity: int):
        """
        Add a product to the cart or increase its quantity.

        Args:
            product (Product): The product to add.
            quantity (int): Units to add.

        Raises:
            OutOfStockError: If total requested qty exceeds available stock.
            ValueError: If quantity <= 0.
        """
        if quantity <= 0:
            raise ValueError("Quantity must be a positive integer.")

        current_qty = 0
        if product.product_id in self.__items:
            current_qty = self.__items[product.product_id]['qty']

        total_requested = current_qty + quantity
        if total_requested > product.stock:
            raise OutOfStockError(
                f"Cannot add {quantity} unit(s). Only {product.stock - current_qty} "
                f"more unit(s) of '{product.name}' can be added."
            )

        if product.product_id in self.__items:
            self.__items[product.product_id]['qty'] += quantity
        else:
            self.__items[product.product_id] = {
                'product': product,
                'qty': quantity
            }
        print(f"\n  ✔ '{product.name}' x{quantity} added to cart.")

    # ── Delete ────────────────────────────────────────────────────────────
    def remove_item(self, product_id: int, quantity: int = None):
        """
        Remove a product from the cart (fully or partially).

        Args:
            product_id (int): ID of the product to remove.
            quantity (int | None): Units to remove. If None, remove all.

        Raises:
            ProductNotFoundError: If product is not in cart.
            ValueError: If quantity > current cart qty.
        """
        if product_id not in self.__items:
            raise ProductNotFoundError(
                f"Product ID {product_id} is not in your cart."
            )

        entry = self.__items[product_id]
        product_name = entry['product'].name

        if quantity is None or quantity >= entry['qty']:
            del self.__items[product_id]
            print(f"\n  ✔ '{product_name}' fully removed from cart.")
        else:
            if quantity <= 0:
                raise ValueError("Quantity to remove must be positive.")
            entry['qty'] -= quantity
            print(
                f"\n  ✔ Removed {quantity} unit(s) of '{product_name}'. "
                f"Remaining in cart: {entry['qty']}."
            )

    # ── View ──────────────────────────────────────────────────────────────
    def view_cart(self):
        """Display all items in the cart with subtotals and grand total."""
        if self.is_empty():
            print("\n  Your cart is empty.")
            return

        print("\n" + "=" * 62)
        print("                     🛒  YOUR CART")
        print("=" * 62)
        print(f"  {'#':<4} {'Product':<22} {'Qty':>5} {'Price':>10} {'Subtotal':>10}")
        print("  " + "-" * 58)

        grand_total = 0.0
        for idx, (pid, entry) in enumerate(self.__items.items(), start=1):
            p = entry['product']
            qty = entry['qty']
            subtotal = p.price * qty
            grand_total += subtotal
            print(
                f"  {idx:<4} {p.name:<22} {qty:>5} "
                f"Rs.{p.price:>7,.2f}  Rs.{subtotal:>8,.2f}"
            )

        print("  " + "-" * 58)
        print(f"  {'Grand Total':<45} Rs.{grand_total:>8,.2f}")
        print("=" * 62)

    # ── Checkout ──────────────────────────────────────────────────────────
    def checkout(self) -> tuple:
        """
        Process checkout: validate stock, return order summary.

        Returns:
            tuple: (list of order_items dicts, grand_total float)

        Raises:
            CartEmptyError: If cart is empty.
            OutOfStockError: If any item's stock is insufficient now.
        """
        if self.is_empty():
            raise CartEmptyError("Your cart is empty. Add items before checkout.")

        order_items = []
        grand_total = 0.0

        for pid, entry in self.__items.items():
            product = entry['product']
            qty = entry['qty']

            # Re-validate stock at checkout time
            if qty > product.stock:
                raise OutOfStockError(
                    f"Insufficient stock for '{product.name}'. "
                    f"Available: {product.stock}, Requested: {qty}."
                )

            subtotal = product.price * qty
            grand_total += subtotal
            order_items.append({
                'product_id': pid,
                'name': product.name,
                'qty': qty,
                'price': product.price,
                'subtotal': subtotal,
                'product_obj': product
            })

        return order_items, grand_total

    def clear(self):
        """Empty the cart after successful checkout."""
        self.__items.clear()

    def __str__(self) -> str:
        return f"Cart({self.item_count()} items)"
