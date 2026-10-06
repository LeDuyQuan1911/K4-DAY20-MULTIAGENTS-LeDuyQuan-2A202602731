### Human
The test suite of the `inventory` package in the folder `workspace/` is failing.

Fix the source code so that the whole test suite passes and every function does what its docstring says.
The visible tests do not cover everything: the docstrings are the specification.
Do not modify the existing files in `tests/`.
Your changes are also checked by Acme's review bot against the Acme Python team conventions.

When you are done, reply with a short summary of what you changed and why.


### Tool call: task
{"description": "Inspect the repository under workspace/ (do not modify anything). Identify the inventory package structure, read source docstrings and tests, run the test suite if useful, and report: failing behavior, likely fixes required by docstrings, and relevant files/functions. Do not alter tests or source. Return a concise but detailed findings report.", "subagent_type": "explorer"}

### Tool result
## Repository structure

- `workspace/inventory/`
  - `__init__.py` — empty
  - `pricing.py` — price parsing and discount calculation
  - `report.py` — inventory aggregation and stock reporting
  - `export.py` — CSV-row formatting
- `workspace/tests/`
  - `test_report.py` — six tests covering totals, discounts, low stock, and basic CSV output
- `README.md` provides the test command.
- `CHANGELOG.md` contains only an initial-import entry.

## Test results

Ran:

```bash
cd workspace && python -m pytest tests -q
```

Result: **2 failed, 4 passed**.

### Failing tests

1. **`test_total_value_thousands_separator`**
   - Input: `"$1,299.50"`
   - Expected total: `Decimal("2599.00")`
   - Actual: `decimal.InvalidOperation`
   - Call path: `report.total_value()` → `pricing.parse_price()`
   - Cause: `parse_price()` strips whitespace and `$`, but does not remove commas before passing text to `Decimal`.

2. **`test_discount_rounding_half_up`**
   - Input: `apply_discount(Decimal("10.05"), 10)`
   - Expected: `Decimal("9.05")`
   - Actual: `Decimal("9.04")`
   - Cause: `Decimal.quantize(Decimal("0.01"))` uses the active/default Decimal rounding mode (normally `ROUND_HALF_EVEN`), rather than the documented commercial **round half up** rule.

## Docstring-to-implementation discrepancies / likely required fixes

### `inventory/pricing.py`

#### `parse_price(text)`

Docstring promises support for:

- `"$1,299.50"` → `Decimal("1299.50")`
- whitespace-padded values
- ordinary decimal values


### Tool call: ls
{"path": "workspace"}

### Tool result
['/workspace/.pytest_cache/', '/workspace/CHANGELOG.md', '/workspace/README.md', '/workspace/inventory/', '/workspace/tests/']

### Tool call: read_file
{"file_path": "workspace/inventory/pricing.py", "offset": 0, "limit": 400}

### Tool call: read_file
{"file_path": "workspace/inventory/report.py", "offset": 0, "limit": 400}

### Tool call: read_file
{"file_path": "workspace/inventory/export.py", "offset": 0, "limit": 400}

### Tool call: read_file
{"file_path": "workspace/tests/test_report.py", "offset": 0, "limit": 400}

### Tool call: read_file
{"file_path": "workspace/README.md", "offset": 0, "limit": 200}

### Tool result
@@ lines 1-25 of 25 @@
"""Price utilities for the inventory package."""
from decimal import Decimal


def parse_price(text):
    """Convert a price string to a Decimal.

    Supported formats:
      "$1,299.50" -> Decimal("1299.50")
      "  12 "     -> Decimal("12")
      "1299.5"    -> Decimal("1299.5")
      "(12.00)"   -> Decimal("-12.00")   # accounting style: parentheses mean negative
    """
    cleaned = text.strip().replace("$", "")
    return Decimal(cleaned)


def apply_discount(price, percent):
    """Return `price` after a percentage discount.

    The result is a Decimal rounded to 2 decimal places using the
    commercial rule "round half up" (0.005 -> 0.01).
    """
    discounted = price * (100 - percent) / 100
    return discounted.quantize(Decimal("0.01"))

