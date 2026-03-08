

import re
from typing import Any


def _scalar_or_list(values):
    """Return scalar for single-value lists, otherwise list, or None."""
    if values is None:
        return None
    return values if len(values) > 1 else values[0]


def _parse_style_kv(values, argname: str) -> dict[str, str]:
    """Parse repeated key=value style args into a dict."""
    if not values:
        return {}
    style = {}
    for item in values:
        if "=" not in item:
            raise ValueError(f"{argname} expects key=value entries, got: '{item}'")
        key, value = item.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            raise ValueError(f"{argname} has empty key in '{item}'")
        style[key] = value
    return style


def parse_bool(value: Any) -> bool:
    """Parse bool-like CLI values."""
    if isinstance(value, bool):
        return value
    sval = str(value).strip().lower()
    if sval in {"1", "true", "t", "yes", "y", "on"}:
        return True
    if sval in {"0", "false", "f", "no", "n", "off"}:
        return False
    raise ValueError(f"invalid boolean value: {value}")


def parse_node_mask(value: Any) -> bool | tuple[bool, bool, bool]:
    """Parse node-mask CLI values.

    Accepts:
    - bool-like strings: true/false, 1/0, yes/no
    - 3-value binary tuple/list text: (1,0,1), [1, 0, 1], 1,0,1
    """
    if isinstance(value, bool):
        return value
    sval = str(value).strip()

    # bool mode
    try:
        return parse_bool(sval)
    except ValueError:
        pass

    # tuple/list mode
    if (sval.startswith("(") and sval.endswith(")")) or (sval.startswith("[") and sval.endswith("]")):
        sval = sval[1:-1].strip()
    parts = [i for i in re.split(r"[\s,]+", sval) if i]
    if len(parts) != 3:
        raise ValueError(
            "invalid node mask. Use true/false or a 3-value binary tuple/list like '(1,0,1)'."
        )
    if any(i not in {"0", "1"} for i in parts):
        raise ValueError("node-mask tuple/list values must be binary 0/1.")
    return tuple(bool(int(i)) for i in parts)


