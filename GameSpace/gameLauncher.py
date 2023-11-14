# -*- coding: utf-8 -*-
"""
Created on Thu Apr 27 20:48:34 2023

@author: James
"""
 

from app_scheme import App
from railroad_inc_graphics import railroadGraphics
from game_graphics_manager import gameGraphicsManager
from game_state_manager import gameStateManager

class gameInstance():
    def __init__(self):
        self.gameManager = gameStateManager('simulated');
        self.graphicsManager = gameGraphicsManager(App,self.gameManager);
        
    def train(self):
        self.graphicsManager.start();
        
        return
    def play(self):
        self.graphicsManager.start();
    
    
    
if __name__ == "__main__":
    newGame = gameInstance();
    newGame.train();