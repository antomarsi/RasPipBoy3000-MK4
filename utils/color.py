def hex_to_rgb(value: str, use_float: bool = False) -> tuple:
    value = value.lstrip('#')
    channels = (int(value[i:i+2], 16) for i in (0, 2, 4))
    if use_float:
        return tuple(c / 255 for c in channels)
    return tuple(channels)
