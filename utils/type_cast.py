def str_to_float(val: str) -> float:
    """Converts a string to a float, handling commas and empty strings."""
    try:
        if not val:
            return 0.0
        return float(val.replace(",", ""))
    except ValueError:
        raise ValueError(f"invalid value type: {val}")
