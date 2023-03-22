# -*- coding: utf-8 -*-
"""
Move Selection
Deals with training the value network and the MCTS algorithm

@author: Owner
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import datasets, layers, models
from tensorflow.keras.models import Sequential
import numpy as np;
from mc_tree_search import MonteCarloSearchTree;
from keras import backend as K

class ValueNetwork():
    def __init__(self, max_evl = 300):
        input_size = (1,5,5,16,1); #[(5x5)*(1 colour 
                     # + (4 layers of player one + all ones + 4 layers of player two
                     # + all ones + 4 layers of buildings) * 1 time step)] = 5x5x15
        output_size = 2; # Win[0], Lose[1]
    
        # define model
        # deep convolutional network
        #model = Sequential([
        #    layers.Conv3D(64, kernel_size=(3,3,16), input_shape = input_size[1:], padding='same', activation='relu'),
        #    layers.Conv3D(64, kernel_size=(3,3,4), padding='same', activation='relu'),
        #    layers.MaxPooling3D(pool_size=(2, 2, 4)),
        #    layers.Conv3D(64, kernel_size=(3,3,2), padding='same', activation='relu'),
        #    layers.MaxPooling3D(pool_size=(2, 2, 1)),
        #    layers.Dropout(0.2),
        #    layers.Flatten(),
        #    layers.Dense(256, activation='relu'),
        #    layers.Dense(output_size,activation='softmax')
        #]);
        model = Sequential([
            layers.Conv3D(64, kernel_size=(3,3,2), input_shape = input_size[1:], padding='same', activation='relu'),
            layers.MaxPooling3D(pool_size=(2, 2, 1)),
            layers.Conv3D(64, kernel_size=(3,3,2), padding='same', activation='relu'),
            layers.MaxPooling3D(pool_size=(2, 2, 1)),
            layers.Dropout(0.2),
            layers.Flatten(),
            layers.Dense(1024, activation='relu'),
            layers.Dense(output_size,activation='softmax')
        ]);
    
        # model loss function
        # classification, win or lose
        opt = keras.optimizers.Adam(learning_rate=0.01);
        model.compile(optimizer=opt,
              loss=tf.keras.losses.BinaryCrossentropy())
        self.network = model;
        return;
        
    def predict(self, boardSpace):
        if isinstance(boardSpace, list):
            items = len(boardSpace);
            boardSpace = np.vstack(boardSpace);
            boardSpace = np.reshape(boardSpace, [items,5,5,16,1]);
            values = self.network.predict(boardSpace, batch_size=items);
            return values[:,0];
        else:
            boardSpace = np.reshape(boardSpace,[1, 5, 5, 16, 1])
            value = self.network.predict(boardSpace);
            return value[0];
    
    def evaluateMoves(self, prediction, boardSpace, legalMoves):
        counter = 0;
        for i,x in enumerate(prediction):
            if x != 0:
                estimate = self.predict(legalMoves[counter])[0];
                prediction[i] *= estimate*len(legalMoves);
                counter += 1;
        return prediction;
    
    def selectMove(self, prediction, player, boardSpace, moveGenerator, evaluator, moveMaker):
        mcts = MonteCarloSearchTree(moveGenerator, self.predict, evaluator, player, moveMaker);
        [move_choice, values, ucbs] = mcts.predict(prediction,boardSpace);
        return [move_choice, values, ucbs];    
    
    def update(self, boardSpace, value):
        boardSpace = np.reshape(boardSpace,[1, 5, 5, 16, 1])
        value = np.reshape(value,[1,2]);
        self.network.fit(boardSpace, value);
        return;
        
    def setLearningRate(self, learningRate):
        K.set_value(self.model.optimizer.learning_rate, learningRate);
        return;
        
    def load(self, path):
        self.network = keras.models.load_model(path);
        return;
        
    def save(self, path):
        self.network.save(path);
        return;

if __name__ == '__main__':
    net = ValueNetwork();
    net.network.summary();
