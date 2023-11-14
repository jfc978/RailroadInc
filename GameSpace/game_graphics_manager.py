# -*- coding: utf-8 -*-
"""
Created on Thu Apr 27 20:35:43 2023

@author: James
"""

import tkinter as tk
import threading
from railroad_inc_graphics import railroadGraphics
from threading import Event


class gameGraphicsManager():
    def __init__(self, appScheme, gameScheme):
        
        #create GUI
        self.root = tk.Tk();
        self.app = appScheme(self.root);
        self.app.pack(fill="both", expand=True);
        
        #create game space
        self.gameSpace = gameScheme;
        self.gameGraphics = railroadGraphics();
        self.gameSpace.assignGraphicsManager(self.gameGraphics);
        
        
        #link GUI and game space with closure event
        kill_event = Event();
        
        self.app.assign_image_source(self.gameGraphics.getImage);
        self.app.assign_closing_protocol(kill_event);
        self.gameGraphics.setEvent(kill_event);
        self.root.protocol("WM_DELETE_WINDOW", self.app.closing_protocol);

    def start(self):
        
        #start game thread
        #self.gameSpace.runGame();
        game_thread = threading.Thread(target=self.gameSpace.runGame,daemon=True); #repeat action?
        game_thread.start();
        print('Number of active threads - ',threading.active_count());
        #start graphics (loops current thread over main loop, game thread continues)
        self.root.mainloop()
        
        
        
        