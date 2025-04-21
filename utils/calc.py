def hex_to_rgb(value: str, use_float = False):
    value = value.lstrip('#')
    if use_float:
        return list(int(value[i:i+2], 16)/255 for i in (0, 2, 4))
    else:
        return tuple(int(value[i:i+2], 16) for i in (0, 2, 4))


def calculate_center(size1, size2):
    return (
        size1[0]/2 - size2[0]/2,
        size1[1]/2 - size2[1]/2
    )
