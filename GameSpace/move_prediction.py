# -*- coding: utf-8 -*-
"""
Move Prediction
Hosts the neural network that takes in input space and outputs weights on all 
possible moves

@author: Owner
"""
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import datasets, layers, models
from tensorflow.keras.models import Sequential
import numpy as np
from keras import backend as K


class PolicyNetwork():
    def __init__(self, batchSize=1):
        input_size = (batchSize,5,5,16,1); #[(5x5)*(1 colour 
                     # + (4 layers of player one + all ones + 4 layers of player two
                     # + all ones + 4 layers of buildings + all ones) * 1 time step)] = 5x5x16
        output_size = np.prod((5,5,8,8)); #[(8 moving)*(8 building)]*(5x5)
    
        # define model
        # deep convolutional network
        model = Sequential([
            layers.Conv3D(64, kernel_size=(3,3,16), input_shape = input_size[1:], padding='same', activation='relu'),
            layers.Conv3D(128, kernel_size=(3,3,16), padding='same', activation='relu'),
            layers.MaxPooling3D(pool_size=(2, 2, 4)),
            layers.Conv3D(256, kernel_size=(3,3,2), padding='same', activation='relu'),
            layers.Conv3D(256, kernel_size=(3,3,2), padding='same', activation='relu'),
            layers.MaxPooling3D(pool_size=(2, 2, 1)),
            layers.Dropout(0.2),
            layers.Flatten(),
            layers.Dense(output_size/2, activation='relu'),
            layers.Dense(output_size,activation='softmax')
        ]);
    
        # model loss function
        # regression, minimization of difference between predicted and expected move distributions
        opt = keras.optimizers.Adam(learning_rate=0.01);
        model.compile(optimizer=opt,
              loss=tf.keras.losses.MeanSquaredError())
        self.network = model;
        return
        
    def predict(self, boardSpace):
        boardSpace = np.reshape(boardSpace,[1, 5, 5, 16, 1])
        distribution = self.network.predict(boardSpace);
        return distribution;
        
    def update(self, boardSpace, valueDistribution):
        boardSpace = np.reshape(boardSpace,[1, 5, 5, 16, 1])
        self.network.fit(boardSpace, valueDistribution);
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
    net = PolicyNetwork();
    net.network.summary();
