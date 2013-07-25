import math

REF_X = 95.047
REF_Y = 100.000
REF_Z = 108.883

def xyz_color_norm(color):
    """Helper function for normalizing color during conversion to XYZ"""

    if color > 0.04045:
        color = math.pow(((color + 0.055) / 1.055), 2.4)
    else:
        color = color / 12.92

    return color * 100

def rgb_to_xyz(ro, go, bo):
    """"Converts given RGB color to XYZ"""

    r, g, b = [
        xyz_color_norm(x / 255.0)
        for x in (ro, go, bo)
    ]

    return (
        r * 0.4124 + g * 0.3576 + b * 0.1805,
        r * 0.2126 + g * 0.7152 + b * 0.0722,
        r * 0.0193 + g * 0.1192 + b * 0.9505
    )

def laab_color_norm(c):
    """Helper function for normalizing color during conversion to L*ab"""

    if c > 0.008856:
        return math.pow(c, 1 / 3.0)
    else:
        return (7.787 * c) + (16 / 116.0)


def xyz_to_laab(x, y, z):
    """Converts given XYZ color to L*ab"""

    var_x = laab_color_norm(x / REF_X)
    var_y = laab_color_norm(y / REF_Y)
    var_z = laab_color_norm(z / REF_Z)

    return (
        (116 * var_y) - 16,
        500 * (var_x - var_y),
        200 * (var_y - var_z)
    )

def cie_lab_2hue(a, b):
    bias = 0

    if a >= 0 and b == 0:
        return 0
    if a < 0 and b == 0:
        return 180
    if a == 0 and b > 0:
        return 90
    if a == 0 and b < 0:
        return 270
    if a > 0 and b > 0:
        bias = 0
    if a < 0:
        bias = 180
    if a > 0 and b < 0:
        bias = 360

    return (math.degrees(math.atan(b / float(a))) + bias)

def color_diff_rgb(c1, c2, whtl=1, whtc=1, whth=1):
    """Converts colors from RGB to XYZ before passing them to color_diff_xyz"""

    c1 = rgb_to_xyz(*c1)
    c2 = rgb_to_xyz(*c2)

    return color_diff_xyz(c1, c2, whtl, whtc, whth)

def color_diff_xyz(c1, c2, whtl=1, whtc=1, whth=1):
    """Converts colors from XYZ to L*ab before passing them to color_diff_laab"""

    c1 = xyz_to_laab(*c1)
    c2 = xyz_to_laab(*c2)

    return color_diff_laab(c1, c2, whtl, whtc, whth)

def color_diff_laab(c1, c2, whtl=1, whtc=1, whth=1):
    """Computes difference between L*ab colors with CIEDE2000 algorithm"""

    ciea1, cieb1, ciel1 = c1
    ciea2, cieb2, ciel2 = c2

    xC1 = math.sqrt(ciea1 * ciea1 + cieb1 * cieb1)
    xC2 = math.sqrt(ciea2 * ciea2 + cieb2 * cieb2)
    xCX = (xC1 + xC2) / 2.0
    xGX = 0.5 * (1 - math.sqrt(math.pow(xCX, 7) / (math.pow(xCX, 7) + math.pow(25, 7))))
    xNN = (1 + xGX) * ciea1
    xC1 = math.sqrt(xNN * xNN + cieb1 * cieb1)
    xH1 = cie_lab_2hue(xNN, cieb1)
    xNN = (1 + xGX) * ciea2
    xC2 = math.sqrt(xNN * xNN + cieb2 * cieb2)
    xH2 = cie_lab_2hue(xNN, cieb2)
    xDL = ciel2 - ciel1
    xDC = xC2 - xC1

    if xC1 * xC2 == 0:
        xDH = 0
    else:
        xNN = round(xH2 - xH1, 12)

        if abs(xNN) <= 180:
            xDH = xH2 - xH1
        elif xNN > 180:
            xDH = xH2 - xH1 - 360
        else:
            xDH = xH2 - xH1 + 360

    xDH = 2 * math.sqrt(xC1 * xC2) * math.sin(math.radians(xDH / 2.0))
    xLX = (ciel1 + ciel2) / 2.0
    xCY = (xC1 + xC2) / 2.0

    if xC1 * xC2 == 0:
        xHX = xH1 + xH2
    else:
        xNN = abs(round(xH1 - xH2, 12))
        if xNN > 180:
            if xH2 + xH1 < 360:
                xHX = xH1 + xH2 + 360
            else:
                xHX = xH1 + xH2 - 360
        else:
            xHX = xH1 + xH2
        xHX /= 2

    xTX = 1 - 0.17 * math.cos(math.radians(xHX - 30)) + 0.24 \
                * math.cos(math.radians(2 * xHX)) + 0.32 \
                * math.cos(math.radians(3 * xHX + 6)) - 0.20 \
                * math.cos(math.radians(4 * xHX - 63))

    xPH = 30 * math.exp(-((xHX - 275) / 25.0) * ((xHX - 275) / 25.0))
    xRC = 2 * math.sqrt(math.pow(xCY, 7) / (math.pow(xCY, 7) + math.pow(25, 7)))
    xSL = 1 + ((0.015 * ((xLX - 50) * (xLX - 50))) /
               math.sqrt(20 + ((xLX - 50) * (xLX - 50))))
    xSC = 1 + 0.045 * xCY
    xSH = 1 + 0.015 * xCY * xTX
    xRT = - math.sin(math.radians(2 * xPH)) * xRC
    xDL = xDL / (whtl * xSL)
    xDC = xDC / (whtc * xSC)
    xDH = xDH / (whth * xSH)

    return math.sqrt(math.pow(xDL, 2) + math.pow(xDC, 2) + math.pow(xDH, 2) + xRT * xDC * xDH)
