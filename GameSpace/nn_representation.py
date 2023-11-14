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
    
#x-y notation
directions_vectors = {'up':[0,-1],'down':[0,1],'left':[-1,0],'right':[1,0]};
rotation_order = ['up','right','down','left'];    

#layer positions
directions_offsets = {'up':0,'right':1,'down':2,'left':3};
rail_road_offsets = {'road':2,'rail':6};
overpass_offset = 10;
special_piece_offsets = {1:11,2:12,3:13,4:14,5:15};

#starting positions
start_roads = [[1,0],[5,0],[0,3],[1,6],[5,6],[6,3]];
start_roads_bordered = [[0,4],[2,0],[2,8],[6,0],[6,8],[8,4]];

start_rails = [[3,0],[0,1],[6,1],[0,5],[6,5],[3,6]];
start_rails_bordered = [[4,0],[0,2],[8,2],[0,6],[8,6],[4,8]];


class RailRoadActions:
    #class to handle actual logic of placing pieces
    def __init__(self):
        self.board_rep = NNRailRoadInterpreter();
        self.tile_manager = railroadTileManager();
        self.tile_converter = TileManagerInterface(self.board_rep,self.tile_manager);
        self.tiled_board = self.create_empty_board();
        
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


    def __count_connected_exits(self):
        # return length of longest path
        rail_networks = self.board_rep.search_connected_exits('rail');
        road_networks = self.board_rep.search_connected_exits('road');
        return;
        
        
    def __count_longest_path(self):
        rail_length = self.board_rep.search_longest_path('rail');
        road_length = self.board_rep.search_longest_path('road');
        
        return [rail_length,road_length]
    
    def __count_center_points(self):
        tiles = self.board_rep.tiles;
        center = tiles[2:4][2:4];
        return sum(center);
        
    def ___count_blocked_tiles(self):
        return self.board_rep.search_blocked_paths('rail') + self.board_rep.search_blocked_paths('road');
        
    def get_board_statistics(self):
        # get representative statistics to allow easier production of heuristics
        # get longest roads, rails, number of remaining tiles, number of "connected tiles", number of tiles in "center", number of blocked tiles, number of failed connections
        [rail_l,road_l] = self.__count_longest_path();
        center = self.__count_center_points();
        blocked = self.__count_blocked_tiles();
        exits = self.__count_connected_exits();
        
        print('Longest Road : ', road_l);
        print('Longest Rail : ', rail_l);
        print('Tiles in Center : ', center);
        print('Connected Exits : ', exits)
        
        return [rail_l, road_l, center, exits, blocked]
        
    def score_final_position(self):
        return;       
        
    def score_intermediate_position(self):
        
        
        return;
        
