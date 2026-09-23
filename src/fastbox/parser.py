import json
import math
import os
from typing import Any

Coordinate = tuple[float, float]


def _validate_coordinate(coord: Any, name: str) -> Coordinate:
    """Validate that coord is a 2-element sequence of finite numbers."""
    if not isinstance(coord, (list, tuple)) or len(coord) != 2:
        raise ValueError(f"Invalid coordinate for {name}: expected [x, y], got {coord!r}")

    x, y = coord
    # Reject booleans because bool is a subclass of int in Python
    if isinstance(x, bool) or isinstance(y, bool):
        raise ValueError(f"Invalid coordinate for {name}: coordinates cannot be booleans")

    if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
        raise ValueError(
            f"Invalid coordinate for {name}: expected numeric values, got ({type(x).__name__}, {type(y).__name__})"
        )

    if math.isnan(x) or math.isnan(y) or math.isinf(x) or math.isinf(y):
        raise ValueError(f"Invalid coordinate for {name}: coordinates must be finite numbers")

    return (float(x), float(y))


def _normalize_locations(
    raw_collection: Any, entity_type: str
) -> dict[str, Coordinate]:
    """
    Normalize warehouses or agents into a dictionary of {id: (x, y)}.
    Supports both dict format (test cases) and list-of-dicts format (base_case).
    """
    if raw_collection is None:
        raise ValueError(f"'{entity_type}' cannot be null")

    normalized: dict[str, Coordinate] = {}

    if isinstance(raw_collection, dict):
        if not raw_collection:
            raise ValueError(f"'{entity_type}' collection cannot be empty")

        for item_id, loc in raw_collection.items():
            if not isinstance(item_id, str) or not item_id.strip():
                raise ValueError(
                    f"{entity_type.capitalize()} ID must be a non-empty string, got {item_id!r}"
                )
            normalized[item_id] = _validate_coordinate(loc, f"{entity_type} '{item_id}'")

    elif isinstance(raw_collection, list):
        if not raw_collection:
            raise ValueError(f"'{entity_type}' collection cannot be empty")

        for item in raw_collection:
            if not isinstance(item, dict):
                raise ValueError(
                    f"Expected each {entity_type} item to be a dictionary, got {type(item).__name__}"
                )
            if "id" not in item:
                raise ValueError(f"{entity_type.capitalize()} item missing 'id' field")
            item_id = item["id"]
            if not isinstance(item_id, str) or not item_id.strip():
                raise ValueError(
                    f"{entity_type.capitalize()} ID must be a non-empty string, got {item_id!r}"
                )
            if item_id in normalized:
                raise ValueError(f"Duplicate {entity_type} ID: '{item_id}'")
            if "location" not in item:
                raise ValueError(f"{entity_type.capitalize()} '{item_id}' missing 'location' field")

            normalized[item_id] = _validate_coordinate(item["location"], f"{entity_type} '{item_id}'")

    else:
        raise ValueError(
            f"'{entity_type}' must be a list or dictionary, got {type(raw_collection).__name__}"
        )

    return normalized


def parse_data(raw_data: Any) -> dict[str, Any]:
    """
    Validate and normalize delivery system data from raw JSON structures.

    Returns a normalized dictionary:
    {
        'warehouses': {'W1': (x, y), ...},
        'agents': {'A1': (x, y), ...},
        'packages': [{'id': 'P1', 'warehouse': 'W1', 'destination': (x, y)}, ...]
    }
    """
    if not isinstance(raw_data, dict):
        raise ValueError(f"Top-level JSON structure must be a dictionary, got {type(raw_data).__name__}")

    for field in ("warehouses", "agents", "packages"):
        if field not in raw_data:
            raise ValueError(f"Missing required top-level field: '{field}'")

    warehouses = _normalize_locations(raw_data["warehouses"], "warehouse")
    agents = _normalize_locations(raw_data["agents"], "agent")

    raw_packages = raw_data["packages"]
    if not isinstance(raw_packages, list):
        raise ValueError(f"'packages' must be a list, got {type(raw_packages).__name__}")
    if not raw_packages:
        raise ValueError("'packages' collection cannot be empty")

    packages: list[dict[str, Any]] = []
    seen_package_ids: set[str] = set()

    for pkg in raw_packages:
        if not isinstance(pkg, dict):
            raise ValueError(f"Package item must be a dictionary, got {type(pkg).__name__}")

        if "id" not in pkg:
            raise ValueError("Package item missing 'id' field")
        pkg_id = pkg["id"]
        if not isinstance(pkg_id, str) or not pkg_id.strip():
            raise ValueError(f"Package ID must be a non-empty string, got {pkg_id!r}")
        if pkg_id in seen_package_ids:
            raise ValueError(f"Duplicate package ID: '{pkg_id}'")
        seen_package_ids.add(pkg_id)

        # Normalize warehouse reference ('warehouse' or 'warehouse_id')
        warehouse_ref = pkg.get("warehouse") or pkg.get("warehouse_id")
        if not warehouse_ref or not isinstance(warehouse_ref, str) or not warehouse_ref.strip():
            raise ValueError(
                f"Package '{pkg_id}' missing valid warehouse reference ('warehouse' or 'warehouse_id')"
            )
        if warehouse_ref not in warehouses:
            raise ValueError(
                f"Package '{pkg_id}' references unknown warehouse '{warehouse_ref}'"
            )

        if "destination" not in pkg:
            raise ValueError(f"Package '{pkg_id}' missing 'destination' field")
        destination = _validate_coordinate(pkg["destination"], f"package '{pkg_id}' destination")

        normalized_pkg: dict[str, Any] = {
            "id": pkg_id,
            "warehouse": warehouse_ref,
            "destination": destination,
        }
        # Preserve any additional metadata keys present in the package
        for key, value in pkg.items():
            if key not in ("id", "warehouse", "warehouse_id", "destination"):
                normalized_pkg[key] = value

        packages.append(normalized_pkg)

    return {
        "warehouses": warehouses,
        "agents": agents,
        "packages": packages,
    }


def load_data(filepath: str | os.PathLike) -> dict[str, Any]:
    """Load JSON file from disk and return normalized delivery data."""
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            raw_data = json.load(f)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON in '{filepath}': {exc}") from exc

    return parse_data(raw_data)
