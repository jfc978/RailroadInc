# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import numpy as np
import tkinter as tk
import threading
from threading import Event
from PIL import Image
import time
from app_scheme import App

#image_size = 700;
        
class emptyGraphics():
    def __init__(self):
        self.roads = np.zeros((7*3,7*3,1), dtype=bool);
        self.rails = np.zeros((7*3,7*3,1), dtype=bool);
        
        self.game_image = Image.fromarray(np.zeros((1,1,3), dtype=np.uint8), 'RGB');
        
        return;
        
        
    def assignSpace(self,board_x,board_y,tile_shape):
        road_space = tile_shape[:,:,0];
        rail_space = tile_shape[:,:,1];
        
        
        x = board_x*3;
        y = board_y*3;
        self.roads[x:x+3,y:y+3,0] = road_space;
        self.rails[x:x+3,y:y+3,0] = rail_space;
        self.displayBoard();
        return;
        
    def updateBoard(self, rails, roads):

        self.roads = roads;
        self.rails = rails;
        
        self.displayBoard();
        
        return;
        
    def displayBoard(self):
        
        data = np.zeros((7*3, 7*3, 3), dtype=np.uint8);
        # combine the objects into a single boolean array
        intersect_array = self.rails & self.roads;

        [cube1_x, cube1_y] = np.where(self.rails == 1)[0:2]
        [cube2_x, cube2_y] = np.where(self.roads == 1)[0:2]
        [cube3_x, cube3_y] = np.where(intersect_array == 1)[0:2]
        
        if(np.any(self.rails)):
            data[cube1_x,cube1_y,:] = [255, 0, 0]; #roads are red
        if(np.any(self.roads)):
            data[cube2_x,cube2_y,:] = [0, 255, 0]; #rails are blue
        if(np.any(intersect_array)):
            data[cube3_x,cube3_y,:] = [150, 150, 0]; #rails are blue
        img = Image.fromarray(data, 'RGB');
        self.game_image = img;
        
        fig = plt.figure(1)
        plt.ion()
        plt.show()
        self.plot = plt.imshow(self.game_image)
        plt.pause(0.001)
        plt.show()
    
    
        return;
        
    def getImage(self):
        
        return self.game_image;
    
    def checkProgram(self):
        return False;
    
    def setEvent(self,event):
        return;

class railroadGraphics():
    def __init__(self):
        self.roads = np.zeros((7*3,7*3,1), dtype=bool);
        self.rails = np.zeros((7*3,7*3,1), dtype=bool);
        
        self.game_image = Image.fromarray(np.zeros((1,1,3), dtype=np.uint8), 'RGB');
        return;
        
        
    def assignSpace(self,board_x,board_y,tile_shape):
        road_space = tile_shape[:,:,0];
        rail_space = tile_shape[:,:,1];
        
        
        x = board_x*3;
        y = board_y*3;
        self.roads[x:x+3,y:y+3,0] = road_space;
        self.rails[x:x+3,y:y+3,0] = rail_space;
        self.displayBoard();
        return;
        
    def updateBoard(self, rails, roads):

        self.roads = roads;
        self.rails = rails;
        
        self.displayBoard();
        
        return;
        
    def displayBoard(self):
        
        data = np.zeros((7*3, 7*3, 3), dtype=np.uint8);
        # combine the objects into a single boolean array
        intersect_array = self.rails & self.roads;

        [cube1_x, cube1_y] = np.where(self.rails == 1)[0:2]
        [cube2_x, cube2_y] = np.where(self.roads == 1)[0:2]
        [cube3_x, cube3_y] = np.where(intersect_array == 1)[0:2]
        
        if(np.any(self.rails)):
            data[cube1_x,cube1_y,:] = [255, 0, 0]; #roads are red
        if(np.any(self.roads)):
            data[cube2_x,cube2_y,:] = [0, 255, 0]; #rails are blue
        if(np.any(intersect_array)):
            data[cube3_x,cube3_y,:] = [150, 150, 0]; #rails are blue
        img = Image.fromarray(data, 'RGB');
        self.game_image = img;
    
        return;
        
    def getImage(self):
        
        return self.game_image;
    
    def checkProgram(self):
        if(hasattr(self,'kill_event')):
            return self.kill_event.is_set();
        else:
            return False;
    
    def setEvent(self,event):
        self.kill_event = event;
    
    #functions below here will be moved into a game run state class
    

        

    
        
'''        
class ThreadManager:
    def __init__(self,thread_name,target_name):
        #self.thread = threading.Thread(target=target_name,daemon=True,name=thread_name);
        return;
        
    def start(self):
        self.thread.start();
        return
        
    def access_field(self):
        return;
        '''

'''
class App(tk.Frame):
    def __init__(self, root, window_size = [900, 600]):
        tk.Frame.__init__(self, root,width=window_size[0],height=window_size[1]);
        
        self.label = tk.Label(self);
        self.image = Image.fromarray(np.zeros((1,1,3), dtype=np.uint8), 'RGB');       
        self.update_display();
        
        return
    
    def assign_image_source(self, game_handle):
        self.game_img = game_handle;
        return;
    
    def update_image(self):
        if(hasattr(self,'game_img')):
            self.image = self.game_img();
            
        return;
    
    def update_display(self):
        self.update_image();
        
        image_size = 700;
        photo = self.image.resize((image_size, image_size),Image.Resampling.NEAREST);
        #photo = self.image;
        photo = ImageTk.PhotoImage(photo);
        self.label.configure(image=photo);
        self.label.image = photo; # keep a reference to prevent garbage collection
        self.label.place(relx=0.5, rely=0.5, anchor="center"); 
        # update every second
        self.after(1000, self.update_display);
        
        return;
        
    def assign_closing_protocol(self, kill_event):
        self.kill_event = kill_event;
        return;
        
    def closing_protocol(self):
        self.kill_event.set();
        self.after(500,root.destroy());
        return;
'''    

if __name__ == "__main__":
    #create GUI
    root = tk.Tk();
    app = App(root);
    app.pack(fill="both", expand=True);
    
    #create game space
    gameGraphics = railroadGraphics();
    
    
    #link GUI and game space with closure event
    kill_event = Event();
    
    app.assign_image_source(gameGraphics.getImage);
    app.assign_closing_protocol(kill_event);
    gameGraphics.setEvent(kill_event);

    game_thread = threading.Thread(target=gameGraphics.simulateGame,daemon=True);
    game_thread.start();
    
    
    root.protocol("WM_DELETE_WINDOW", app.closing_protocol)
    
    root.mainloop()
    