class NNRailRoadInterpreter:
    #class to handle higher level operations from nn representation
    def __init__(self):
        self.representation = NNRailRoadRepresentation();
        self.update_available_positions();
        return;

        
    def place_piece(self,x,y,connections):
        self.representation.assign_placement(x,y,connections);
        return;
        
    def find_legal_placements(self,tile_rotations):
        legal_placements = []; #x,y,u
        for x_idx in range(self.representation.size_x-2):
            for y_idx in range(self.representation.size_y-2):
                if(self.representation.available_tiles[x_idx][y_idx]):
                    for u_idx in range(len(rotation_order)):
                        current_rotation_connections = tile_rotations[u_idx];
                        legal = self.is_placement_legal(current_rotation_connections,x_idx,y_idx);
                        if(legal):
                            legal_placements.append([x_idx,y_idx,u_idx]);
        return legal_placements
        
    def update_available_positions(self):
        self.representation.update_available_positions();
        self.tiles = self.representation.placed_tiles;
        self.available_positions = self.representation.available_tiles;
        self.available_list = self.representation.available_positions_list;
        return;
    
    def get_available_tiles(self):
        return self.representation.available_positions_list;
    
    def is_placement_legal(self,connections,x,y):
        is_legal = False;
        is_illegal = False;
        for rail_or_road,direction in connections:
            [allowed_connection,illegal_connection] = self.representation.check_legal_connection(x, y, rail_or_road, direction);
            is_legal = is_legal or allowed_connection; #only one connection must connect
            is_illegal = is_illegal or illegal_connection;
        return is_legal and not is_illegal;
    
    def vectorize_placements(self,placement_list):
        return self.representation.vectorize_placements(placement_list);
    
    def search_connected_exits(self,rail_or_road):
        if(rail_or_road == 'rail'):
            full_board = start_rails;
        else:
            full_board = start_roads;
        
        networks = [];
        while len(full_board) > 0:
            next_point  = full_board.pop(0);
            [connections,points_searched,farthest_point] = self.find_connected_exits(next_point[0], next_point[1], rail_or_road);
            for [x_idx,y_idx] in points_searched.keys():
                if [x_idx,y_idx] in full_board:
                    full_board.remove([x_idx,y_idx]);
            if(connections > 1):
                networks.append(connections);
        
        return networks;
    
    def find_connected_exits(self,start_x,start_y,rail_or_road):
        #BFS
        point_history = {(start_x,start_y):1}; #history dictionary
        
        if(rail_or_road == 'rail'):  
            adjusted_entries = start_rails_bordered - 1; 
        else:
            adjusted_entries = start_roads_bordered - 1; 
        
        unexplored_points = [[start_x,start_y]];
        connected_exits = 0;
        #continue to search until running out of points
        while len(unexplored_points) > 0:
            #pick nearest point to explore
            next_point = unexplored_points.pop(0);
            
            #check for connections
            children = self.representation.traverse_tile(next_point[0], next_point[1], rail_or_road);
            
            for child in children:
                child_key = (child[0],child[1]);
                if(child_key not in point_history):
                    unexplored_points.append(child);
           
            point_history[(next_point[0],next_point[1])] = 0;
            
            if(next_point in adjusted_entries):
                connected_exits += 1;
                    
        return [connected_exits,point_history]
    
    
    def search_blocked_paths(self,rail_or_road):
        blocked = 0;
        for x_idx in range(7):
            for y_idx in range(7):
                [failed_connections] = self.repesentation.blocked_tile(x_idx,y_idx,rail_or_road);
                blocked += len(failed_connections);

        
        return blocked
    
    
    def search_longest_path(self,rail_or_road):
        full_board = [];
        for x_idx in range(7):
            for y_idx in range(7):
                full_board.append([x_idx,y_idx]);
        
        longest_path = 0;
        while len(full_board) > 0:
            next_point  = full_board.pop(0);
            [length,points_searched,farthest_point] = self.find_longest_path(next_point[0], next_point[1], rail_or_road);
            for [x_idx,y_idx] in points_searched.keys():
                if [x_idx,y_idx] in full_board:
                    full_board.remove([x_idx,y_idx]);
            if(length > longest_path):
                longest_path = length;
        
        return longest_path
    
    def find_longest_path(self,start_x,start_y,rail_or_road):
        #BFS
        length_to_point = {(start_x,start_y):1}; #history dictionary
        
        if(rail_or_road == 'rail'):  
            adjusted_entries = start_rails_bordered; 
        else:
            #adjusted_entries = [[y-1 for y in x] for x in start_roads_bordered];
            adjusted_entries = start_roads_bordered;
        
        unexplored_points = [[start_x,start_y]];
        longest_path = 0;
        #continue to search until running out of points
        while len(unexplored_points) > 0:
            #pick nearest point to explore
            next_point = unexplored_points.pop(0);
            
            #check for connections
            children = self.representation.traverse_tile(next_point[0], next_point[1], rail_or_road);
            
            
            min_dist = length_to_point[(next_point[0],next_point[1])];
            for child in children:
                child_key = (child[0],child[1]);
                if(child_key in length_to_point):
                    #update position based on connctions
                    if(length_to_point[child_key] + 1 < min_dist):
                        min_dist = length_to_point[child_key] + 1;
                        print(next_point[0],next_point[1],min_dist);
                        
                else:
                    unexplored_points.append(child);
           
            length_to_point[(next_point[0],next_point[1])] = min_dist;
            
            #add child lengths
            for child in children:
                child_key = (child[0],child[1]);
                if(child_key not in length_to_point):
                    length_to_point[child_key] = min_dist+1;
            
                
        
        #try again from furthest point (likely a longer path)
        v = list(length_to_point.values());
        k = list(length_to_point.keys());
        farthest_point = k[v.index(max(v))];
        longest_path = max(v);
         
        
        return [longest_path,length_to_point,farthest_point];
    
  
    

        
