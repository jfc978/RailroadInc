# -*- coding: utf-8 -*-
"""
Created on Sat Nov 18 19:05:33 2023

@author: James
"""
import numpy as np
import math
from rail_road_actions import RailRoadActions

class RailAIInterface:
    #class handle overhead of interfacing with Monte Carlo Search Method
    def __init__(self, training = True):
        # Game Representation
        self.game = RailRoadActions();
        self.game_rep = self.game.board_rep;
        self.current_tiles = self.game.tile_manager.remainingTiles();
        self.remaining_turns = 8;
        self.search_depth = 2;
        self.search_width = 12;
        self.alpha = 0.01;
        self.expected_game_iters = 500;
        self.game_number = 0;

    def startSearch(self,prediction,evaluation):
        # recursive tree search for simple move generation
        available_tiles = self.game.tile_manager.rollTiles();
        moves_vector = [];
        placement_vector = [];
        while len(available_tiles) > 0:
            dup_tiles = available_tiles.copy();
            start_board = self.game.getBoard();
            [best_child,best_child_score,best_move,tile_selection,best_start,best_start_clear,prediction_vector] = self.completeRecursion(start_board,dup_tiles,0,evaluation,prediction);
            if(best_child is None):
                return [False,None,None,None];
            available_tiles.remove(tile_selection);
            self.game.updateBoard(best_child);
            
            moves_vector.append([best_start,prediction_vector,best_start_clear,self.onehot_move(best_move[0], best_move[1], best_move[2])]);
            placement_vector.append([best_move[0], best_move[1], best_move[2],tile_selection])
            
        final_board = best_child;
        return [True,final_board, moves_vector,placement_vector];
        
    def completeRecursion(self,boardSpace,available_tiles,depth,evaluator,predictor):
        best_child = None;
        best_child_score = -1;
        best_move = [0,0,0];
        chosen_tile = None;
        best_start = boardSpace;
        best_start_clear = None;
        prediction_vector = None;
        
        #in case of failure
        move_prediction = None;
        hybrid_score = -1;
        encoded_board = None;
        ss_child = None;
        ss_clear = False;
        ss_move = None;
        ss_score = 0;
        
        if(len(available_tiles) > 0 and depth < self.search_depth):
            current_game = RailRoadActions(np.copy(boardSpace));
            for tile in available_tiles:
                cur_tiles = available_tiles;
                cur_tiles.remove(tile);
                
                # get prediction vector
                [legal_vector] = current_game.find_legal_placements_vector(tile)
                encoded_board = current_game.get_board_with_tile(current_game.getBoard(),tile);
                move_prediction = legal_vector*np.random.normal(1,0.01,np.shape(legal_vector));
                #move_prediction = np.transpose(predictor(encoded_board));      
                #move_prediction[legal_vector == 0] = 0;
                move_prediction = move_prediction / sum(move_prediction);
                pred_priority = sorted(move_prediction,reverse=True);
                
                # evaluate top [search width] moves from prediction
                ss_child = None;
                ss_score = 0;
                search_width = min(self.search_width,len(np.nonzero(pred_priority)[0]))
                for target_pred in pred_priority[0:search_width]:
                    if(target_pred > 0):
                        [ss_board,x,y,u] = current_game.moveFromIndex(np.where(move_prediction == target_pred)[0][0],tile);
                        ss_clear_board = current_game.get_board_without_tile(ss_board);
                        eval_score = evaluator(ss_clear_board);
                        fast_score = self.calculatedScore(ss_board);
                        score = self.combineScores(eval_score,fast_score);
                        
                        if(score > ss_score):
                            ss_child = np.copy(ss_board);
                            ss_clear = np.copy(ss_clear_board);
                            ss_move = [x,y,u];
                            ss_score = np.copy(eval_score);
                
                
                [sub_child, sub_child_score,sub_child_move,a,b,c,d] = self.completeRecursion(np.copy(ss_child),cur_tiles,depth+1,evaluator,predictor)
                
                if(sub_child is not None):
                    #expensive evalute child
                    exp_score = self.calculatedScore(ss_child);
                    hybrid_score = self.combineScores(ss_score,exp_score);
                    hybrid_score = max(sub_child_score,hybrid_score);
                else:
                    exp_score = self.calculatedScore(ss_child);
                    hybrid_score = self.combineScores(ss_score,exp_score);
                    
                    
                if(hybrid_score > best_child_score):
                    best_child = np.copy(ss_child);
                    best_child_score = hybrid_score;
                    best_move = np.copy(ss_move);
                    chosen_tile = np.copy(tile);
                    best_start = np.copy(encoded_board);
                    best_start_clear = np.copy(ss_clear);
                    prediction_vector = np.copy(move_prediction);
                    
                
        return [best_child,best_child_score,best_move,chosen_tile,best_start,best_start_clear,prediction_vector]
        

    def takeTurn(self,boardSpace):
        self.game.updateBoard(boardSpace);
        self.remaining_turns -= 1;
        
    ## AI Commands
    def generateLegalMoves(self, boardSpace, turnNumber, build=True):
        #check for remaining tiles
        if(turnNumber > len(self.tile_manager.remainingTiles())):
            legalMoves = [];
            legalVector = [];
            nextTurn = [];
            return [legalMoves,legalVector,nextTurn];
        
        #next tile
        rolled_tiles = self.tile_manager.remainingTiles();
        
        
        #create NN_Interpretation Object
        
        
        #decode tile from board representation
        
        
       
        return [legalVector, legalMoves, nextTurn];
    
    def moveFromIndex(self, index, tile):
        boardSpace = self.game.moveFromIndex(index, tile);
        return boardSpace;
      
    def calculatedScore(self,boardSpace):
        if(boardSpace is None):
            return 0;
        return self.score_sigmoid(self.game.score_intermediate_position(boardSpace));
    
    def calculatedScoreFast(self,boardSpace):
        if(boardSpace is None):
            return 0;
        return self.score_sigmoid(self.game.score_fast_position(boardSpace));
        
    
    def onehot_move(self,x,y,z):
        return self.game.board_rep.vectorize_placements([[x,y,z]]);
    
    def exportRailsRoads(self):
        board = self.game.getBoard();
        rails = board[1:8,1:8,0];
        roads = board[1:8,1:8,1];
        return rails,roads;
    
    def isOver(self):
        return self.remaining_turns <= 0;
    
    def combineScores(self,nn,heuristic):
        return nn*(1-self.alpha) + heuristic*(self.alpha);
    
    def score_sigmoid(self,score):
        return 1 / (1 + math.exp(-(score-20)/20));
    
    def restart_game(self):
        self.game = RailRoadActions();
        self.game_rep = self.game.board_rep;
        self.remaining_turns = 8;
        self.update_alpha();
        return

    def update_alpha(self):
        self.game_number += 1;
        self.alpga = 1 / (1 + math.exp(-(self.game_number-(self.expected_game_iters/2))/((self.expected_game_iters/6))));


        
        
        
    """
        
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
        for u_idx in range(len(rotation_order)):
            tile_rotations.append(self.tile_converter.decompose_tile(tile, u_idx));
        legal_placements = self.board_rep.find_legal_placements(tile_rotations);
        
        return legal_placements;
    
    def find_legal_placements_vector(self,tile):
        legal_placement_list = self.find_legal_placements(tile);
        return self.board_rep.VectorizePlacements(legal_placement_list);
        
        
    def place_piece(self,x,y,tile,rotation):
        connections = self.tile_converter.decompose_tile(tile, rotation);
        self.board_rep.place_piece(x,y,connections);
        try:
            self.tiled_board[x][y] = [tile,rotation];
        except:
            print('error');
                
            
        
        #update available tiles
        
        
        return;
       
    def rollTiles(self):
        return self.tile_manager.rollTiles();

    def vectorize_board(self,board_rep,tile):
        board = board_rep.get_board();
        layered_tile = board_rep.encode_tile;
        stacked_board = board;
        stacked_board[17:18] = layered_tile;
        return stacked_board
    
    

        
    def score_final_position(self,board_rep):
        [rail_l,road_l] = self.__count_longest_path(self.board_rep);
        center = self.__count_center_points(self.board_rep);
        blocked = self.__count_blocked_tiles(self.board_rep);
        exits = self.__count_connected_exits(self.board_rep);
        return rail_l + road_l + center - blocked + sum(exits);    
        
    def score_intermediate_position(self,board_rep):
        [rail_l,road_l] = self.__count_longest_path(self.board_rep);
        center = self.__count_center_points(self.board_rep);
        blocked = self.__count_blocked_tiles(self.board_rep);
        exits = self.__count_connected_exits(self.board_rep);
        return rail_l + road_l + center - blocked + sum(exits);
    """
    
def dummy_prediction(boardSpace):
    predict = np.transpose(np.random.random((7*7*4,1)));
    return predict;

def dummy_score(boardSpace):
    predict = np.random.random();
    return predict;
    
    
if __name__ == "__main__":
    rai = RailAIInterface();
    rai.startSearch(dummy_prediction,dummy_score);