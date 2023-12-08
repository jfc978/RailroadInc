# -*- coding: utf-8 -*-
"""
Santorini Machine
Initializes all code related to the AI 

@author: Owner
"""
import numpy as np
from NN_AI_Interface import RailAIInterface
from move_prediction import PolicyNetwork
from move_selection import ValueNetwork
import random


class GameAI():
    def __init__(self, gameobj, training = True):
        #construct prediction network
        self.network = PolicyNetwork();
        #construct value network
        self.value_net = ValueNetwork();
        #start game environment
        self.game = gameobj;
        self.policy_moves = [];
        self.value_moves = [];
        self.policy_decision = [];
        self.policy_index = [];
        self.final_score = 0;
        self.training_proportion = 0.20; #number of states to train on
        #allow training
        self.isTrain = training;
        #flag for no legal moves
        self.stall = False;
        return;
        
    def load_models(self, path):
        value_path = path + "/value_net";
        policy_path = path + "/policy_net";
        self.value_net.load(value_path);
        self.network.load(policy_path);
        return;
        
    def save_models(self, path):
        value_path = path + "/value_net";
        policy_path = path + "/policy_net";
        
        self.value_net.save(value_path);
        self.network.save(policy_path);
        return [value_path, policy_path];
    
    def takeTurn(self):
        turnFlag = False;
        while turnFlag is False:
            [turnFlag,final_state,best_move_order,best_placements] = self.game.startSearch(self.network.predict,self.value_net.predict)

        
        self.game.takeTurn(final_state);
        for move in best_move_order:
            self.policy_decision.append(move[1]);
            self.policy_moves.append(move[0]);
            self.policy_index.append(move[3]);
            self.value_moves.append(move[2]);
        self.final_score = self.game.calculatedScore(self.game.game.getBoard());
        return best_move_order, best_placements;
    
    def predictMove(self, boardState):
        #return a list of weights for all possible moves
        return np.squeeze(self.network.predict(boardState));
    
    def move(self,boardState):
        self.game.board = boardState;
        return;
        
    def receiveMove(self,boardState):
        self.game.updateBoard(boardState);
        return;
        
    def evaluateWinLoss(self, boardState):
        if(self.stall == True):
            return -1;
        else:
            return self.game.score_final_position();
    
    def startGame(self):
        self.game.restart_game();
        return;
        
    def setLearningRate(self, lr):
        self.network.setLearningRate(lr);
        self.value_net.setLearningRate(lr);
    
        
    def updateNetworks(self, win_value):
        if(self.isTrain):
            print('Training Network')
            #only update policy network on wins
            for x in range(int(len(self.policy_moves)*self.training_proportion+1)):
                i = random.randint(0,len(self.policy_moves)-1);
                print(i)
                
                policy_index_num = np.nonzero(self.policy_index[i][0])[0][0];
                updated_policy = self.policy_decision[i];
                updated_policy[policy_index_num] = self.final_score;
                updated_policy = updated_policy/sum(updated_policy);
                
                #self.network.update(self.policy_moves[i],np.transpose(updated_policy))
                self.value_net.update(self.value_moves[i],self.final_score)
        return;
        
    def updateValueNetwork(self, board, value):
        self.value_net.update(board,value);
        return;
        
    def updatePredictionNetwork(self, boardState, values):
        self.network.update(boardState, values)
        return;

        
if __name__ == '__main__':
    print('Start');
    gameob = RailAIInterface();
    ai = GameAI(gameob);
    x = ai.takeTurn();
    print("Finished")
    
    

        