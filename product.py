"""
product.py — Product class for the Shopping Cart System
"""


class ProductNotFoundError(Exception):
    """Raised when a product ID does not exist in the catalog."""
    pass


class OutOfStockError(Exception):
    """Raised when requested quantity exceeds available stock."""
    pass


class Product:
    """
    Represents a single product in the store catalog.

    Attributes:
        product_id (int): Unique identifier for the product.
        name (str): Product name.
        price (float): Price per unit in INR.
        stock (int): Available quantity in stock.
    """

    def __init__(self, product_id: int, name: str, price: float, stock: int):
        self.__product_id = int(product_id)
        self.__name = str(name).strip()
        self.__price = float(price)
        self.__stock = int(stock)

    # ── Getters ───────────────────────────────────────────────────────────
    @property
    def product_id(self) -> int:
        return self.__product_id

    @property
    def name(self) -> str:
        return self.__name

    @property
    def price(self) -> float:
        return self.__price

    @property
    def stock(self) -> int:
        return self.__stock

    # ── Setters ───────────────────────────────────────────────────────────
    @price.setter
    def price(self, value: float):
        if value < 0:
            raise ValueError("Price cannot be negative.")
        self.__price = float(value)

    @stock.setter
    def stock(self, value: int):
        if value < 0:
            raise ValueError("Stock cannot be negative.")
        self.__stock = int(value)

    # ── Methods ───────────────────────────────────────────────────────────
    def update_stock(self, quantity: int):
        """
        Deduct sold quantity from stock.

        Args:
            quantity (int): Units sold / to be deducted.

        Raises:
            OutOfStockError: If quantity exceeds available stock.
        """
        if quantity > self.__stock:
            raise OutOfStockError(
                f"Only {self.__stock} unit(s) of '{self.__name}' available."
            )
        self.__stock = max(0, self.__stock - quantity)

    def display(self):
        """Print a formatted single-line product listing."""
        display_stock = max(0, self.__stock)
        stock_status = "In Stock" if display_stock > 0 else "Out of Stock"
        print(
            f"  [{self.__product_id:>4}]  {self.__name:<22}  "
            f"Rs.{self.__price:>8,.2f}  Stock: {display_stock:>4}  ({stock_status})"
        )

    def to_file_line(self) -> str:
        """Serialize product to a pipe-delimited string for file storage."""
        return f"{self.__product_id}|{self.__name}|{self.__price:.2f}|{self.__stock}"

    def __str__(self) -> str:
        return (
            f"Product(id={self.__product_id}, name='{self.__name}', "
            f"price={self.__price:.2f}, stock={self.__stock})"
        )

    def __repr__(self) -> str:
        return self.__str__()
