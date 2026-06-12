"""
utils.py — Validation helpers and UI utilities for the Shopping Cart System
"""


# ── Input Helpers ─────────────────────────────────────────────────────────────

def safe_input(prompt: str) -> str:
    """
    Wrapper around input() that re-raises KeyboardInterrupt cleanly
    (prints a newline first so the console prompt isn't left dangling).
    """
    try:
        return input(prompt)
    except KeyboardInterrupt:
        print()          # move cursor to next line
        raise            # let the caller / main loop handle it


def get_int(prompt: str, min_val: int = None, max_val: int = None) -> int:
    """
    Prompt the user for an integer, retrying until valid input is given.
    KeyboardInterrupt is propagated so Ctrl+C reaches the main loop.

    Args:
        prompt (str): Message to display.
        min_val (int | None): Minimum acceptable value (inclusive).
        max_val (int | None): Maximum acceptable value (inclusive).

    Returns:
        int: Validated integer input.
    """
    while True:
        try:
            value = int(safe_input(prompt).strip())
            if min_val is not None and value < min_val:
                print(f"  [!] Please enter a value >= {min_val}.")
                continue
            if max_val is not None and value > max_val:
                print(f"  [!] Please enter a value <= {max_val}.")
                continue
            return value
        except ValueError:
            print("  [!] Invalid input. Please enter a whole number.")
        # KeyboardInterrupt is NOT caught here — bubbles up intentionally


def get_positive_int(prompt: str) -> int:
    """Prompt for a positive (>= 1) integer."""
    return get_int(prompt, min_val=1)


def confirm(prompt: str) -> bool:
    """
    Ask a yes/no confirmation question.
    KeyboardInterrupt is propagated so Ctrl+C reaches the main loop.

    Returns:
        bool: True if user types 'y' or 'yes', False otherwise.
    """
    try:
        answer = safe_input(prompt + " (y/n): ").strip().lower()
        return answer in ("y", "yes")
    except KeyboardInterrupt:
        raise   # let main loop handle it


# ── Display Helpers ───────────────────────────────────────────────────────────

def print_header(title: str):
    """Print a prominent section header."""
    width = 62
    print("\n" + "=" * width)
    print(f"  {title}")
    print("=" * width)


def print_divider():
    print("  " + "-" * 58)


def pause():
    """Wait for the user to press Enter before continuing."""
    try:
        safe_input("\n  Press Enter to return to menu...")
    except KeyboardInterrupt:
        raise   # let main loop handle it


def clear_screen():
    """Print blank lines to visually separate sections (cross-platform)."""
    print("\n" * 2)
