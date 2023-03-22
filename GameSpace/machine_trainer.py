# -*- coding: utf-8 -*-
"""
Machine Trainer
Trains separate networks against each other to select the best network

@author: Owner
"""
import sys, os
import numpy as np
import pickle
import copy
from game_environment import NoMoves
from santorini_machine import GameAI
from board_illustrator import BoardGraphics

class Trainer():
    def __init__(self, m_one, m_two):
        self.player_one = m_one;
        self.player_two = m_two;
        self.isDisplay = False;
        
    def assignDisplay(self, display):
        self.display = display;
        self.isDisplay = True;
        return;
        
    def playGame(self):
        if(self.player_one.player == 0):
            activePlayer = self.player_one;
            waitingPlayer = self.player_two;
        else:
            activePlayer = self.player_two;
            waitingPlayer = self.player_one;
        
        game_over = False;
        
        move_history = [];
        
        move_count = 0;
        winner = 0;
        while (game_over is not True):
            #active player
            print(activePlayer.player, " is taking their turn");
            print("Move : ", move_count);
            #oldout = sys.stdout;
            #sys.stdout = open(os.devnull, 'w');
            #sys.stdout = oldout;
            moveChoice = activePlayer.takeTurn();
            #waiting player
            waitingPlayer.receiveMove(moveChoice);
            win = activePlayer.evaluateWinLoss(moveChoice);
            
            move_history.append([moveChoice, activePlayer.player]);

            
            #win conditions
            if(win == 1):
                print(activePlayer.player, " has won");
                game_over = True;
                winner = activePlayer.player;

            elif(win == -1):
                print(waitingPlayer.player, " has won");
                game_over = True;
                winner = waitingPlayer.player;
            
            #switch roles
            waitingPlayer, activePlayer = activePlayer, waitingPlayer;
            move_count += 1;
            
            #update display
            if(self.isDisplay):
                self.display.updateBoard(moveChoice, self.player_one.game.disectBoard);
            
        return [winner,move_history];
            
    def train(self):
        player_wins = np.zeros((1,2));
        ai_wins = np.zeros((1,2));
        num_games = 30;
        game_history = [];
        for i in range(num_games):
            print("\n", i, " of ", num_games, " complete");
            print("AI One : ", int(ai_wins[0][0]), " - AI Two : ", int(ai_wins[0][1]));
            #swap players
            m_one_p, m_two_p = self.player_one.player, self.player_two.player;
            self.player_one.startGame(m_two_p);
            self.player_two.startGame(m_one_p);
            
            #play game
            [winner,moves] = self.playGame();
            game_history.append([winner,moves]);
            player_wins[0][winner] += 1;
            
            if(winner == self.player_one.player):
                ai_wins[0][0] += 1;
                self.player_one.updateNetworks(1);
                self.player_two.updateNetworks(-1);
            else:
                ai_wins[0][1] += 1;
                self.player_one.updateNetworks(-1);
                self.player_two.updateNetworks(1);

        # Display Results
        print("Player one : ", player_wins[0][0], " wins\n")
        print("Player two : ", player_wins[0][1], " wins\n\n")
        print("AI one : ", ai_wins[0][0], " wins\n")
        print("AI two : ", ai_wins[0][1], " wins")
        
        # Save Models
        #cwd = os.getcwd();
        #self.player_one.save_models(cwd+'/AI_one_deep');
        #self.player_two.save_models(cwd+'/AI_two_deep');
        
        #agent1 = Agent(self.player_one.player,training = True);
        #agent2 = Agent(self.player_two.player,training = False);
        
        #agent1.opponent = agent2.path;
        #agent2.opponent = agent1.path;
        
        #agent1.iteration = 1;
        #agent2.iteration = 1;
        
        agent1_result = ai_wins[0][0]/num_games;
        #agent1.result = 3/20;
        
        agent2_result = ai_wins[0][1]/num_games;
        #agent2.result = 17/20;
        
        #agent1.save_models(cwd+'/AI_gen1_train1');
        #agent2.save_models(cwd+'/AI_gen1_opponent');
        
        return [[agent1_result,agent2_result], game_history];
        
class Agent_Organizer():
    def __init__(self, iterations, num_players):
        self.depth = iterations; #iterations to train
        self.current_depth = 0; 
        self.breadth = num_players; #players in each iteration
        self.results_grid = np.zeros((self.breadth, self.depth)); #store training results
        self.folder = os.getcwd(); #home folder
        
        self.paths = [];
        self.agents = []
        self.baseline = [];
        return;
        
    def set_fp(self, ai, gen):
        return self.folder + '/AI_' + str(ai) + '/gen_' + str(gen);
    
    def reload_progress(self): #may not be needed
        #search through all possible agents
        for d in range(0,self.depth):
            for i in range(0,self.breadth):
                try:
                    search_path = self.set_fp(i,d);
                    new_agent = Agent(0,load_path = search_path);
                    self.results_grid[i,d] = new_agent.result;
                    
                except:
                    pass;
            #check for reference agent
        return;
        
    def produce_generation(self):
        #generate possible paths