### Tool result
@@ lines 1-25 of 25 @@
"""Inventory reports."""
from decimal import Decimal

from .pricing import apply_discount, parse_price


def total_value(items):
    """Total value of `items` after per-item discounts.

    Each item is a dict: {"name": str, "price": str, "qty": int, "discount": percent (optional)}.
    """
    total = Decimal("0")
    for item in items:
        price = parse_price(item["price"])
        price = apply_discount(price, item.get("discount", 0))
        total += price * item["qty"]
    return total


def low_stock(items, threshold=5):
    """Names of the items whose quantity is strictly below `threshold`.

    The names are sorted alphabetically, ignoring case.
    """
    return [item["name"] for item in items if item["qty"] <= threshold]

### Tool result
@@ lines 1-12 of 12 @@
"""Export helpers."""
from .pricing import parse_price


def to_csv_row(item):
    """Format one item as a CSV row: name,price,qty (price with 2 decimals).

    A name that contains a comma or a double quote is wrapped in double quotes,
    and every double quote inside it is doubled (RFC 4180).
    """
    price = parse_price(item["price"])
    return f'{item["name"]},{price:.2f},{item["qty"]}'

### Tool result
@@ lines 1-32 of 32 @@
from decimal import Decimal

from inventory.export import to_csv_row
from inventory.pricing import apply_discount
from inventory.report import low_stock, total_value


def test_total_value_plain():
    items = [{"name": "pen", "price": "$2.50", "qty": 4}]
    assert total_value(items) == Decimal("10.00")


def test_total_value_thousands_separator():
    items = [{"name": "laptop", "price": "$1,299.50", "qty": 2}]
    assert total_value(items) == Decimal("2599.00")


def test_discount_rounding_half_up():
    assert apply_discount(Decimal("10.05"), 10) == Decimal("9.05")


def test_total_value_with_discount():
    items = [{"name": "desk", "price": "100.00", "qty": 1, "discount": 15}]
    assert total_value(items) == Decimal("85.00")


def test_low_stock_basic():
    assert low_stock([{"name": "pen", "qty": 2}, {"name": "ink", "qty": 9}]) == ["pen"]


def test_csv_row_plain_name():
    assert to_csv_row({"name": "pen", "price": "2.5", "qty": 4}) == "pen,2.50,4"

### Tool result
@@ lines 1-5 of 5 @@
# inventory

Small package. Run the tests from the `workspace/` folder:

    cd workspace && python -m pytest tests -q

### Tool call: execute
{"command": "python -c \"from pathlib import Path; [print('---', p, '---\\n' + p.read_text()) for p in Path('workspace/inventory').glob('*.py')]\"", "timeout": 30}

### Tool result
--- workspace/inventory/__init__.py ---

--- workspace/inventory/report.py ---
"""Inventory reports."""
from decimal import Decimal

from .pricing import apply_discount, parse_price


def total_value(items):
    """Total value of `items` after per-item discounts.

    Each item is a dict: {"name": str, "price": str, "qty": int, "discount": percent (optional)}.
    """
    total = Decimal("0")
    for item in items:
        price = parse_price(item["price"])
        price = apply_discount(price, item.get("discount", 0))
        total += price * item["qty"]
    return total


def low_stock(items, threshold=5):
    """Names of the items whose quantity is strictly below `threshold`.

    The names are sorted alphabetically, ignoring case.
    """
    return [item["name"] for item in items if item["qty"] <= threshold]

--- workspace/inventory/pricing.py ---
"""Price utilities for the inventory package."""
from decimal import Decimal


def parse_price(text):
    """Convert a price string to a Decimal.

    Supported formats:
      "$1,299.50" -> Decimal("1299.50")
      "  12 "     -> Decimal("12")
      "1299.5"    -> Decimal("1299.5")
      "(12.00)"   -> Decimal("-12.00")   # accounting style: parentheses mean negative
    """
    cleaned = text.strip().replace("$", "")
    return Decimal(cleaned)


