
import math


def deg2num(lat_deg, lon_deg, zoom):
    """Convert lat/lon to tile coordinates"""
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return (xtile, ytile)


def tile_to_quadkey(x, y, zoom):
    """Convert tile coordinates to quadkey"""
    quadkey = ""
    for i in range(zoom, 0, -1):
        digit = 0
        mask = 1 << (i - 1)
        if (x & mask) != 0:
            digit += 1
        if (y & mask) != 0:
            digit += 2
        quadkey += str(digit)
    return quadkey


def get_quadkeys_for_bbox(north, south, east, west, zoom):
    """Get all quadkeys that intersect with a bounding box"""
    """

    # example:
    # Westchester County approximate bounds
    # You might want to refine these bounds
    north = 41.37  # Northern border
    south = 40.85  # Southern border
    east = -73.45  # Eastern border
    west = -73.90  # Western border


    quadkeys = get_quadkeys_for_bbox(north, south, east, west, 9)
    print(f"Quadkeys for Westchester County at level 9:")
    for qk in sorted(quadkeys):
        print(qk)
    print(f"\nTotal quadkeys: {len(quadkeys)}")
    """
    min_x, max_y = deg2num(south, west, zoom)
    max_x, min_y = deg2num(north, east, zoom)

    quadkeys = []
    for x in range(min_x, max_x + 1):
        for y in range(min_y, max_y + 1):
            quadkey = tile_to_quadkey(x, y, zoom)
            quadkeys.append(quadkey)

    return quadkeys
