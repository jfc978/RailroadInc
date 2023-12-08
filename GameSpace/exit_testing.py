# -*- coding: utf-8 -*-
"""
Created on Wed Nov 22 15:43:11 2023

@author: James
"""

from railroad_inc_graphics import emptyGraphics
from rail_road_actions import RailRoadActions
from rail_tile_manager import railroadTileManager



def place_piece(x,y,u,tile,game,graphics):
    game.place_piece(x,y, tile, u)
    tile_space = game.tile_manager.rotateTile(tile,u);
    #tile_shape = self.game.place_piece(x, y, random_dice[rand_tile], rotation)
    graphics.assignSpace(y,x,tile_space);
        
    return 

if __name__ == "__main__":
    game = RailRoadActions();
    tiles = railroadTileManager();
    graphics = emptyGraphics();
    
    straight_road = tiles.dice1[0];
    right_road = tiles.dice1[2];
    
    print('placing tiles')
    place_piece(3,0,0,straight_road,game,graphics)
    place_piece(0,1,1,straight_road,game,graphics)
    place_piece(1,1,1,straight_road,game,graphics)
    place_piece(2,1,1,straight_road,game,graphics)
    place_piece(3,1,1,right_road,game,graphics)
    print('checking tiles')

    game.get_board_statistics()