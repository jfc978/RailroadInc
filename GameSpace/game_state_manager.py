# -*- coding: utf-8 -*-
"""
Created on Tue May 23 23:56:35 2023

@author: James
"""

print('Loading Modules');

import time
import numpy as np
from app_scheme import App
from game_graphics_manager import gameGraphicsManager
from railroad_inc_sim import RailroadInc
from nn_representation import NNRailRoadInterpreter
from railroad_inc_graphics import emptyGraphics
from rail_road_AI import GameAI
from rail_road_actions import RailRoadActions
from NN_AI_Interface import RailAIInterface

print('Completed : Loading Modules');

class gameStateManager():
    def __init__(self,state_str):
        if(state_str == 'auto'):
            self.state = autoGameState(self);
        elif(state_str == 'interactive'):
            self.state = interactiveGameState(self);
        elif(state_str == 'ai_training'):
            self.state = AITrainingGameState(self);
        else:
            self.state = simulatedGameState_v2(self);

        return;
    
    def assignGraphicsManager(self,graphicsManager):
        self.graphicsManager = graphicsManager;
        self.state.graphicsManager = graphicsManager;
        return
    
    def checkProgram(self):
        if(hasattr(self,'kill_event')):
            return self.kill_event.is_set();
        else:
            return False;
    
    def setEvent(self,event):
        self.kill_event = event;
        
    def changeState(self,state):
        self.state = state
        return
    
    def runGame(self):
        self.state.startGame();
        return
    
    
class gameState():
    def __init__(self,gameManager):
        self.state = gameManager;
        self.graphicsManager = [];
        self.game = RailRoadActions();
        return;
        
    def startGame(self):
        pass;
    
    def iterateGame(self):
        pass;
        
class simulatedGameState(gameState):
    #iteratively roll and place tiles randomly
    def startGame(self):
        while True:
            self.iterateGame();
            time.sleep(1.6);
            if(self.state.checkProgram()):
                break;
    
    def iterateGame(self):
        print('Simulating Gameplay')
        random_dice = self.game.rollTiles();
        rand_x = np.random.choice(range(7));
        rand_y = np.random.choice(range(7));
        rand_tile = np.random.choice(range(4));
        tile_shape = random_dice[rand_tile].tileShape;
        self.graphicsManager.assignSpace(rand_x,rand_y,tile_shape);

            
          
class simulatedGameState_v2(gameState):
    #iteratively roll and place tiles in legal positions
    def startGame(self):
        print('Playing random moves')
        while True:
            self.iterateGame();
            time.sleep(0.5);
            if(self.state.checkProgram()):
                break;
    
    def iterateGame(self):
        print('Simulating Gameplay')
        random_dice = self.game.rollTiles();
        rand_tile = np.random.choice(range(4));
        ntup = self.game.find_legal_placements(random_dice[rand_tile]);
        move = ntup[np.random.choice(range(len(ntup)))];
        print(move);
        self.game.place_piece(move[0],move[1], random_dice[rand_tile], move[2])
        tile_space = self.game.tile_manager.rotateTile(random_dice[rand_tile],move[2]);
        #tile_shape = self.game.place_piece(x, y, random_dice[rand_tile], rotation)
        self.graphicsManager.assignSpace(move[1],move[0],tile_space);
        print(tile_space[:,:,0]);
        self.game.get_board_statistics()
            
          
            
class autoGameState(gameState):
    def iterateGame(self):
        pass;
    
class interactiveGameState(gameState):
    def iterateGame(self):
        pass;
        
class AITrainingGameState(gameState):
    def startGame(self):
        print('Starting AI Training')
        rail_game = RailAIInterface();
        rrAI = GameAI(rail_game);
        self.AI = rrAI;
        self.AI.scoring = [];
        while True:
            self.AI.startGame();
            self.graphicsManager.resetImage();
            while not rail_game.isOver():
                self.iterateGame();
                time.sleep(0.01);
                if(self.state.checkProgram()):
                    break;
            
            self.AI.updateNetworks(0)
            self.AI.scoring.append(self.AI.final_score);
    
    def iterateGame(self):
        print('Simulating Gameplay')
        moves,placements = self.AI.takeTurn();
        for x,y,u,tile in placements:
            detile = tile[()];
            tile_space = self.game.tile_manager.rotateTile(detile,u);
            self.graphicsManager.assignSpace(y,x,tile_space);
        self.AI.game.game.get_board_statistics()

    
        
        
if __name__ == "__main__":
    gsm = gameStateManager('ai_training');
    gsm.assignGraphicsManager(emptyGraphics());
    
    gsm.runGame();
        

            
            