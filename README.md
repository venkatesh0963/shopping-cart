# 🛒 Shopping Cart System

A console-based e-commerce shopping cart application built in **pure Python**,
demonstrating OOP, CRUD, File Handling, and Exception Handling.

---

## Project Structure

```
Shopping_cart/
├── main.py            ← Entry point (main menu loop).
├── product.py         ← Product class + custom exceptions.
├── cart.py            ← Cart class (add, remove, checkout).
├── file_handler.py    ← Load/save products & orders to disk.
├── utils.py           ← Input validation & display helpers.
│
└── data/
    ├── products.txt   ← Product catalog (auto-updated on exit).
    └── orders.txt     ← Order receipts (appended on checkout).
```

---

## How to Run.....

```bash
python main.py
```

Requires **Python 3.8+** — no third-party packages needed.

---

## Features

| # | Feature | Description |
|---|---------|-------------|
| A | Product Listing | View all products with ID, name, price, and stock |
| B | Add to Cart | Select product by ID and quantity; stock-validated |
| C | Remove from Cart | Remove fully or partially; handles empty-cart edge case |
| D | Checkout & Bill | Itemized bill with grand total, printed and saved to file |
| E | Stock Validation | Prevents over-purchase; all inputs validated with try/except |
| F | Menu Loop | 6-option menu that loops until user exits |

---

## OOP Design

### `Product` class (`product.py`)
- **Attributes**: `product_id`, `name`, `price`, `stock` (private with properties)
- **Methods**: `display()`, `update_stock()`, `to_file_line()`
- **Custom Exceptions**: `ProductNotFoundError`, `OutOfStockError`

### `Cart` class (`cart.py`)
- **Attributes**: `items` (dict: `{product_id: {product, qty}}`)
- **Methods**: `add_item()`, `remove_item()`, `view_cart()`, `checkout()`, `clear()`
- **Custom Exception**: `CartEmptyError`

---

## CRUD Mapping

| Operation | Where |
|-----------|-------|
| **Create** | Add item to cart (`cart.add_item`) |
| **Read** | View products, view cart, load from file |
| **Update** | Increase qty in cart, deduct stock after purchase |
| **Delete** | Remove item from cart, clear cart post-checkout |

---

## File Handling

| File | Operation | When |
|------|-----------|------|
| `products.txt` | Read | On startup |
| `products.txt` | Write (overwrite) | On exit & after checkout |
| `orders.txt` | Append | After each successful checkout |

---

## Exception Handling

- `ProductNotFoundError` — invalid product ID entered
- `OutOfStockError` — quantity exceeds stock
- `CartEmptyError` — checkout attempted on empty cart
- `ValueError` — non-integer input for numeric fields
- `FileNotFoundError` — missing data files on first run
- `IOError` — disk write failures

---

## Sample Menu

```
==============================================================
                    🛒  MAIN MENU
==============================================================
  Cart: 0 item(s)

    1.  View Products
    2.  Add to Cart
    3.  View Cart
    4.  Remove from Cart
    5.  Checkout & Generate Bill
    6.  Exit
==============================================================
```

---

## Evaluation Compliance

| Criteria | Marks | Implementation |
|----------|-------|---------------|
| OOP | 20 | 2 classes, properties, custom exceptions |
| CRUD | 20 | Full create/read/update/delete in cart & products |
| File Handling | 15 | Read on load, write on exit/checkout, append orders |
| Exception Handling | 15 | try/except on all user inputs and file ops |
| Menu & Flow | 10 | 6-option looping menu, clean navigation |
| Code Quality | 10 | PEP 8, docstrings, single-responsibility functions |
| Output Formatting | 10 | Aligned tables, formatted bill with header/footer |
| **Total** | **100** | |
