from game.world.managers.maps.Cell import Cell, CellKey
from game.world.managers.maps.Constants import CELL_SIZE
from game.world.managers.maps.MapHelpers import MapHelpers
from utils.constants.MiscCodes import ObjectTypes


class GridManager(object):
    def __init__(self, active_cell_callback, map_id, instance_id=0):
        self.map_id = map_id
        self.instance_id = instance_id
        self.cells = [[None for r in range(0, 256)] for c in range(0, 256)]
        self.active_cell_callback = active_cell_callback

    def add_or_get(self, world_object, store=False):
        cell_key = GridManager.get_cell_key(world_object.location.x, world_object.location.y, self.map_id)
        if not self.cells[cell_key.x][cell_key.y]:
            self.cells[cell_key.x][cell_key.y] = Cell(self.active_cell_callback, cell_key)

        if store:
            self.cells[cell_key.x][cell_key.y].add(self, world_object)

        return self.cells[cell_key.x][cell_key.y]

    def update_object(self, world_object, old_grid_manager):
        cell_key = GridManager.get_cell_key(world_object.location.x, world_object.location.y, world_object.map_)

        if cell_key != world_object.current_cell:
            if world_object.current_cell:
                if old_grid_manager == self:
                    print('Removing from current grid manager.')
                    self.remove_object(world_object, notify=False)
                else:
                    print('Removing from old grid manager.')
                    old_grid_manager.remove_object(world_object, notify=True)

            # If the new cell already exists, add this world object.
            if self.cells[cell_key.x][cell_key.y]:
                self.cells[cell_key.x][cell_key.y].add(self, world_object)
            # Create the new cell and add the world object.
            else:
                self.add_or_get(world_object, store=True)

            # Update old GridManager with the old CellKey.
            if old_grid_manager != self and world_object.current_cell:
                old_grid_manager.update_players(world_object)

            # Update world_object cell.
            world_object.current_cell = cell_key

            # Update new GridManager with the new CellKey.
            self.update_players(world_object)

            world_object.on_cell_change()

    def update_players(self, world_object):
        for cell in list(self.get_surrounding_cells_by_object(world_object)):
            cell.update_players()

    def remove_object(self, world_object, notify=False):
        if self.cells[world_object.current_cell.x][world_object.current_cell.y]:
            self.cells[world_object.current_cell.x][world_object.current_cell.y].remove(self, world_object)
            if notify:
                self.update_players(world_object)

    def is_active_cell(self, cell_key):
        return self.cells[cell_key.x][cell_key.y] and self.cells[cell_key.x][cell_key.y].has_players()

    # TODO: Should cleanup loaded tiles for deactivated cells.
    def deactivate_cells(self):
        pass

    def get_surrounding_cell_keys(self, world_object, vector=None):
        if not vector:
            vector = world_object.location
        near_cell_keys = set()

        x = MapHelpers.get_tile_x(vector.x, CELL_SIZE, 128)
        y = MapHelpers.get_tile_y(vector.y, CELL_SIZE, 128)

        # Quadrants.
        # | x | x | x |
        # | x | P | x |
        # | x | x | x |
        for i in range(-1, 1):
            for j in range(-1, 1):
                if -1 < x + i < 256 and -1 < y + j < 256:
                    if self.cells[x + i][y + j] and self.cells[x + i][y + j]:
                        near_cell_keys.add(CellKey(x=x + i, y=y + j, map_=self.map_id))
                    if self.cells[x - i][y - j] and self.cells[x - i][y - j]:
                        near_cell_keys.add(CellKey(x=x - i, y=y - j, map_=self.map_id))
                    if self.cells[x - i][y + j] and self.cells[x - i][y + j]:
                        near_cell_keys.add(CellKey(x=x - i, y=y + j, map_=self.map_id))
                    if self.cells[x + i][y - j] and self.cells[x + i][y - j]:
                        near_cell_keys.add(CellKey(x=x + i, y=y - j, map_=self.map_id))

        return near_cell_keys

    def get_surrounding_cells_by_cell(self, cell):
        return self.get_surrounding_cells_by_location(0, 0, cell.key)

    def get_surrounding_cells_by_object(self, world_object):
        vector = world_object.location
        return self.get_surrounding_cells_by_location(vector.x, vector.y)

    def get_surrounding_cells_by_location(self, x, y, cell_key=None):
        near_cells = set()

        x = MapHelpers.get_tile_x(x, CELL_SIZE, 128)
        y = MapHelpers.get_tile_y(y, CELL_SIZE, 128)

        if cell_key:
            x = cell_key.x
            y = cell_key.y

        # Quadrants.
        # | x | x | x |
        # | x | P | x |
        # | x | x | x |
        for i in range(-1, 1):
            for j in range(-1, 1):
                if -1 < x + i < 256 and -1 < y + j < 256:
                    if self.cells[x + i][y + j] and self.cells[x + i][y + j]:
                        near_cells.add(self.cells[x + i][y + j])
                    if self.cells[x - i][y - j] and self.cells[x - i][y - j]:
                        near_cells.add(self.cells[x - i][y - j])
                    if self.cells[x - i][y + j] and self.cells[x - i][y + j]:
                        near_cells.add(self.cells[x - i][y + j])
                    if self.cells[x + i][y - j] and self.cells[x + i][y - j]:
                        near_cells.add(self.cells[x + i][y - j])

        return near_cells

    def send_surrounding(self, packet, world_object, include_self=True, exclude=None, use_ignore=False):
        for cell in self.get_surrounding_cells_by_object(world_object):
            cell.send_all(packet, source=None if include_self else world_object, exclude=exclude, use_ignore=use_ignore)

    def send_surrounding_in_range(self, packet, world_object, range_, include_self=True, exclude=None,
                                  use_ignore=False):
        for cell in self.get_surrounding_cells_by_object(world_object):
            cell.send_all_in_range(
                packet, range_, world_object, include_self, exclude, use_ignore)

    def get_surrounding_objects(self, world_object, object_types):
        surrounding_objects = [{}, {}, {}]
        for cell in self.get_surrounding_cells_by_object(world_object):
            if ObjectTypes.TYPE_PLAYER in object_types:
                surrounding_objects[0] = {**surrounding_objects[0], **cell.players}
            if ObjectTypes.TYPE_UNIT in object_types:
                surrounding_objects[1] = {**surrounding_objects[1], **cell.creatures}
            if ObjectTypes.TYPE_GAMEOBJECT in object_types:
                surrounding_objects[2] = {**surrounding_objects[2], **cell.gameobjects}

        return surrounding_objects

    def get_surrounding_players(self, world_object):
        return self.get_surrounding_objects(world_object, [ObjectTypes.TYPE_PLAYER])[0]

    def get_surrounding_units(self, world_object, include_players=False):
        object_types = [ObjectTypes.TYPE_PLAYER, ObjectTypes.TYPE_UNIT] if include_players else [ObjectTypes.TYPE_UNIT]
        res = self.get_surrounding_objects(world_object, object_types)
        if include_players:
            return res[0], res[1]
        else:
            return res[1]

    def get_surrounding_units_by_location(self, vector, range_, include_players=False):
        units = [{}, {}]
        for cell in self.get_surrounding_cells_by_location(vector.x, vector.y):
            for guid, creature in list(cell.creatures.items()):
                if creature.location.distance(vector) <= range_:
                    units[0][guid] = creature
            if not include_players:
                continue
            for guid, player in list(cell.players.items()):
                if player.location.distance(vector) <= range_:
                    units[1][guid] = player
        return units

    def get_surrounding_gameobjects(self, world_object):
        return self.get_surrounding_objects(world_object, [ObjectTypes.TYPE_GAMEOBJECT])[2]

    def get_surrounding_player_by_guid(self, world_object, guid):
        for p_guid, player in list(self.get_surrounding_players(world_object).items()):
            if p_guid == guid:
                return player
        return None

    def get_surrounding_unit_by_guid(self, world_object, guid, include_players=False):
        surrounding_units = self.get_surrounding_units(world_object, include_players)
        if include_players:
            for p_guid, player in list(surrounding_units[0].items()):
                if p_guid == guid:
                    return player

        creature_dict = surrounding_units[1] if include_players else surrounding_units
        for u_guid, unit in list(creature_dict.items()):
            if u_guid == guid:
                return unit

        return None

    def get_surrounding_gameobject_by_guid(self, world_object, guid):
        for g_guid, gameobject in list(self.get_surrounding_gameobjects(world_object).items()):
            if g_guid == guid:
                return gameobject
        return None

    @staticmethod
    def get_cell_key(x, y, map_):
        x = MapHelpers.get_tile_x(x, CELL_SIZE, 128)
        y = MapHelpers.get_tile_y(y, CELL_SIZE, 128)
        return CellKey(x=x, y=y, map_=map_)

    def get_cells(self):
        return self.cells

    def update_creatures(self):
        for x in range(0, 256):
            for y in range(0, 256):
                if self.cells[x][y] and self.cells[x][y].has_players():
                    for guid, creature in list(self.cells[x][y].creatures.items()):
                        creature.update()

    def update_gameobjects(self):
        for x in range(0, 256):
            for y in range(0, 256):
                if self.cells[x][y] and self.cells[x][y].has_players():
                    for guid, gameobject in list(self.cells[x][y].gameobjects.items()):
                        gameobject.update()