#        if(self.current_depth == 0):
        for i in range(0,self.breadth):
            if(self.current_depth == 0):
                try:
                    os.mkdir(self.folder + '/AI_' + str(i));
                except:
                    pass;
                self.paths.append(self.folder + '/AI_' + str(i));
            try:
                os.mkdir(self.set_fp(i,self.current_depth));
            except:
                pass;
        #comparison AI
        self.baseline.append(self.folder + '/AI_baseline');
        #generate agents
#        else: 
#            for i in range(0,self.breadth):
#                try:
#                    new_path = self.set_fp(i,self.current_depth);
#                    os.mkdir(new_path);
#                    if(self.current_depth != 0):
#                        best_path = self.find_best(self.current_depth-1);
#                        new_agent = Agent(0,load_path = best_path);
#                    else:
#                        new_agent = Agent(0);
#                    new_agent.save_models(new_path);
#                    self.agents.append(new_agent);
#                except:
#                    pass;
                
        #comparison AI
        if(self.current_depth == 0):
            try:
                os.mkdir(self.folder + '/AI_baseline' );
            except:
                pass;
        try:
            new_path = self.folder + '/AI_baseline' + '/gen_' + str(self.current_depth);
            os.mkdir(new_path);
        except:
            pass;
        return;
            
    def find_best(self, targetLayer):
        if(targetLayer == -1):
            return self.folder+'/AI_two_deep';
        
        scores = self.results_grid[:][targetLayer][0];
        best_idx = np.array(np.where(scores == np.max(scores)))[0][0];
        path = self.set_fp(best_idx,targetLayer);
        return path;
    
    def begin(self):
        graphics = BoardGraphics();
        for i in range(self.current_depth,self.depth):
            self.produce_generation();
            
            #select best network from previous generation
            best_path = self.find_best(self.current_depth-1);
            #generate AI to train against network
            adversary = Agent(1,training=False,load_path=best_path);
            adversary.save_models(self.folder + '/AI_baseline/gen_' + str(self.current_depth));
            
            self.train_generation(adversary, graphics);
            self.current_depth += 1;
            self.save_progress();
        return
    
    def train_generation(self,adversary, graphics):
        for i in range(0,self.breadth):
            #check existing data
            if(self.results_grid[i,self.current_depth] != 0):
                continue;
            
            #call train on agents
            agent = Agent(0);
            trainer = Trainer(agent.AI,adversary.AI);
            trainer.assignDisplay(graphics);
            [num_wins, game_history] = trainer.train();
            
            #save progress
            agent.assign_training(adversary,self.current_depth,num_wins[0]);
            agent.save_models(self.set_fp(i,self.current_depth));
            self.results_grid[i,self.current_depth] = num_wins[0];
        
        return;
    
    def save_progress(self):
        folder = os.getcwd();  
        with open(folder + '/organizer.pkl', 'wb') as outp:  # Overwrites any existing file.;            
            pickle.dump(self, outp, pickle.HIGHEST_PROTOCOL);
        return;
        
    def load_progress(self):
        folder = os.getcwd();  
        with open(folder + '/organizer.pkl', 'rb') as inp:  # Overwrites any existing file.;            
            agent = pickle.load(inp);
            self.depth = agent.depth;
            self.breadth = agent.breadth;
            self.results_grid = agent.results_grid;
            self.paths = agent.paths;
            self.current_depth = agent.current_depth;
        return;
        
        
class Agent():
    def __init__(self,player,training=True,load_path=None):
        self.player = player;
        self.isTraining = training;
        
        #generate default AI
        self.AI = GameAI(player,training = self.isTraining);
        
        self.opponent = None;
        self.iteration = None;
        self.result = 0;
        
        self.load_path = None;
        
        if(load_path is not None):
            self.load_models(load_path);
            self.load_path = load_path;
            
        return;
    
    def assign_training(self, opponent, iteration, result):
        self.opponent = opponent.load_path;
        self.iteration = iteration;
        self.result = result;
        return;
    
    def save_models(self, save_path):
        self.AI.save_models(save_path);
        model = copy.copy(self);
        del model.AI;
        with open(save_path + '/agent.pkl', 'wb') as outp:  # Overwrites any existing file.;            
            pickle.dump(model, outp, pickle.HIGHEST_PROTOCOL);
        return;
        
    def load_models(self, load_path):
        with open(load_path + '/agent.pkl', 'rb') as inp:
            agent = pickle.load(inp);
            self.opponent = agent.opponent;
            self.iteration = agent.iteration;
            self.result = agent.result;
            del agent;    
        self.AI = GameAI(self.player, self.isTraining);
        self.AI.load_models(load_path)
        return;
    
     
if __name__ == '__main__':
    #player = 0;
    #m_one = GameAI(0, training = True);
    #m_two = GameAI(1, training = False);
    #cwd = os.getcwd();
    #m_one.load_models(cwd+"/AI_one_deep/value_net",cwd+"/AI_one_deep/policy_net");
    #m_two.load_models(cwd+"/AI_two_deep/value_net",cwd+"/AI_two_deep/policy_net");
    #print("Begin Game")
    #trainer = Trainer(m_one,m_two);
    #graphics = BoardGraphics();
    #trainer.assignDisplay(graphics);
    #[num_wins, game_history] = trainer.train();
    
    print("Begin Game");
    ao = Agent_Organizer(1,2);
    ao.load_progress();
    ao.begin();
    
    
    