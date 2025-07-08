def str_to_float(val: str) -> float:
    try:
        value: int

        if not val:
            return 0.0
        if val.__class__ == str:
            value = val.replace(",", "")
        elif val.__class__ == int:
            value = val
        elif val.__class__ == float:
            return val

        return float(value)
    except ValueError as e:
        raise ValueError(f"invalid value type: {val}")
