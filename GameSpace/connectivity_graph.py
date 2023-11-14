# -*- coding: utf-8 -*-
"""
Created on Sun Aug 20 18:52:35 2023

@author: James
"""
import numpy as np
from railroad_inc_sim import railroadTileManager, railroadTile

error_val = -1;
idx_array = [[[-1, 0, -1], [1, -1, 2], [-1, 3, -1]],\
             [[-1, 4, -1], [5, -1, 6], [-1, 7, -1]]];

class RailRoadGraph:
    def __init__(self):
        self.size_x = 7;
        self.size_y = 7;
        self.set_default_graph();
        self.available_positions = np.zeros((self.size_x,self.size_y,1),dtype = bool);
        
    def set_default_graph(self):
        emp_graph = [];
        
        for x_idx in range(self.size_x):
            graph_row = [];
            for y_idx in range(self.size_x):
                graph_row.append(TileNode(x_idx,y_idx));
            emp_graph.append(graph_row);
        self.graph = emp_graph;
        
        #top roads
        self.available_positions[1,0] = True;
        self.available_positions[5,0] = True;
        #bottom roads
        self.available_positions[1,6] = True;
        self.available_positions[5,6] = True;
        #left roads
        self.available_positions[0,3] = True;
        #right roads
        self.available_positions[6,3] = True;
        
        #top rails
        self.available_positions[3,0] = True;
        #bottom rails
        self.available_positions[3,6] = True;
        #left rails
        self.available_positions[0,1] = True;
        self.available_positions[0,5] = True;
        #right rails
        self.available_positions[6,1] = True;
        self.available_positions[6,5] = True;
        
        return;
                
        
    def get_adjacency_matrix(self):
        pass
        
    def insert_tile(self,tile,pos_x,pos_y):
        cur_node = self.graph[pos_x,pos_y];
        cur_node.set_allowed_connections(tile);
        for x_idx in [-1,0,1]:
            for y_idx in [-1,0,1]:
                x_tar = pos_x + x_idx;
                y_tar = pos_y + y_idx;
                if((x_tar >= 0 & x_tar <= self.size_x) & (y_tar >= 0 & y_tar <= self.size_y)):
                    node_tar = self.graph[x_tar,y_tar];
                    cur_node.update_neighbor_list(node_tar);
                
        return;
    
    def find_legal_placements(self,tile):
        for x_idx in range(self.size_x):
            for y_idx in range(self.size_y):
                if(self.available_positions[x_idx,y_idx]):
                
                
        return;
    
    def is_placement_legal(self,tile,x,y):
        dummy_node = Nodetile(x,y);
        
        legality_vector = [];

        
        for r_idx in range(4): #rotations
            r_tile = rotate(tile);
            dummy_node.set_allowed_connections(r_tile);
            temp_vector = [];
            for x_idx in [-1,0,1]:
                for y_idx in [-1,0,1]:
                    x_tar = pos_x + x_idx;
                    y_tar = pos_y + y_idx;
                    if((x_tar >= 0 & x_tar <= self.size_x) & (y_tar >= 0 & y_tar <= self.size_y)):
                        #lookup starting positions
                        outside_tile = Nodetile(x_tar,y_tar);
                    else:
                        tar_node = self.graph[x_tar,y_tar];
                        temp_vector.append(dummy_node.is_connection_legal);
                    ##not done
                    
        

class TileNode:
    def __init__(self,x_pos,y_pos):
        self.x_pos = x_pos;
        self.y_pos = y_pos;
        self.neighbors = [None]*8;
        self.allowed_connections = [True]*8
        self.allow_layer_transfer = False;
        
        
    def update_neighbor_list(self,node):    
        diff_x = node.x_pos - self.x_pos;
        diff_y = node.y_pos - self.y_pos;
        
        if(np.abs(diff_x) > 1 | np.abs(diff_y) > 1 ):
            return;
        diff_x += 1;
        diff_y += 1;
        
        #find allowed connection layer at position
        top_layer_pos = idx_array[0][diff_x][diff_y];
        bottom_layer_pos = idx_array[1][diff_x][diff_y];
        
        n_top_layer_pos = idx_array[0][2-diff_x][2-diff_y];
        n_bottom_layer_pos = idx_array[1][2-diff_x][2-diff_y];
        
        top_flag = self.allowed_connections[top_layer_pos] & node.allowed_connections[n_top_layer_pos];
        bottom_flag = self.allowed_connections[bottom_layer_pos] & node.allowed_connections[n_bottom_layer_pos];
        
        if((bottom_flag & top_flag) | ~(bottom_flag | top_flag)):
            raise Exception("Top and Bottom Layer Connected. Node ill-defined.")
        elif(bottom_flag):
            self.neighbors[bottom_layer_pos] = node;
            node.neighbors[n_bottom_layer_pos] = self;
        elif(top_flag):
            self.neighbors[top_layer_pos] = node;
            node.neighbors[n_top_layer_pos] = self;
        else:
            raise Exception("Nodes can't be connected in current configuration.")
    
    def is_connection_legal(self,node):
        diff_x = node.x_pos - self.x_pos;
        diff_y = node.y_pos - self.y_pos;
        
        if(np.abs(diff_x) > 1 | np.abs(diff_y) > 1 ):
            return;
        diff_x += 1;
        diff_y += 1;
        
        #find allowed connection layer at position
        top_layer_pos = idx_array[0][diff_x][diff_y];
        bottom_layer_pos = idx_array[1][diff_x][diff_y];
        
        n_top_layer_pos = idx_array[0][2-diff_x][2-diff_y];
        n_bottom_layer_pos = idx_array[1][2-diff_x][2-diff_y];
        
        top_flag = self.allowed_connections[top_layer_pos] & node.allowed_connections[n_top_layer_pos];
        bottom_flag = self.allowed_connections[bottom_layer_pos] & node.allowed_connections[n_bottom_layer_pos];
        
        return [(top_flag ^ bottom_flag),top_flag,bottom_flag];
    
            
    def set_allowed_connections(self,tile):
        for r_idx in range(len(self.allowed_connections)):
            self.allowed_connections[r_idx] = False;
        for x_idx in range(np.shape(tile)[0]):
            for y_idx in range(np.shape(tile)[1]):
                for z_idx in range(2):
                    if(tile[x_idx][y_idx][z_idx] == 1):
                        neighbor_val = idx_array[z_idx][x_idx][y_idx];
                        
                        # set neighbors
                        if(neighbor_val != -1):
                            self.allowed_connections[neighbor_val] = True;
                            
        return;
        
    
    def traverse_node(self):
        pass;
        
        
        
if __name__ == "__main__":
    #start graph object
    graph = RailRoadGraph();
    
    #generate tiles
    tile_set = railroadTileManager();
    rolled_tiles = tile_set.rollTiles();
    
    #assign tile connectivity   
    graph.graph[1][1].set_allowed_connections(rolled_tiles[0].tileShape);
    
    
    tile_set = railroadTileManager();
    rolled_tiles = tile_set.rollTiles();
    for tile in rolled_tiles:
        print(tile.ID);
        print(tile.tileShape[:,:,0]);
        print(tile.tileShape[:,:,1]);