class NNRailRoadRepresentation:
    #representation_scheme
    #[9 (x position + 2 border) by 9 (y_position + 2 border) by N (layers) - binary matrix]
    #layer 1 : Tile placement, 1 = tile placed, 0 = no tile
    #layer 2 : Tile availability, 1 = "a tile can be placed here", 0 = "a tile can not be placed here"
    #
    #start of tile conditioning layers
    #layer 3 : "Can road connect upwards?" (y+1), 1 = "yes", 0 = "no"
    #layer 4 : "Can road connect downwards?" (y-1), 1 = "yes", 0 = "no"
    #layer 5 : "Can road connect right?" (x+1), 1 = "yes", 0 = "no"
    #layer 6 : "Can road connect left?" (x-1), 1 = "yes", 0 = "no"
    #layer 7 : "Can rail connect upwards?" (y+1), 1 = "yes", 0 = "no"
    #layer 8 : "Can rail connect downwards?" (y-1), 1 = "yes", 0 = "no"
    #layer 9 : "Can rail connect right?" (x+1), 1 = "yes", 0 = "no"
    #layer 10 : "Can rail connect left?" (x-1), 1 = "yes", 0 = "no"
    #layer 11 : "Overpass?", 1 = "yes", 0 = "no"
    #questions are oriented from the perspective of the (x,y) tile. i.e (if can connect road upwards, that means the x,y tile has a road oriented towards x,y+1)
    #    
    #encoding of available action
    #layer 11-15 : unique identifier of input piece, shouldn't convolve with above layers. Potentially binary encoded representation in (number of bits) layers
    #layer 16 : unique identifiers of available "special pieces", each piece can be a full 7x7 1 or 0 for availabilty
    
    def __init__(self):
        self.size_x = 9;
        self.size_y = 9;
        self.layers = 16;
        self.size_move_vector = 7*7*4; #allows encoding for all 7x by 7y by 4 rotation placements
        self.available_positions_list = [];
        self.placed_tiles = np.zeros((self.size_x-2,self.size_y-2),dtype = bool);
        self.available_tiles = np.zeros((self.size_x-2,self.size_y-2),dtype = bool);
        self.directions = directions_offsets;
        self.rail_road_layers = rail_road_offsets;
        self.set_default_mat();
        
    def set_default_mat(self):
        emp_graph = [];
        
        self.board = np.zeros((self.size_x,self.size_y,self.layers),dtype = bool); 
        
        #need to assign connections in border
        
        #top roads
        self.assign_connectivity(2,0,'road','down');
        self.board[2][0][0] = 1;
        self.assign_connectivity(6,0,'road','down');
        self.board[6][0][0] = 1;
        
        #bottom roads
        self.assign_connectivity(2,8,'road','up');
        self.board[2][8][0] = 1;
        self.assign_connectivity(6,8,'road','up');
        self.board[6][8][0] = 1;
    
        #left roads
        self.assign_connectivity(0,4,'road','right');
        self.board[0][4][0] = 1;

        #right roads
        self.assign_connectivity(8,4,'road','left');
        self.board[8][4][0] = 1;
        
        #top rails
        self.assign_connectivity(4,0,'rail','down');
        self.board[4][0][0] = 1;
        #bottom rails
        self.assign_connectivity(4,8,'rail','up');
        self.board[4][8][0] = 1;
        #left rails
        self.assign_connectivity(0,2,'rail','right');
        self.board[0][2][0] = 1;
        self.assign_connectivity(0,6,'rail','right');
        self.board[0][6][0] = 1;
        #right rails
        self.assign_connectivity(8,2,'rail','left');
        self.board[8][2][0] = 1;
        self.assign_connectivity(8,6,'rail','left');
        self.board[8][6][0] = 1;
        
        #make tiles available
        #top roads
        self.board[2,1,1]=1;
        self.board[6,1,1]=1;
        #bottom roads
        self.board[2,7,1]=1;
        self.board[6,7,1]=1;
        #left roads
        self.board[1,4,1]=1;
        #right roads
        self.board[7,4,1]=1;
        #top rails
        self.board[4,1,1]=1;
        #bottom rails
        self.board[4,7,1]=1;
        #left rails
        self.board[1,2,1]=1;
        self.board[1,6,1]=1;
        #right rails
        self.board[7,2,1]=1;
        self.board[7,6,1]=1;
        
        self.update_available_positions();
        
        return;

    def get_layer(self,rail_or_road,direction):
        return self.rail_road_layers[rail_or_road]+self.directions[direction];
    
    def get_vector_offset(self,x,y,direction):
        vector = directions_vectors[direction];
        return [x+vector[0],y+vector[1]]
    
    def assign_connectivity(self,x,y,rail_or_road,direction):   
        self.board[x,y,self.get_layer(rail_or_road,direction)] = 1;
        return;
        
    def check_legal_connection(self,x,y,rail_or_road,direction):
        #returns true if current connection is a connection (only one connection at a time)
        if(direction == 'center'):
            return [False,False];

        
        vector = directions_vectors[direction];
        target_x = x + vector[0] + 1; #adjust for border
        target_y = y + vector[1] + 1; #adjust for border
        legality = False;
        illegality = False;
        
        if(self.board[target_x][target_y][0] == 0):#if no tile placed, then connection
            legality = False;
        else:
            # check if opposite connection is present in target tile
            opposite_direction_offset = (directions_offsets[direction] + 2) % 4;
            opposite_direction_str = list(directions_offsets.keys())[opposite_direction_offset];
            
            if(rail_or_road == 'rail'):
                opposite_type_str = 'road';
            else:
                opposite_type_str = 'rail';
            
            connection = self.board[target_x][target_y][self.get_layer(rail_or_road,opposite_direction_str)];
            illegal_connection = self.board[target_x][target_y][self.get_layer(opposite_type_str,opposite_direction_str)];
            if(connection == 1):
                legality = True;
            if(illegal_connection == 1):
                illegality = True;
        return [legality,illegality]
    
    def check_connected_tiles(self,x,y,rail_or_road,direction):
        #checks adjacent tiles of a placed tile for updating of available tiles
        vector = directions_vectors[direction];
        target_x = x + vector[0];
        target_y = y + vector[1];
        availability = False;
        
        if(self.board[target_x][target_y][0] == 0):#if no tile placed
            availability = True;
            
        return [target_x,target_y,availability]
        
    def update_available_positions(self):
        sublayer = self.board[1:8,1:8,1];
        self.available_positions_list = np.nonzero(sublayer);
        self.placed_tiles = self.board[1:8,1:8,0];
        self.available_tiles = self.board[1:8,1:8,1];
        return;
        
    def assign_placement(self,x,y,connections):
        #connections is a key-value list of rail_or_road followed by direction. May include additional tags
        
        b_x = x+1; #adjust x from tile position to board position (account for borders)
        b_y = y+1; #adjust y from tile position to board position (account for borders) 
        
        #occupy x,y position
        self.board[b_x,b_y,0] = 1; #tile is placed here
        self.board[b_x,b_y,1] = 0; #position is no longer available
        
        #update available positions
        for rail_or_road,direction in connections:
            self.assign_connectivity(b_x,b_y,rail_or_road,direction);
            [target_x,target_y,availability] = self.check_connected_tiles(b_x, b_y, rail_or_road, direction);
            if(self.board[target_x,target_y,0] == 0): #no tile
                self.board[target_x,target_y,1] = availability;
            
        self.update_available_positions();
                        
        return;
        
    def vectorize_placements(self,placement_list):
        move_vector = np.zeros([self.size_move_vector],dtype='bool');
        for [x,y,u] in placement_list:
            move_vector[x*(7*4) + y*4 + u] = 1;
        return move_vector
    
    def traverse_tile(self,x,y,rail_or_road):
        #return list of all connected [x,y,rail/road] positions from given tile
        x = x+1;
        y = y+1;
        
        connected_positions = [];
        
        rr_keys = list(rail_road_offsets.keys());
        dir_keys = list(directions_offsets.keys());
    
        for u_idx in range(4):
            direction = dir_keys[u_idx];
            vector_xy = self.get_vector_offset(x, y, direction);
            if(vector_xy[0] == 0 or vector_xy[0] == 8):
                continue;
            if(vector_xy[1] == 0 or vector_xy[1] == 8):
                continue;     
            
            route_exists = self.board[x,y,self.get_layer(rail_or_road, direction)];
            [legal,illegal] = self.check_legal_connection(x-1,y-1,rail_or_road,direction);
            
            if(route_exists and legal and not illegal):
                connected_positions.append([vector_xy[0]-1,vector_xy[1]-1]);
        return connected_positions;
    
    def blocked_tile(self,x,y,rail_or_road):
        #return list of all routes that are failed connections [x,y,rail/road] from given tile
        x = x+1;
        y = y+1;
        
        connected_positions = [];
        
        rr_keys = list(rail_road_offsets.keys());
        dir_keys = list(directions_offsets.keys());
    
        for u_idx in range(4):
            direction = dir_keys[u_idx];
            vector_xy = self.get_vector_offset(x, y, direction);
            if(vector_xy[0] == 0 or vector_xy[0] == 8):
                continue;
            if(vector_xy[1] == 0 or vector_xy[1] == 8):
                continue;     
            
            route_exists = self.board[x,y,self.get_layer(rail_or_road, direction)];
            [legal,illegal] = self.check_legal_connection(x-1,y-1,rail_or_road,direction);
            
            if(route_exists and not legal):
                connected_positions.append([vector_xy[0]-1,vector_xy[1]-1]);
        return connected_positions;
        

