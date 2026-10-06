### Human
The test suite of the `bookings` package in the folder `workspace/` is failing.

Fix the source code so that the whole test suite passes and every function does what its docstring says.
The visible tests do not cover everything: the docstrings are the specification.
Do not modify the existing files in `tests/`.
Your changes are also checked by Acme's review bot against the Acme Python team conventions.

When you are done, reply with a short summary of what you changed and why.


### Tool call: ls
{"path": "workspace"}

### Tool result
['/workspace/CHANGELOG.md', '/workspace/README.md', '/workspace/bookings/', '/workspace/tests/']

### Tool call: ls
{"path": "workspace/bookings"}

### Tool result
['/workspace/bookings/__init__.py', '/workspace/bookings/__pycache__/', '/workspace/bookings/billing.py', '/workspace/bookings/calendar_export.py', '/workspace/bookings/schedule.py', '/workspace/bookings/timeutil.py']

### Tool call: read_file
{"file_path": "workspace/bookings/billing.py", "offset": 0, "limit": 400}

### Tool call: read_file
{"file_path": "workspace/bookings/calendar_export.py", "offset": 0, "limit": 400}

### Tool call: read_file
{"file_path": "workspace/bookings/schedule.py", "offset": 0, "limit": 500}

### Tool call: read_file
{"file_path": "workspace/bookings/timeutil.py", "offset": 0, "limit": 400}

### Tool call: read_file
{"file_path": "workspace/README.md", "offset": 0, "limit": 400}

### Tool call: read_file
{"file_path": "workspace/tests", "offset": 0, "limit": 20}

### Tool result
@@ lines 1-11 of 11 @@
"""Billing rules."""


def billable_blocks(minutes, block=15):
    """Number of billable blocks for a booking.

    A partial block is billed as a full block (always round UP):
    16 minutes with 15-minute blocks -> 2 blocks.
    `minutes` must be >= 0; a negative value raises ValueError.
    """
    return round(minutes / block)

### Tool result
@@ lines 1-7 of 7 @@
"""Calendar export."""
from .timeutil import parse_duration


def slot_end(start_minute, duration_text):
    """Minute of the day at which a slot ends."""
    return start_minute + parse_duration(duration_text)

### Tool result
@@ lines 1-17 of 17 @@
"""Schedule helpers."""
from .timeutil import parse_duration


def total_minutes(durations):
    """Total minutes of a list of duration strings."""
    return sum(parse_duration(d) for d in durations)


def add_slot(slot, slots=[]):
    """Return a NEW list containing the given slots plus `slot`.

    Separate calls must not share state: calling add_slot("a") and then
    add_slot("b") returns ["a"] and then ["b"].
    """
    slots.append(slot)
    return slots

### Tool result
@@ lines 1-19 of 19 @@
"""Time helpers for the bookings package."""
import re


def parse_duration(text):
    """Convert a duration string to whole minutes (int).

    Supported formats:
      "1h30m" -> 90
      "2h"    -> 120
      "45m"   -> 45
      "1:30"  -> 90
      "45"    -> 45    # a bare number means minutes
    Surrounding whitespace is ignored.
    """
    m = re.fullmatch(r"(\d+)h(\d+)m", text.strip())
    if not m:
        raise ValueError(f"bad duration: {text!r}")
    return int(m.group(1)) * 60 + int(m.group(2))

### Tool result
@@ lines 1-5 of 5 @@
# bookings

Small package. Run the tests from the `workspace/` folder:

    cd workspace && python -m pytest tests -q

### Tool result
Error: File '/workspace/tests' not found

### Tool call: ls
{"path": "workspace/tests"}

### Tool call: read_file
{"file_path": "workspace/bookings/timeutil.py", "offset": 0, "limit": 200}

### Tool call: read_file
{"file_path": "workspace/bookings/__init__.py", "offset": 0, "limit": 200}

### Tool call: read_file
{"file_path": "workspace/CHANGELOG.md", "offset": 0, "limit": 400}

### Tool result
['/workspace/tests/__pycache__/', '/workspace/tests/test_bookings.py']

### Tool result
@@ lines 1-19 of 19 @@
"""Time helpers for the bookings package."""
import re


def parse_duration(text):
    """Convert a duration string to whole minutes (int).

    Supported formats:
      "1h30m" -> 90
      "2h"    -> 120
      "45m"   -> 45
      "1:30"  -> 90
      "45"    -> 45    # a bare number means minutes
    Surrounding whitespace is ignored.
    """
    m = re.fullmatch(r"(\d+)h(\d+)m", text.strip())
    if not m:
        raise ValueError(f"bad duration: {text!r}")
    return int(m.group(1)) * 60 + int(m.group(2))

