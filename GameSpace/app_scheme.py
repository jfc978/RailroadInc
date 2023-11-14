# -*- coding: utf-8 -*-
"""
Created on Thu Apr 27 20:43:01 2023

@author: James
"""
import numpy as np
import tkinter as tk
from PIL import Image, ImageTk


class AppScheme(tk.Frame):
    def __init__(self, root, window_size):
        pass;
    def assign_image_source(self, game_handle):
        pass;
    def update_image(self):
        pass;
    def update_display(self):
        pass;
    def assign_closing_protocol(self, kill_event):
        pass;
    def closing_protocol(self):
        pass;
        


class App(AppScheme):
    def __init__(self, root, window_size = [900, 800]):
        tk.Frame.__init__(self, root,width=window_size[0],height=window_size[1]);
        self.root = root;
        self.label = tk.Label(self);
        self.image = Image.fromarray(np.zeros((1,1,3), dtype=np.uint8), 'RGB');       
        self.update_display();
        print('Starting Display')
        
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
        self.after(500,self.root.destroy());
        return;