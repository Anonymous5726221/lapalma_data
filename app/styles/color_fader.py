from skimage.color import lab2rgb
from numpy import asarray, linspace, cos, sin, vstack, ones, radians


def lch_to_lab(L, c, h):
    """
    L is lightness, 0 (black) to 100 (white)
    c is chroma, 0-100 or more
    h is hue, in degrees, 0 = red, 90 = yellow, 180 = green, 270 = blue
    """
    a = c * cos(radians(h))
    b = c * sin(radians(h))
    return L, a, b


def lab_color_scale(lutsize=256, hue=0, chroma=50, rot=1/4, l=None):
    """
    List of rgb colors created by drawing arcs through the L*c*h*
    (lightness, chroma, hue) cylindrical coordinate color space.
    Parameters
    ----------
    lutsize : int
        The number of individual colors. (Default is 256.)
    hue : float
        Hue angle at which the colormap starts, in degrees.  Default 0 is
        reddish.
    chroma : float
        Chroma radius for the colormap path.  If chroma is 0, the colormap is
        grayscale.  If chroma is too large, the colors will exceed the RGB
        gamut and produce ugly bands.  Since the RGB cube is pointy at the
        black and white ends, this always clips somewhat.
    rot : float
        Number of hue rotations.  If 0, hue is constant and only lightness is
        varied. If 1, all hues are passed through once.  If 2, circle through
        all hues twice, etc.
        For counterclockwise rotation, make the value negative
    l : float/list
        Lightness value for constant-lightness (isoluminant) colormaps. If
        not specified, lightness is varied from 0 at minimum to 100 at maximum.
    Returns
    -------
    RGBs : list
        The resulting colormap object
    """
    hue = linspace(hue, hue + rot * 360, lutsize)

    if l is None:
        L = linspace(0, 100, lutsize)
    elif hasattr(l, "__len__"):
        if len(l) == 2:
            L = linspace(l[0], l[1], lutsize)
        elif len(l) == 1:
            L = l * ones(lutsize)
        elif len(l) == lutsize:
            L = asarray(l)
        else:
            raise ValueError('lightness argument not understood')
    else:
        L = l * ones(lutsize)

    L, a, b = lch_to_lab(L, chroma, hue)

    Lab = vstack([L, a, b])

    RGBs = [tuple(map(lambda x: x*255, lab2rgb(i))) for i in Lab.T]

    return [f"rgb({r}, {g}, {b})" for r, g, b in RGBs]


def custom_discrete_sequence(n):

    return lab_color_scale(lutsize=n, hue=306, rot=140/360, chroma=80, l=[16, 93])