### Tool result
@@ lines 1-1 of 1 @@
__version__ = "1.4.2"

### Tool result
@@ lines 1-6 of 6 @@
# Changelog

## Unreleased

## 1.4.2
- initial import

### Tool call: read_file
{"file_path": "workspace/tests/test_bookings.py", "offset": 0, "limit": 400}

### Tool result
@@ lines 1-15 of 15 @@
from bookings.billing import billable_blocks
from bookings.schedule import add_slot, total_minutes


def test_total_minutes_mixed_formats():
    assert total_minutes(["1h30m", "2h"]) == 210


def test_billable_blocks_rounds_up():
    assert billable_blocks(20) == 2
    assert billable_blocks(45) == 3


def test_add_slot_single_call():
    assert add_slot("a") == ["a"]

### Tool call: grep
{"pattern": "parse_duration", "path": "workspace", "glob": "*", "output_mode": "content", "max_count": 50}

### Tool result
/workspace/bookings/calendar_export.py:
  2: from .timeutil import parse_duration
  7:     return start_minute + parse_duration(duration_text)
/workspace/bookings/schedule.py:
  2: from .timeutil import parse_duration
  7:     return sum(parse_duration(d) for d in durations)
/workspace/bookings/timeutil.py:
  5: def parse_duration(text):

### Tool call: execute
{"command": "python -c \"from pathlib import Path; print(repr(Path('workspace/bookings/timeutil.py').read_text()))\" && cd workspace && python -m pytest tests -q", "timeout": 120}

### Tool result
'"""Time helpers for the bookings package."""\nimport re\n\n\ndef parse_duration(text):\n    """Convert a duration string to whole minutes (int).\n\n    Supported formats:\n      "1h30m" -> 90\n      "2h"    -> 120\n      "45m"   -> 45\n      "1:30"  -> 90\n      "45"    -> 45    # a bare number means minutes\n    Surrounding whitespace is ignored.\n    """\n    m = re.fullmatch(r"(\\d+)h(\\d+)m", text.strip())\n    if not m:\n        raise ValueError(f"bad duration: {text!r}")\n    return int(m.group(1)) * 60 + int(m.group(2))\n'
FF.                                                                      [100%]
=================================== FAILURES ===================================
_______________________ test_total_minutes_mixed_formats _______________________

>   ???

C:\Users\PC\Desktop\lab\lab_20\K4-DAY20-MULTIAGENTS-LeDuyQuan-2A202602731\tasks\code-eval\workspace\tests\test_bookings.py:6: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
bookings/schedule.py:7: in total_minutes
    return sum(parse_duration(d) for d in durations)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
bookings/schedule.py:7: in <genexpr>
    return sum(parse_duration(d) for d in durations)
               ^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

