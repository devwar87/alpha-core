import math


class MapHelpers(object):
    @staticmethod
    def calculate_tile(x, y, size, resolution, offset):
        x = MapHelpers.validate_map_coord(x, size, offset)
        y = MapHelpers.validate_map_coord(y, size, offset)
        map_tile_x = int(math.floor(32.0 - (x / size)))
        map_tile_y = int(math.floor(32.0 - (y / size)))
        tile_local_x = int(resolution * (32.0 - (x / size) - map_tile_x))
        tile_local_y = int(resolution * (32.0 - (y / size) - map_tile_y))
        return map_tile_x, map_tile_y, tile_local_x, tile_local_y

    @staticmethod
    def validate_map_coord(coord, size, offset):
        if coord > offset * size:
            return offset * size
        elif coord < -offset * size:
            return -offset * size
        else:
            return coord

    @staticmethod
    def get_tile_x(x, size, offset):
        x = MapHelpers.validate_map_coord(x, size, offset)
        tile_x = int(math.floor(offset - x / size))
        return tile_x

    @staticmethod
    def get_tile_y(y, size, offset):
        y = MapHelpers.validate_map_coord(y, size, offset)
        tile_y = int(math.floor(offset - y / size))
        return tile_y

    @staticmethod
    def get_submap_tile_x(x, size, resolution, offset):
        x = MapHelpers.validate_map_coord(x, size, offset)
        tile_x = int((resolution - 1) * (offset - x / size - int(offset - x / size)))

        return tile_x

    @staticmethod
    def get_submap_tile_y(y, size, resolution, offset):
        y = MapHelpers.validate_map_coord(y, size, offset)
        tile_y = int((resolution - 1) * (offset - y / size - int(offset - y / size)))

        return tile_y