class TileManagerInterface:
    #utility class to generalize different possible "TileManagers" to connect with NN representation
    #all tile rotations should be managed in this class
    
    def __init__(self,board_rep,tile_manager):
        self.board_rep = board_rep;
        self.tile_manager = tile_manager;
        
    def decompose_tile(self,tile,rotation):
        tile_array = tile.tileShape;
        
        road_grid = tile_array[:,:,0];
        rail_grid = tile_array[:,:,1];
        
        connections = [];
        
        if(road_grid[0,1]):
            connections.append(['road','up']);
        if(road_grid[2,1]):
            connections.append(['road','down']);
        if(road_grid[1,0]):
            connections.append(['road','left']);
        if(road_grid[1,2]):
            connections.append(['road','right']);
        
        if(rail_grid[0,1]):
            connections.append(['rail','up']);
        if(rail_grid[2,1]):
            connections.append(['rail','down']);
        if(rail_grid[1,0]):
            connections.append(['rail','left']);
        if(rail_grid[1,2]):
            connections.append(['rail','right']);
        
        #if(road_grid[1,1]):
        #    connections.append(['overpass','center']);
            
            
        #apply rotations
        rotated = [];
        for con in connections:
            tile_type = con[0];
            tile_direction = con[1];
            if(tile_direction in rotation_order):
                rot_pos = rotation_order.index(tile_direction);
                new_pos = (rot_pos + rotation) % len(rotation_order);
                rotated.append([tile_type,rotation_order[new_pos]])
            else:
                rotated.append([tile_type,tile_direction]);
            
        return rotated;
    
    def rotateTile(self,tile,rotation):
        return;
    
    #def get_connections(self,tile,rotation):
        #key-value list of ['rail','up',etc]
        #return
    
    
    
    
    
if __name__ == "__main__":
    #start graph object
    graph = RailRoadActions();
    
    #generate tiles
    while len(graph.available_tiles) > 0:
        rolled_tiles = graph.rollTiles();
        ntup = graph.find_legal_placements(rolled_tiles[0]);
        
        move = ntup[0];
        graph.place_piece(move[0],move[1], rolled_tiles[0], move[2])
        
    

    
    
    tile_set = railroadTileManager();
    rolled_tiles = tile_set.rollTiles();
    for tile in rolled_tiles:
        print(tile.ID);
        print(tile.tileShape[:,:,0]);
        print(tile.tileShape[:,:,1]);