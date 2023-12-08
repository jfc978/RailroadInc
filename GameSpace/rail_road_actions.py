# -*- coding: utf-8 -*-
"""
Created on Sun Nov 19 14:05:58 2023

@author: James
"""

from nn_representation import NNRailRoadInterpreter, TileManagerInterface
from rail_tile_manager import railroadTileManager
import numpy as np


class RailRoadActions:
    #class to handle actual logic of placing pieces
    def __init__(self,boardSpace = None):
        if(boardSpace is not None):
            self.board_rep = NNRailRoadInterpreter(boardSpace);
        else:
            self.board_rep = NNRailRoadInterpreter();
        self.tile_manager = railroadTileManager();
        self.tile_converter = TileManagerInterface(self.board_rep,self.tile_manager);
        self.tiled_board = self.create_empty_board();
        
    def create_empty_board(self):
        base = [];
        for x_idx in range(7):
            temp = [];
            for y_idx in range(7):
                temp.append([self.tile_manager.emptyTile(),0]);
            base.append(temp);
                
        return base
        
    def find_legal_placements(self,tile):
        #return x,y,and rotation of legal placement options
        tile_rotations = [];
        for u_idx in range(len(self.board_rep.rotation_order)):
            tile_rotations.append(self.tile_converter.decompose_tile(tile, u_idx));
        legal_placements = self.board_rep.find_legal_placements(tile_rotations);
        
        return legal_placements;
    
    def find_legal_placements_vector(self,tile):
        legal_placement_list = self.find_legal_placements(tile);
        vectored_output = self.board_rep.vectorize_placements(legal_placement_list);
        pos = np.nonzero(vectored_output[0])[0]
        for n in pos:
            [x,y,u] = self.board_rep.get_index_move(n);
            if [x,y,u] not in legal_placement_list:
                print('Error');

        
        return vectored_output
        
        
    def place_piece(self,x,y,tile,rotation):
        connections = self.tile_converter.decompose_tile(tile, rotation);
        self.board_rep.place_piece(x,y,connections);
        self.tiled_board[x][y] = [tile,rotation];
                
        #update available tiles
        self.board_rep.update_available_positions();
        return;
        
    def place_piece_new_board(self,boardSpace,x,y,tile,rotation):
        connections = self.tile_converter.decompose_tile(tile, rotation);
        new_board = NNRailRoadInterpreter(boardSpace);
        new_board.place_piece(x,y,connections);
                
        #update available tiles
        new_board.update_available_positions();
        return new_board.representation.board;
       
    def rollTiles(self):
        return self.tile_manager.rollTiles();
    
    def updateBoard(self,boardSpace):
        self.board_rep.representation.board = boardSpace;
        self.board_rep.update_available_positions();
        return
        
    def getBoard(self):
        return np.copy(self.board_rep.representation.board);
        
        
    def moveFromIndex(self,index,tile,update = False):
        [x,y,u] = self.board_rep.get_index_move(index);
        if(update):
            self.place_piece(x, y, tile, u);
            ret_board = self.getBoard();
        else:
            new_board = self.place_piece_new_board(self.getBoard(), x, y, tile, u)
            ret_board = new_board;
        return [ret_board,x,y,u];

    def vectorize_board(self,board_rep,tile):
        board = board_rep.getBoard();
        connections = self.tile_converter.decompose_tile(tile, 0);
        stacked_board = board_rep.get_board_with_tile(connections);
        return stacked_board
      
    ## Scoring
    def __count_connected_exits(self,board_rep):
        exits_point_lookup = [0,4,8,12,16,20,24,28,32];

        # return length of longest path
        points = 0;
        rail_networks = self.board_rep.search_connected_exits('rail');
        for nets in rail_networks:
            points += exits_point_lookup[nets];
        road_networks = self.board_rep.search_connected_exits('road');
        for nets in road_networks:
            points += exits_point_lookup[nets];
        
        return points;
        
        
    def __count_longest_path(self,board_rep):
        rail_length = self.board_rep.search_longest_path('rail');
        road_length = self.board_rep.search_longest_path('road');
        
        return [rail_length,road_length]
    
    def __count_center_points(self,board_rep):
        tiles = self.board_rep.tiles;
        center = tiles[2:5,2:5];
        return sum(sum(center));
        
    def __count_blocked_tiles(self,board_rep):
        return self.board_rep.search_blocked_paths('rail') + self.board_rep.search_blocked_paths('road');
        
    def get_board_statistics(self):
        # get representative statistics to allow easier production of heuristics
        # get longest roads, rails, number of remaining tiles, number of "connected tiles", number of tiles in "center", number of blocked tiles, number of failed connections
        [rail_l,road_l] = self.__count_longest_path(self.board_rep);
        center = self.__count_center_points(self.board_rep);
        blocked = self.__count_blocked_tiles(self.board_rep);
        exits = self.__count_connected_exits(self.board_rep);
        
        print('Longest Road : ', road_l);
        print('Longest Rail : ', rail_l);
        print('Tiles in Center : ', center);
        print('Connected Exits : ', exits)
        print('Blocked Tiles : ', blocked)
        print('Sum Score : ', road_l + rail_l + center + exits - blocked);
        
        return [rail_l, road_l, center, exits, blocked]
        
    def score_final_position(self,board_rep):
        [rail_l,road_l] = self.__count_longest_path(self.board_rep);
        center = self.__count_center_points(self.board_rep);
        blocked = self.__count_blocked_tiles(self.board_rep);
        exits = self.__count_connected_exits(self.board_rep);
        return rail_l + road_l + center - blocked + exits;    
        
    def score_intermediate_position(self,board_rep):
        [rail_l,road_l] = self.__count_longest_path(self.board_rep);
        center = self.__count_center_points(self.board_rep);
        blocked = self.__count_blocked_tiles(self.board_rep);
        exits = self.__count_connected_exits(self.board_rep);
        return rail_l + road_l + center - (blocked*0.75) + (exits*5);
    
    def score_fast_position(self,board_rep):
        center = self.__count_center_points(self.board_rep);
        exits = self.__count_connected_exits(self.board_rep);
        return center + exits;
    
    def get_board_with_tile(self,board,tile):
        return self.board_rep.get_board_with_tile(board,self.tile_converter.decompose_tile(tile,0));
    
    def get_board_without_tile(self,board):
        return self.board_rep.get_board_without_tile(board);
    
if __name__ == "__main__":
    #start graph object
    graph = RailRoadActions();
    
    #generate tiles
    for n in range(8):
        rolled_tiles = graph.rollTiles();
        ntup = graph.find_legal_placements(rolled_tiles[0]);
        
        move = ntup[0];
        graph.place_piece(move[0],move[1], rolled_tiles[0], move[2])
        
    
    tile_set = railroadTileManager();
    rolled_tiles = tile_set.rollTiles();
    for tile in rolled_tiles:
        print(tile.ID);
        print(tile.tileShape[:,:,0]);
        print(tile.tileShape[:,:,1]);