text = '2h'

    def parse_duration(text):
        """Convert a duration string to whole minutes (int).
    
        Supported formats:
          "1h30

### Tool call: edit_file
{"file_path": "workspace/bookings/timeutil.py", "old_string": "\"\"\"Time helpers for the bookings package.\"\"\"\nimport re\n\n\ndef parse_duration(text):\n    \"\"\"Convert a duration string to whole minutes (int).\n\n    Supported formats:\n      \"1h30m\" -> 90\n      \"2h\"    -> 120\n      \"45m\"   -> 45\n      \"1:30\"  -> 90\n      \"45\"    -> 45    # a bare number means minutes\n    Surrounding whitespace is ignored.\n    \"\"\"\n    m = re.fullmatch(r\"(\\d+)h(\\d+)m\", text.strip())\n    if not m:\n        raise ValueError(f\"bad duration: {text!r}\")\n    return int(m.group(1)) * 60 + int(m.group(2))\n", "new_string": "\"\"\"Time helpers for the bookings package.\"\"\"\nimport re\n\n\n_DURATION_PATTERN = re.compile(\n    r\"(?:((?P<hours>\\d+))h(?:(?P<hour_minutes>\\d+))?m?|\"\n    r\"(?P<clock_hours>\\d+):(?P<clock_minutes>\\d+)|\"\n    r\"(?P<minutes>\\d+)m?)\"\n)\n\n\ndef parse_duration(text):\n    \"\"\"Convert a duration string to whole minutes (int).\n\n    Supported formats:\n      \"1h30m\" -> 90\n      \"2h\"    -> 120\n      \"45m\"   -> 45\n      \"1:30\"  -> 90\n      \"45\"    -> 45    # a bare number means minutes\n    Surrounding whitespace is ignored.\n    \"\"\"\n    if not isinstance(text, str):\n        raise ValueError(f\"bad duration: {text!r}\")\n\n    match = _DURATION_PATTERN.fullmatch(text.strip())\n    if match is None:\n        raise ValueError(f\"bad duration: {text!r}\")\n\n    if match[\"hours\"] is not None:\n        return int(mat

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/bookings/timeutil.py'

### Tool call: edit_file
{"file_path": "workspace/bookings/timeutil.py", "old_string": "_DURATION_PATTERN = re.compile(\n    r\"(?:((?P<hours>\\d+))h(?:(?P<hour_minutes>\\d+))?m?|\"\n    r\"(?P<clock_hours>\\d+):(?P<clock_minutes>\\d+)|\"\n    r\"(?P<minutes>\\d+)m?)\"\n)\n", "new_string": "_DURATION_PATTERN = re.compile(\n    r\"(?:\"\n    r\"(?P<hours>\\d+)h(?:(?P<hour_minutes>\\d+)m)?|\"\n    r\"(?P<clock_hours>\\d+):(?P<clock_minutes>\\d+)|\"\n    r\"(?P<minutes>\\d+)m?\"\n    r\")\"\n)\n", "replace_all": false}

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/bookings/timeutil.py'

### Tool call: edit_file
{"file_path": "workspace/bookings/billing.py", "old_string": "    return round(minutes / block)", "new_string": "    if minutes < 0:\n        raise ValueError(\"minutes must be non-negative\")\n    if block <= 0:\n        raise ValueError(\"block must be positive\")\n    return (minutes + block - 1) // block", "replace_all": false}

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/bookings/billing.py'

### Tool call: edit_file
{"file_path": "workspace/bookings/schedule.py", "old_string": "def add_slot(slot, slots=[]):\n    \"\"\"Return a NEW list containing the given slots plus `slot`.\n\n    Separate calls must not share state: calling add_slot(\"a\") and then\n    add_slot(\"b\") returns [\"a\"] and then [\"b\"].\n    \"\"\"\n    slots.append(slot)\n    return slots", "new_string": "def add_slot(slot, slots=None):\n    \"\"\"Return a NEW list containing the given slots plus `slot`.\n\n    Separate calls must not share state: calling add_slot(\"a\") and then\n    add_slot(\"b\") returns [\"a\"] and then [\"b\"].\n    \"\"\"\n    if slots is None:\n        slots = []\n    return [*slots, slot]", "replace_all": false}

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/bookings/schedule.py'

### Tool call: edit_file
{"file_path": "workspace/bookings/billing.py", "old_string": "\"\"\"Billing rules.\"\"\"\n\n\ndef billable_blocks(minutes, block=15):", "new_string": "\"\"\"Billing rules.\"\"\"\nimport math\n\n\ndef billable_blocks(minutes, block=15):", "replace_all": false}

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/bookings/billing.py'

### Tool call: edit_file
{"file_path": "workspace/bookings/billing.py", "old_string": "    if minutes < 0:\n        raise ValueError(\"minutes must be non-negative\")\n    if block <= 0:\n        raise ValueError(\"block must be positive\")\n    return (minutes + block - 1) // block", "new_string": "    if minutes < 0:\n        raise ValueError(\"minutes must be non-negative\")\n    if block <= 0:\n        raise ValueError(\"block must be positive\")\n    return math.ceil(minutes / block)", "replace_all": false}

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/bookings/billing.py'

### Tool call: execute
{"command": "cd workspace && python -m pytest tests -q && python - <<'PY'\nfrom bookings.timeutil import parse_duration\nfrom bookings.billing import billable_blocks\nfrom bookings.schedule import add_slot\nassert [parse_duration(value) for value in ('1h30m', '2h', '45m', '1:30', '45', ' 2h ')] == [90, 120, 45, 90, 45, 120]\nfor value in ('', '1h30', '1:2:3', 'h', '1m2'):\n    try:\n        parse_duration(value)\n    except ValueError:\n        pass\n    else:\n        raise AssertionError(value)\nassert billable_blocks(16) == 2\ntry:\n    billable_blocks(-1)\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('negative minutes accepted')\noriginal = ['a']\nresult = add_slot('b', original)\nassert result == ['a', 'b'] and original == ['a']\nPY", "timeout": 120}

### Tool result
...                                                                      [100%]
3 passed in 0.01s

[Command succeeded with exit code 0]

### Assistant
Fixed the bookings utilities so documented behavior is implemented:

- Updated duration parsing to support all documented formats and whitespace handling.
- Corrected billable-block rounding, including negative-minute validation.
- Removed shared mutable state from `add_slot` and ensured it returns a new list.

All tests now pass.