# -*- coding: utf-8 -*-
"""
Created on Thu Jan 13 13:11:21 2022

Generate a visual representation of the board.

@author: Owner
"""

import matplotlib.pyplot as plt
import numpy as np

class BoardGraphics():
    def __init__(self):
        self.plot = plt.figure(0);
        self.roads = np.zeros((7*3,7*3,2), dtype=bool);
        self.rails = np.zeros((7*3,7*3,2), dtype=bool);
        return;
        
        
    def updateBoard(self, board, deconstructor):
        [roads, rails] = deconstructor(board);
        self.roads = roads;
        self.rails = rails;
        
        self.displayBoard();
        
        return;
        
    def displayBoard(self):
        cube1 = (self.roads == 1);
        cube2 = (self.rails == 1);
        
        # combine the objects into a single boolean array
        voxelarray = cube1 | cube2
        
        # set the colors of each object
        colors = np.empty(voxelarray.shape, dtype=object)
        colors[cube1] = 'red'
        colors[cube2] = 'blue'
        self.plot = plt.figure(0);
        # and plot everything
        ax = self.plot.add_subplot(projection='2d')
        ax.voxels(voxelarray, facecolors=colors, edgecolor='k')
        
        plt.show()
        return;

if __name__ == '__main__':
    graphics = BoardGraphics();
    graphics.displayBoard();
    
    print("display")