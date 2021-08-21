import math

from game.world.managers.maps.Constants import SIZE, RESOLUTION_ZMAP


class MapHelpers(object):
    @staticmethod
    def calculate_tile(x, y, resolution):
        x = MapHelpers.validate_map_coord(x)
        y = MapHelpers.validate_map_coord(y)
        map_tile_x = int(math.floor(32.0 - (x / SIZE)))
        map_tile_y = int(math.floor(32.0 - (y / SIZE)))
        tile_local_x = int(resolution * (32.0 - (x / SIZE) - map_tile_x))
        tile_local_y = int(resolution * (32.0 - (y / SIZE) - map_tile_y))
        return map_tile_x, map_tile_y, tile_local_x, tile_local_y


    @staticmethod
    def validate_map_coord(coord):
        if coord > 32.0 * SIZE:
            return 32.0 * SIZE
        elif coord < -32.0 * SIZE:
            return -32 * SIZE
        else:
            return coord

    @staticmethod
    def get_tile_x(x):
        tile_x = int(math.floor(32.0 - MapHelpers.validate_map_coord(x) / SIZE))
        return tile_x

    @staticmethod
    def get_tile_y(y):
        tile_y = int(math.floor(32.0 - MapHelpers.validate_map_coord(y) / SIZE))
        return tile_y

    @staticmethod
    def get_submap_tile_x(x):
        tile_x = int((RESOLUTION_ZMAP - 1) * (
                32.0 - MapHelpers.validate_map_coord(x) / SIZE - int(32.0 - MapHelpers.validate_map_coord(x) / SIZE)))

        return tile_x

    @staticmethod
    def get_submap_tile_y(y):
        tile_y = int((RESOLUTION_ZMAP - 1) * (
                32.0 - MapHelpers.validate_map_coord(y) / SIZE - int(32.0 - MapHelpers.validate_map_coord(y) / SIZE)))

        return tile_y