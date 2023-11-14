# -*- coding: utf-8 -*-
"""
Created on Sun Apr 23 17:00:01 2023

@author: James
"""

import os
from os.path import dirname, abspath
import numpy as np
import random
from rail_tile_manager import railroadTileManager, railroadTile

class RailroadInc:
    def __init__(self, playerColor = 0):
        # define basic structures
        self.rails = np.zeros((7*3,7*3,1), dtype=bool);
        self.roads = np.zeros((7*3,7*3,1), dtype=bool);
        self.remaining_tiles = np.zeros((7,7,1), dtype=bool);
        

        self.remaining_spaces = 7*7;
        self.remaining_turns = 7;
                
        self.legal_tiles = self.generateBoard();
        self.tile_system = railroadTileManager();
            
    def disectBoard(self, boardSpace):
        #player one
        rails = boardSpace[:,:,0];
        roads = boardSpace[:,:,1];
        
        return [rails, roads];
    
    def generateBoard(self):
        legal_tiles = np.zeros((7,7,1), dtype=bool);
        #top roads
        legal_tiles[1,0,0] = True;
        legal_tiles[5,0,0] = True;
        #bottom roads
        legal_tiles[1,6,0] = True;
        legal_tiles[5,6,0] = True;
        #left roads
        legal_tiles[0,3,0] = True;
        #right roads
        legal_tiles[6,3,0] = True;
        
        #top rails
        legal_tiles[3,0,1] = True;
        #bottom rails
        legal_tiles[3,6,1] = True;
        #left rails
        legal_tiles[0,1,1] = True;
        legal_tiles[0,5,1] = True;
        #right rails
        legal_tiles[6,1,1] = True;
        legal_tiles[6,5,1] = True;
        
        return legal_tiles;
    
    def placeTile(self,tile,position):
        self.tile_system.useTile(tile);
        
        #deconstruct position
        x_pos = position[0];
        y_pos = position[1];
        
        self.remaining_tiles[x_pos,y_pos] = False;
        

if __name__ == "__main__":
    tile_set = railroadTileManager();
    rolled_tiles = tile_set.rollTiles();
    for tile in rolled_tiles:
        print(tile.ID);
        print(tile.tileShape[:,:,0]);
        print(tile.tileShape[:,:,1]);
        

            
            