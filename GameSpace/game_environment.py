# -*- coding: utf-8 -*-
"""
Santorini Environment
Defines board space and updates board with moves
Encodes game rules

@author: Owner
"""
import os
from os.path import dirname, abspath
import numpy as np
import random

class RailroadInc:
    def __init__(self, playerColor = 0):
        # define basic structures
        self.rails = np.zeros((7*3,7*3,1), dtype=bool);
        self.roads = np.zeros((7*3,7*3,1), dtype=bool);
        self.tiles = np.zeros((7,7,2), dtype=bool);
        

        self.remaining_spaces = 7*7;
        self.tile_queue = [];
        self.board = self.generateBoard();
            
    def disectBoard(self, boardSpace):
        #player one
        rails = boardSpace[:,:,1];
        roads = boardSpace[:,:,2];
        
        return [rails, roads];
        
    def constructBoard(self, rails, roads, tiles):
        boardSpace = np.concatenate(rails,roads,
                                    np.ones((7*3,7*3,1),dtype=bool),np.pad(tiles,((0,16),(0,16))),dtype=bool);
        return boardSpace;

    def generateBoard(self):
        tiles = self.tiles;
        #set available rail tiles
        tiles[3,0,0] = 1;
        tiles[3,6,0] = 1;
        tiles[0,1,0] = 1;
        tiles[0,5,0] = 1;
        tiles[6,0,0] = 1;
        tiles[6,5,0] = 1;
        
        #set available road tiles
        tiles[1,0,1] = 1;
        tiles[5,0,1] = 1;
        tiles[1,6,1] = 1;
        tiles[5,6,1] = 1;
        tiles[0,3,0] = 1;
        tiles[6,3,0] = 1;
        
        boardSpace = np.concatenate(self.rails,self.roads,
                            np.ones((7*3,7*3,1),dtype=bool),np.pad(tiles,((0,16),(0,16))),dtype=bool);

        return boardSpace;
            
    def generateLegalMoves(self, boardSpace, build=True):
        # generate a mask vector of every possible move
        # 0 for illegal, 1 for legal, 1x(7x7x4) 
        # also generate a list of boardspaces to pass to monte carlo tree search

        # produce indices
        # output_size = 196; #[(7x7)tiles]*[(4)rotation]*[(2)reversed]
        output_size = (7,7,4,2)
        pos_x_idx = np.prod(output_size[1:])
        pos_y_idx = np.prod(output_size[2:])
        rot_d_idx = 1 #may need to be 1

        # move representation vector
        legalityVector = np.zeros(np.prod(output_size),dtype=bool);
        
        # find starting positions of playerTurn's pieces
        [rails, roads, tiles] = self.disectBoard(boardSpace)
        tiles = tiles[1:7][1:7][1]        
        
        availablePositions = np.where(tiles == 1);

        
        
        # search for legal moves
        legalSpaces = [];
        validation = [];
        for w in [0,1]: #worker positions 
            w_x = workerPositions[0][w];
            w_y = workerPositions[1][w];
            w_z = workerPositions[2][w];
            

            index = w_x * pos_x_idx + w_y * pos_y_idx + move_direction * move_d_idx + build_direction * build_d_idx;
            legalityVector[index] = 1;
            
            # construct boardSpace
            if(build):
                #move in direction and height specified by (move_d)
                moveSpace = np.copy(playerSpace);
                moveSpace[w_x, w_y, w_z] = 0;
                
                moveSpace[check_x, check_y, building_height + 1] = 1;
                
                #build in appropriate location
                newBuildSpace = np.copy(buildSpace);
                newBuildSpace[check_x + b_r,check_y + b_t, build_height+1] = 1;
                
                #print("Found legal move at (", w_x, w_y,\
                #      ") to (",check_x,check_y, building_height+1, \
                #      "), then build at (", check_x + b_r,check_y + b_t,\
                #      build_height + 1,")");
                
                #reconstruct board
                if(playerTurn == 0):
                    newBoardSpace = self.constructBoard(moveSpace, playerTwo, newBuildSpace, 0);
                else:
                    newBoardSpace = self.constructBoard(playerOne, moveSpace, newBuildSpace, 1);
                legalSpaces.append(newBoardSpace);
                            
        return [legalityVector, legalSpaces];
    
    def moveFromIndex(self, boardSpace, index, playerTurn):
        output_size = (7,7,4,2)
        direction_map = ([-1,-1], [-1,0], [-1,1], [0,-1], [0,1], [1,-1], [1,0], [1,1]);
        
        #modulo reduction
        build_d = int(index % np.prod(output_size[:]));
        index -= build_d;
        
        move_d = index % np.prod(output_size[2:]);
        index -= move_d;
        move_d = int(move_d / np.prod(output_size[3:]));
        
        pos_y = index % np.prod(output_size[1:]);
        index -= pos_y;
        pos_y = int(pos_y / np.prod(output_size[2:]));
        
        pos_x = int(index / np.prod(output_size[1:]));
       
        #separate board space
        [playerOne, playerTwo, buildSpace] = self.disectBoard(boardSpace)
        
        if(playerTurn==0):
            playerSpace = playerOne;
        else:
            playerSpace = playerTwo;
        
        #move in direction and height specified by (move_d)
        pos_z = max(max(np.where(buildSpace[pos_x,pos_y,:]==1)),default = -1);
        if(not playerSpace[pos_x,pos_y,pos_z+1] == 1):
            raise ValueError("Player piece does not exist at expected location");
        playerSpace[pos_x,pos_y,pos_z+1] = 0;
        
        pos_x += direction_map[move_d][0];
        pos_y += direction_map[move_d][1];
        pos_z = max(max(np.where(buildSpace[pos_x,pos_y,:]==1)),default = -1);
        playerSpace[pos_x,pos_y,pos_z+1] = 1;
        
        #build in appropriate location
        pos_x += direction_map[build_d][0];
        pos_y += direction_map[build_d][1];
        pos_z = max(max(np.where(buildSpace[pos_x,pos_y,:]==1)),default = -1);
        buildSpace[pos_x,pos_y,pos_z+1] = 1;
        
        #reconstruct board
        if(playerTurn == 0):
            boardSpace = self.constructBoard(playerSpace, playerTwo, buildSpace, 0);
        else:
            boardSpace = self.constructBoard(playerOne, playerSpace, buildSpace, 1);
        
        return boardSpace;
      
    def updateBoard(self, boardSpace):
        boardSpace[:,:,15] = self.current_player;
        self.board = boardSpace;
        return boardSpace;
        
    def determineWinLoss(self, boardSpace, player):
        [playerOne, playerTwo, buildSpace] = self.disectBoard(boardSpace);
        
        playerOneWin = max(np.array(np.where(playerOne == 1))[2])==3;
        playerTwoWin = max(np.array(np.where(playerTwo == 1))[2])==3;
        
        if(playerOneWin and not player):
            return 1;
        if(playerTwoWin and player):
            return 1;
        if(playerOneWin and player):
            return -1;
        if(playerTwoWin and not player):
            return -1;
        return 0;
        
class NoMoves(Exception):
    pass;
    


if __name__ == '__main__':
    game = Santorini();
    board = game.generateBoard();
    [legalVector,legalSpace] = game.generateLegalMoves(board,0);
    
    win = game.determineWinLoss(board,0)
    next_move = random.choice(np.where(legalVector==1));
    next_move = random.choice(next_move);
    next_move = game.moveFromIndex(game.constructBoard(game.player_one,game.player_two, game.pieces,0), next_move, 0);
    