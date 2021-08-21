from utils.constants.MiscCodes import ObjectTypes
from typing import NamedTuple


class Cell_Key(NamedTuple):
    x: int
    y: int
    cx: int
    cy: int
    map_: int


class Cell(object):
    def __init__(self, active_cell_callback, key, gameobjects=None, creatures=None, players=None):
        self.active_cell_callback = active_cell_callback
        self.key = key
        self.gameobjects = gameobjects
        self.creatures = creatures
        self.players = players

        if not gameobjects:
            self.gameobjects = dict()
        if not creatures:
            self.creatures = dict()
        if not players:
            self.players = dict()

    def has_players(self):
        return len(self.players) > 0

    def add(self, grid_manager, world_object):
        # Update world_object cell so the below messages affect the new cell surroundings.
        world_object.current_cell = self.key
        if world_object.get_type() == ObjectTypes.TYPE_PLAYER:
            self.players[world_object.guid] = world_object
        elif world_object.get_type() == ObjectTypes.TYPE_UNIT:
            self.creatures[world_object.guid] = world_object
        elif world_object.get_type() == ObjectTypes.TYPE_GAMEOBJECT:
            self.gameobjects[world_object.guid] = world_object

        # A world_object entered this cell, notify players.
        self.update_players()

        # Always trigger cell changed event for players.
        if world_object.get_type() == ObjectTypes.TYPE_PLAYER:
            self.active_cell_callback(world_object)

    # Make each player update its surroundings, adding or removing world objects as needed.
    def update_players(self):
        for player in list(self.players.values()):
            player.update_surrounding_on_me()

    def remove(self, world_object):
        if world_object.get_type() == ObjectTypes.TYPE_PLAYER:
            self.players.pop(world_object.guid, None)
        elif world_object.get_type() == ObjectTypes.TYPE_UNIT:
            self.creatures.pop(world_object.guid, None)
        elif world_object.get_type() == ObjectTypes.TYPE_GAMEOBJECT:
            self.gameobjects.pop(world_object.guid, None)

        self.update_players()

    def send_all(self, packet, source=None, exclude=None, use_ignore=False):
        for guid, player_mgr in list(self.players.items()):
            if player_mgr.online:
                if source and player_mgr.guid == source.guid:
                    continue
                if exclude and player_mgr.guid in exclude:
                    continue
                if use_ignore and source and player_mgr.friends_manager.has_ignore(source.guid):
                    continue

                player_mgr.enqueue_packet(packet)

    def send_all_in_range(self, packet, range_, source, include_self=True, exclude=None, use_ignore=False):
        if range_ <= 0:
            self.send_all(packet, source, exclude)
        else:
            for guid, player_mgr in list(self.players.items()):
                if player_mgr.online and player_mgr.location.distance(source.location) <= range_:
                    if not include_self and player_mgr.guid == source.guid:
                        continue
                    if use_ignore and player_mgr.friends_manager.has_ignore(source.guid):
                        continue

                    player_mgr.enqueue_packet(packet)
