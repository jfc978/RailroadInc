# -*- coding: utf-8 -*-
"""
Santorini Machine
Initializes all code related to the AI 

@author: Owner
"""
import numpy as np
from game_environment import Santorini
from move_prediction import PolicyNetwork
from move_selection import ValueNetwork
from tensorflow import keras
import random
import matplotlib.pyplot as plt


class GameAI():
    def __init__(self, playerColor, training = True):
        #construct prediction network
        self.network = PolicyNetwork();
        #construct value network
        self.value_net = ValueNetwork();
        #start game environment
        self.game = Santorini(playerColor);
        self.moves = [];
        self.expected_values = []
        #set player color for current game
        self.player = playerColor;
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
        boardState = self.game.board;
        move_prediction = self.predictMove(boardState);
        best_move = self.hybridSelect(move_prediction, boardState);
        if(best_move is not None):
            self.move(best_move);
        return best_move;
    
    def predictMove(self, boardState):
        #return a list of weights for all possible moves
        return np.squeeze(self.network.predict(boardState));
      
    def hybridSelect(self, prediction, boardState):
        #reduce to legal moves
        [legalVector, legalMoves] = self.game.generateLegalMoves(boardState,self.player);
        prediction[~legalVector] = 0;
        
        #normalize weights accordingly
        prediction = prediction/sum(prediction);
        
        #perform search
        value_prediction = self.value_net.evaluateMoves(prediction, boardState, legalMoves)
        [move_choice, values, graphed] = self.value_net.selectMove(value_prediction, self.player,\
                                                   boardState, self.game.generateLegalMoves,\
                                                       self.evaluateWinLoss, self.game.moveFromIndex);
            
        if(move_choice is not None):
            #update policy network
            counter = 0;
            win_value = np.zeros((1,1600));
            for i,x in enumerate(legalVector):
                if x:
                    win_value[0][i] = values[counter][0];
                    counter += 1;
                
            win_value = win_value/(np.sum(win_value,1)[0]);
            self.expected_values.append(win_value);
            self.moves.append(move_choice);
        #plot moves
        ucbs = graphed[0];
        sub_ucbs = graphed[1];
        fig = plt.figure();
        plt.bar(range(0,len(ucbs)),ucbs);
        plt.show();
        fig = plt.figure();
        plt.bar(range(0,len(sub_ucbs)),sub_ucbs);
        plt.show();
        
        return move_choice;
        
    
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
            return self.game.determineWinLoss(boardState,self.player);
    
    def startGame(self, playerColor):
        self.player = playerColor;
        self.game = Santorini(playerColor);
        self.moves = [];
        self.expected_values = [];
        self.stall = False;
        return;
        
    def setLearningRate(self, lr):
        self.network.setLearningRate(lr);
        self.value_net.setLearningRate(lr);
        return;
    
    def updatePlayer(self, playerColor):
        self.game.updatePlayerColor(playerColor);
        self.player = playerColor;
        return;
        
    def updateNetworks(self, win_value):
        if(self.isTrain):
            print('Training Network')
            #only update policy network on wins
            for x in range(int(len(self.moves)/8)+1):
                i = random.randint(0,len(self.moves)-1);
                print(i)
                if(win_value == 1):
                    self.network.update(self.moves[i],self.expected_values[i])
                        
                #update value network with win_value
                norm_value = (win_value + 1)/2;
                self.value_net.update(self.moves[i],[norm_value, 1-norm_value])
        return;
        
    def updateValueNetwork(self, board, value):
        self.value_net.update(board,value);
        return;
        
    def updatePredictionNetwork(self, boardState, values):
        self.network.update(boardState, values)
        return;


        
if __name__ == '__main__':
    player = 0;
    ai = GameAI(player);
    x = ai.takeTurn();
    print("Finished")
    
    

        