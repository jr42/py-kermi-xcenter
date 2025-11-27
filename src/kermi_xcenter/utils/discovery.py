"""Device capability discovery utilities.

This module provides helper functions for saving, loading, and managing
discovered device capabilities. Capabilities can be saved to JSON files
and reused across sessions to skip probing unavailable registers.
"""

import json
from pathlib import Path


def save_capabilities(capabilities: dict[str, bool], file_path: str | Path) -> None:
    """Save discovered capabilities to a JSON file.

    Args:
        capabilities: Dictionary mapping register names to availability
        file_path: Path to save the JSON file

    Example:
        >>> caps = await heat_pump.discover_capabilities()
        >>> save_capabilities(caps, "heat_pump_caps.json")
    """
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "w") as f:
        json.dump(capabilities, f, indent=2, sort_keys=True)


def load_capabilities(file_path: str | Path) -> dict[str, bool]:
    """Load capabilities from a JSON file.

    Args:
        file_path: Path to the JSON file

    Returns:
        Dictionary mapping register names to availability

    Raises:
        FileNotFoundError: If file does not exist
        json.JSONDecodeError: If file contains invalid JSON

    Example:
        >>> caps = load_capabilities("heat_pump_caps.json")
        >>> hp = HeatPump(client, capabilities=caps)
    """
    with open(file_path) as f:
        caps: dict[str, bool] = json.load(f)
        return caps


def merge_capabilities(*capability_dicts: dict[str, bool]) -> dict[str, bool]:
    """Merge multiple capability dictionaries with OR logic.

    If a register appears as True in any dictionary, it will be True in the result.
    This is useful for combining capabilities from multiple device instances.

    Args:
        *capability_dicts: Variable number of capability dictionaries to merge

    Returns:
        Merged dictionary where a register is True if True in any input

    Example:
        >>> caps1 = {"temp": True, "pressure": False}
        >>> caps2 = {"temp": True, "pressure": True, "flow": False}
        >>> merged = merge_capabilities(caps1, caps2)
        >>> # Result: {"temp": True, "pressure": True, "flow": False}
    """
    result: dict[str, bool] = {}

    for cap_dict in capability_dicts:
        for name, available in cap_dict.items():
            # OR logic: if available in any dict, mark as available
            result[name] = result.get(name, False) or available

    return result