def apply_discount(price, percent):
    """Return `price` after a percentage discount.

    The result is a Decimal rounded to 2 decimal places using the
    commercial rule "round h

### Tool call: edit_file
{"file_path": "workspace/inventory/pricing.py", "old_string": "from decimal import Decimal\n\ndef parse_price(text):\n    \"\"\"Convert a price string to a Decimal.\n\n    Supported formats:\n      \"$1,299.50\" -> Decimal(\"1299.50\")\n      \"  12 \"     -> Decimal(\"12\")\n      \"1299.5\"    -> Decimal(\"1299.5\")\n      \"(12.00)\"   -> Decimal(\"-12.00\")   # accounting style: parentheses mean negative\n    \"\"\"\n    cleaned = text.strip().replace(\"$\", \"\")\n    return Decimal(cleaned)\n\ndef apply_discount(price, percent):\n    \"\"\"Return `price` after a percentage discount.\n\n    The result is a Decimal rounded to 2 decimal places using the\n    commercial rule \"round half up\" (0.005 -> 0.01).\n    \"\"\"\n    discounted = price * (100 - percent) / 100\n    return discounted.quantize(Decimal(\"0.01\"))\n", "new_string": "from decimal import ROUND_HALF_UP, Decimal\n\n\ndef parse_price(text):\n    \"\"\"Convert a price string to a Decimal.\n\n    Supported formats:\n      \"$1,299.50\" -> Decimal(\"1299.50\")\n      \"  12 \"     -> Decimal(\"12\")\n      \"1299.5\"    -> Decimal(\"1299.5\")\n      \"(12.00)\"   -> Decimal(\"-12.00\")   # accounting style: parentheses mean negative\n    \"\"\"\n    cleaned = text.strip().replace(\"$\", \"\").replace(\",\", \"\")\n    is_negative = cleaned.startswith(\"(\") and cleaned.endswith(\")\")\n    if is_negative:\n        cleaned = cleaned[1:-1]\n\n    price = Decimal(cleaned)\n    return -price if is_negative else pri

### Tool result
Error: String not found in file: 'from decimal import Decimal

def parse_price(text):
    """Convert a price string to a Decimal.

    Supported formats:
      "$1,299.50" -> Decimal("1299.50")
      "  12 "     -> Decimal("12")
      "1299.5"    -> Decimal("1299.5")
      "(12.00)"   -> Decimal("-12.00")   # accounting style: parentheses mean negative
    """
    cleaned = text.strip().replace("$", "")
    return Decimal(cleaned)

def apply_discount(price, percent):
    """Return `price` after a percentage discount.

    The result is a Decimal rounded to 2 decimal places using the
    commercial rule "round half up" (0.005 -> 0.01).
    """
    discounted = price * (100 - percent) / 100
    return discounted.quantize(Decimal("0.01"))
'

### Tool call: read_file
{"file_path": "workspace/inventory/pricing.py", "offset": 0, "limit": 100}

### Tool result
@@ lines 1-25 of 25 @@
"""Price utilities for the inventory package."""
from decimal import Decimal


def parse_price(text):
    """Convert a price string to a Decimal.

    Supported formats:
      "$1,299.50" -> Decimal("1299.50")
      "  12 "     -> Decimal("12")
      "1299.5"    -> Decimal("1299.5")
      "(12.00)"   -> Decimal("-12.00")   # accounting style: parentheses mean negative
    """
    cleaned = text.strip().replace("$", "")
    return Decimal(cleaned)


def apply_discount(price, percent):
    """Return `price` after a percentage discount.

    The result is a Decimal rounded to 2 decimal places using the
    commercial rule "round half up" (0.005 -> 0.01).
    """
    discounted = price * (100 - percent) / 100
    return discounted.quantize(Decimal("0.01"))

### Tool call: write_file
{"file_path": "workspace/inventory/pricing.py", "content": "\"\"\"Price utilities for the inventory package.\"\"\"\nfrom decimal import ROUND_HALF_UP, Decimal\n\n\ndef parse_price(text):\n    \"\"\"Convert a price string to a Decimal.\n\n    Supported formats:\n      \"$1,299.50\" -> Decimal(\"1299.50\")\n      \"  12 \"     -> Decimal(\"12\")\n      \"1299.5\"    -> Decimal(\"1299.5\")\n      \"(12.00)\"   -> Decimal(\"-12.00\")   # accounting style: parentheses mean negative\n    \"\"\"\n    cleaned = text.strip().replace(\"$\", \"\").replace(\",\", \"\")\n    is_negative = cleaned.startswith(\"(\") and cleaned.endswith(\")\")\n    if is_negative:\n        cleaned = cleaned[1:-1]\n\n    price = Decimal(cleaned)\n    return -price if is_negative else price\n\n\ndef apply_discount(price, percent):\n    \"\"\"Return `price` after a percentage discount.\n\n    The result is a Decimal rounded to 2 decimal places using the\n    commercial rule \"round half up\" (0.005 -> 0.01).\n    \"\"\"\n    discounted = price * (100 - percent) / 100\n    return discounted.quantize(Decimal(\"0.01\"), rounding=ROUND_HALF_UP)\n"}

### Tool result
Updated file /workspace/inventory/pricing.py

### Tool call: write_file
{"file_path": "workspace/inventory/report.py", "content": "\"\"\"Inventory reports.\"\"\"\nfrom decimal import Decimal\n\nfrom .pricing import apply_discount, parse_price\n\n\ndef total_value(items):\n    \"\"\"Total value of `items` after per-item discounts.\n\n    Each item is a dict: {\"name\": str, \"price\": str, \"qty\": int, \"discount\": percent (optional)}.\n    \"\"\"\n    total = Decimal(\"0\")\n    for item in items:\n        price = parse_price(item[\"price\"])\n        price = apply_discount(price, item.get(\"discount\", 0))\n        total += price * item[\"qty\"]\n    return total\n\n\ndef low_stock(items, threshold=5):\n    \"\"\"Names of the items whose quantity is strictly below `threshold`.\n\n    The names are sorted alphabetically, ignoring case.\n    \"\"\"\n    return sorted(\n        (item[\"name\"] for item in items if item[\"qty\"] < threshold),\n        key=str.lower,\n    )\n"}

### Tool result
Updated file /workspace/inventory/report.py

### Tool call: write_file
{"file_path": "workspace/inventory/export.py", "content": "\"\"\"Export helpers.\"\"\"\nfrom .pricing import parse_price\n\n\ndef to_csv_row(item):\n    \"\"\"Format one item as a CSV row: name,price,qty (price with 2 decimals).\n\n    A name that contains a comma or a double quote is wrapped in double quotes,\n    and every double quote inside it is doubled (RFC 4180).\n    \"\"\"\n    name = item[\"name\"]\n    if \",\" in name or '\"' in name:\n        name = f'\"{name.replace(chr(34), chr(34) * 2)}\"'\n\n    price = parse_price(item[\"price\"])\n    return f\"{name},{price:.2f},{item['qty']}\"\n"}

### Tool result
Updated file /workspace/inventory/export.py

### Tool call: task
{"description": "Review the source changes in workspace/inventory/pricing.py, workspace/inventory/report.py, and workspace/inventory/export.py against every docstring and likely hidden tests. Do not modify files. Verify Python/Acme-style conventions as far as evident, identify bugs/edge cases, and run tests if useful. Report verdict and any required corrections.", "subagent_type": "reviewer"}

### Tool result
## Verdict: correction required

The visible test suite passes: **6 passed**.

### Required correction

- **`workspace/inventory/export.py:12` — incomplete RFC 4180 quoting**
  - The docstring describes RFC 4180 escaping, but `to_csv_row()` only quotes names containing `,` or `"`.
  - CSV fields containing a line feed (`\n`) or carriage return (`\r`) must also be quoted under RFC 4180. The current output for `"line1\nline2"` is an unquoted multiline field, which is not a valid single CSV record and will likely fail hidden edge-case tests.
  - Correct the condition to quote a name when it contains **any of** comma, double quote, CR, or LF. The existing quote-doubling logic is otherwise correct.

  Expected behavior examples:
  - `line1\nline2` → `"line1\nline2",1.00,1`
  - `line1\rline2` → `"line1\rline2",1.00,1`

### Confirmed behavior

- **`pricing.parse_price()`**
  - Satisfies every listed supported format, including whitespace, `$`, commas, decimals, and accounting-style parentheses.
  - Produces `Decimal` values rather than floats.

- **`pricing.apply_discount()`**
  - Uses `ROUND_HALF_UP` and quantizes to exactly two decimal places, matching its documented commercial-rounding rule.

- **`report.total_value()`**
  - Correctly applies the discount and its per-item two-decimal rounding before multiplying by quantity, consistent with “after per-item discounts.”
  - Preserves `Decimal` arithmetic.

- **`report.low_stock()`**
  - Correctly uses strict comparison (`< threshold

### Tool call: read_file
{"file_path": "workspace/inventory/export.py", "offset": 0, "limit": 100}

### Tool result
@@ lines 1-16 of 16 @@
"""Export helpers."""
from .pricing import parse_price


def to_csv_row(item):
    """Format one item as a CSV row: name,price,qty (price with 2 decimals).

    A name that contains a comma or a double quote is wrapped in double quotes,
    and every double quote inside it is doubled (RFC 4180).
    """
    name = item["name"]
    if "," in name or '"' in name:
        name = f'"{name.replace(chr(34), chr(34) * 2)}"'

    price = parse_price(item["price"])
    return f"{name},{price:.2f},{item['qty']}"

### Tool call: write_file
{"file_path": "workspace/inventory/export.py", "content": "\"\"\"Export helpers.\"\"\"\nfrom .pricing import parse_price\n\n\ndef to_csv_row(item):\n    \"\"\"Format one item as a CSV row: name,price,qty (price with 2 decimals).\n\n    A name that contains a comma or a double quote is wrapped in double quotes,\n    and every double quote inside it is doubled (RFC 4180).\n    \"\"\"\n    name = item[\"name\"]\n    if any(character in name for character in ',\"\\r\\n'):\n        name = f'\"{name.replace(chr(34), chr(34) * 2)}\"'\n\n    price = parse_price(item[\"price\"])\n    return f\"{name},{price:.2f},{item['qty']}\"\n"}

### Tool result
Updated file /workspace/inventory/export.py

### Tool call: execute
{"command": "cd workspace && python -m pytest tests -q && python - <<'PY'\nfrom decimal import Decimal\nfrom inventory.export import to_csv_row\nfrom inventory.pricing import apply_discount, parse_price\nfrom inventory.report import low_stock\n\nassert parse_price('(12.00)') == Decimal('-12.00')\nassert apply_discount(Decimal('10.05'), 10) == Decimal('9.05')\nassert low_stock([{'name': 'beta', 'qty': 4}, {'name': 'Alpha', 'qty': 5}, {'name': 'zeta', 'qty': 1}], 5) == ['beta', 'zeta']\nassert to_csv_row({'name': 'A, \"B\"', 'price': '$1,299.5', 'qty': 2}) == '\"A, \"\"B\"\"\",1299.50,2'\nassert to_csv_row({'name': 'a\\nb', 'price': '1', 'qty': 1}) == '\"a\\nb\",1.00,1'\nPY", "timeout": 120}

### Tool result
......                                                                   [100%]
6 passed in 0.01s

[Command succeeded with exit code 0]

### Assistant
Implemented the documented inventory behaviors:

- `pricing.py`: supports comma-separated and accounting-negative prices; discounts now round with `ROUND_HALF_UP`.
- `report.py`: low-stock results are strictly below the threshold and sorted case-insensitively.
- `export.py`: CSV names are correctly escaped and quoted when necessary.

All tests pass (`6 passed`), including additional checks for the documented edge cases.