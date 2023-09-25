def hex_to_rgb(value: str):
    value = value.lstrip('#')
    return tuple(int(value[i:i+2], 16) for i in (0, 2, 4))


def calculate_center(size1, size2):
    return (
        size1[0]/2 - size2[0]/2,
        size1[1]/2 - size2[1]/2
    )
