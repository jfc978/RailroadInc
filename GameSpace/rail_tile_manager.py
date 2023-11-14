import numpy as np
import random


class railroadTileManager:
    def __init__(self):
        self.dice1 = [
            railroadTile([[0,1,0],[0,1,0],[0,1,0]], False, 1/6, 'straight_road',railOrRoad = 'Road'),
            railroadTile([[0,1,0],[0,1,0],[0,1,0]], False, 1/6, 'straight_rail',railOrRoad = 'Rail'),
            railroadTile([[0,0,0],[1,1,0],[0,1,0]], False, 1/6, 'right_road',railOrRoad = 'Road'),
            railroadTile([[0,0,0],[1,1,0],[0,1,0]], False, 1/6, 'right_rail',railOrRoad = 'Rail'),
            railroadTile([[0,0,0],[1,1,1],[0,1,0]], False, 1/6, 't_road',railOrRoad = 'Road'),
            railroadTile([[0,0,0],[1,1,1],[0,1,0]], False, 1/6, 't_rail',railOrRoad = 'Rail')
            ];
        self.dice2 = [
            railroadTile([[0,1,0],[0,1,0],[0,1,0]], False, 1/6, 'straight_road',railOrRoad = 'Road'),
            railroadTile([[0,1,0],[0,1,0],[0,1,0]], False, 1/6, 'straight_rail',railOrRoad = 'Rail'),
            railroadTile([[0,0,0],[1,1,0],[0,1,0]], False, 1/6, 'right_road',railOrRoad = 'Road'),
            railroadTile([[0,0,0],[1,1,0],[0,1,0]], False, 1/6, 'right_rail',railOrRoad = 'Rail'),
            railroadTile([[0,0,0],[1,1,1],[0,1,0]], False, 1/6, 't_road',railOrRoad = 'Road'),
            railroadTile([[0,0,0],[1,1,1],[0,1,0]], False, 1/6, 't_rail',railOrRoad = 'Rail')
            ];

        self.dice3 = [
            railroadTile([[0,1,0],[0,1,0],[0,1,0]], False, 1/6, 'straight_road',railOrRoad = 'Road'),
            railroadTile([[0,1,0],[0,1,0],[0,1,0]], False, 1/6, 'straight_rail',railOrRoad = 'Rail'),
            railroadTile([[0,0,0],[1,1,0],[0,1,0]], False, 1/6, 'right_road',railOrRoad = 'Road'),
            railroadTile([[0,0,0],[1,1,0],[0,1,0]], False, 1/6, 'right_rail',railOrRoad = 'Rail'),
            railroadTile([[0,0,0],[1,1,1],[0,1,0]], False, 1/6, 't_road',railOrRoad = 'Road'),
            railroadTile([[0,0,0],[1,1,1],[0,1,0]], False, 1/6, 't_rail',railOrRoad = 'Rail')
            ];

        self.dice4 = [
            railroadTile([[[0,1,0],[0,1,0],[0,1,0]],[[0,0,0],[1,1,1],[0,0,0]]], False, 1/3, 'overpass'),
            railroadTile([[[0,0,0],[1,0,0],[0,0,0]],[[0,0,0],[0,0,1],[0,0,0]]], False, 1/3, 'straight_station'),
            railroadTile([[[0,0,0],[1,0,0],[0,0,0]],[[0,0,0],[0,0,0],[0,1,0]]], False, 1/3, 'right_station')
            ];
        
        self.special = [
            railroadTile([[[0,1,0],[1,1,1],[0,0,0]],[[0,0,0],[0,0,0],[0,1,0]]], False, 1, 'three_road_one_rail'),
            railroadTile([[[0,0,0],[1,0,0],[0,0,0]],[[0,0,0],[1,1,1],[0,1,0]]], False, 1, 'one_road_three_rail'),
            railroadTile([[[0,1,0],[1,1,1],[0,1,0]],[[0,0,0],[0,0,0],[0,0,0]]], False, 1, 'four_road'),
            railroadTile([[[0,0,0],[0,0,0],[0,0,0]],[[0,1,0],[1,1,1],[0,1,0]]], False, 1, 'four_rail'),
            railroadTile([[[0,1,0],[1,1,0],[0,0,0]],[[0,0,0],[0,1,1],[0,1,0]]], False, 1, 'two_road_two_rail'),
            railroadTile([[[0,0,0],[1,0,1],[0,0,0]],[[0,1,0],[0,0,0],[0,1,0]]], False, 1, 'cross_station'),
            ];

        self.base_tiles = [];
        self.base_tiles.extend(self.dice1);
        self.base_tiles.extend(self.dice2);
        self.base_tiles.extend(self.dice3);
        self.base_tiles.extend(self.dice4);
        self.base_tiles.extend(self.special);
        
        self.rolled_tiles = [];
        return;
        
    def remainingTiles(self):
        self.rolled_tiles;
        return;
    
    def useTile(self,tile):
        #use a tile, remove the tile if it is unique
        #there's definitely a more efficient way to do this
        list_copy = self.base_tiles;
        for tile_obj in list_copy:
            if(tile.tileShape == tile_obj.tileShape):
                if(tile_obj.unique):
                    self.base_tiles.remove(tile_obj)
                break;
                
    def rollTiles(self):
        roll_one = random.choices(self.dice1,weights = [a.probability for a in self.dice1])[0];
        roll_two = random.choices(self.dice2,weights = [a.probability for a in self.dice2])[0];
        roll_three = random.choices(self.dice3,weights = [a.probability for a in self.dice3])[0];
        roll_four = random.choices(self.dice4,weights = [a.probability for a in self.dice4])[0];
        
        self.rolled_tiles = [roll_one,roll_two,roll_three,roll_four];
        
        return self.rolled_tiles;
        
    def emptyTile(self):
        return railroadTile([[[0,0,0],[0,0,0],[0,0,0]],[[0,0,0],[0,0,0],[0,0,0]]], False, 1, 'empty');
    
    def rotateTile(self,tile,rotation):
        tile_space = tile.tileShape
        return np.rot90(tile_space,-rotation,axes=(0,1));
        
        
class railroadTile:
    def __init__(self, tileShape, isUnique, probability, tileID, railOrRoad = 'None'):
        self.unique = isUnique;
        self.probability = probability;
        self.ID = tileID;
        emptyTile = np.zeros((3,3,2), dtype=bool);
        
        if(railOrRoad == 'None'):
            emptyTile[:,:,0] = np.array(tileShape[0],dtype=bool);
            emptyTile[:,:,1] = np.array(tileShape[1],dtype=bool);
        elif(railOrRoad == 'Rail'):
            emptyTile[:,:,0] = tileShape;
        else:
            emptyTile[:,:,1] = tileShape;
        
        self.tileShape = emptyTile;
        return;

    def rotate(self):
        m = self.tileShape;
        rotated_tile = [[m[j][i] for j in range(len(m))] for i in range(len(m[0])-1,-1,-1)]
        return railroadTile(rotated_tile, self.isUnique, self.probability, self.ID);