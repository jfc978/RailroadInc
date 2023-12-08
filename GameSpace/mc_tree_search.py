# -*- coding: utf-8 -*-
"""
Monte Carlo Tree Search

@author: Owner
"""
import numpy as np;
import random;

class MonteCarloSearchTree():
    def __init__(self, moveGenerator, boardEvaluator, winEvaluator, startingPlayer, moveMaker):
        self.weight = 0.95; # recommended 1.4 for rewards between [0,1], 1.0-0.8
        self.neural_weight = 0.1; #0.5->1->0.1
        self.resources = 60;
        self.roll_max_iter = 50;
        self.roll_max_depth = 8;
        self.generator = moveGenerator;
        self.evaluator = boardEvaluator;
        self.indexMove = moveMaker;
        self.winLoss = winEvaluator;
        self.player = startingPlayer;
        self.active_children = [];
        return;
        
    def predict(self, values, boardState):
        [legalVector, legalMoves, nextPlayer] = self.generator(boardState,self.player);
        
        
        if(len(legalMoves)==0):
            score = self.winLoss(boardState);
            return [None,score];
        
        # create root of tree
        self.root = Node(boardState, 0, None,self.player);
        
        counter = 0;
        # evaluate all children through value network
        for i,x in enumerate(values):
            # create new node for legal moves
            if(x):
                nodeValue = values[i] + self.winLoss(legalMoves[counter]); #+ self.evaluator(legalMoves[counter]);
                newNode = Node(legalMoves[counter], nodeValue, self.root, nextPlayer[counter]);
                [net_wins, num_games] = self.rollout(newNode);  
                newNode.backprop(net_wins, num_games);
                
                self.root.children.append(newNode);
                self.active_children.append(newNode);
                counter += 1;
        
        # perform MCTS
        iterations = 0;
        
        while(iterations < self.resources):
            iterations += 1;
            
            # select best node
            targetNode = self.select(self.active_children);
            #self.active_children.remove(targetNode);
            
            # expand node
            [self.active_children, unexploredChildren] = self.expand(targetNode);
            if(unexploredChildren == 0):
                self.active_children.remove(targetNode);
            
            # rollout
            [net_wins, num_games] = self.rollout(targetNode);
            
            # backprop
            targetNode.backprop(net_wins, num_games);
            #print("MC Iteration ", iterations)
        
        # find best child nodes
        best_value = -1;
        most_visits = 0;
        boards = [];
        values = [];
        ucbs = [];
        for node in self.root.children:
            boards.append(node.boardSpace);
            ucbs.append(self.get_ucb(node));
            win_value = 0.5 + node.wins/(2*node.games); #must be between 0 and 1, 0.5 suggests unknown
            values.append([win_value, 1-win_value])
            node_visits = node.visits;
            node_score = node.pos_value + node.wins/node.games; #(node.visits/self.resources) + (node.wins/node.games);
            best_node_condition = ((node_visits > most_visits) or (node_visits == most_visits and node_score > best_value));
            if(best_node_condition):
                most_visits = node_visits;
                best_value = node_score;
                best_node = node;
                
        sub_ucbs = [];
        for node in best_node.children:
            sub_ucbs.append(self.get_ucb(node));
            
        print("Move Choice - Greedy (",best_node.wins/best_node.games,\
              "), Learned (",best_node.pos_value * self.neural_weight,\
              "), Explorative (",self.weight * np.sqrt(np.log(best_node.parent.visits)/best_node.visits),")");
        print("Visits (", best_node.visits,")\n");
        return [best_node.boardSpace, values, [ucbs, sub_ucbs]];
        

    def select(self, nodes):
        # find next target node based on MCTS formula
        best_value = -1;
        best_node = nodes[0];
        for i,x in enumerate(nodes):
            value = self.get_ucb(x)
            if(value > best_value):
                best_value = value
                best_node = x;
        
        return best_node;
    
    def evaluateNode(self, boardSpaces):
        values = self.evaluator(boardSpaces);
        for i,x in enumerate(boardSpaces):
            winLoss = self.winLoss(x);
            if winLoss != 0:
                values[i] = winLoss/self.neural_weight;
        return values;
            

            
    def expand(self, node):
        # evaluate win condition at node
        return node.expand(self.generator, self.evaluateNode, self.active_children);
    
    def rollout(self, targetNode):
        #randomly choose moves until end of game
        #save no information
        iterations = 0;
        max_iterations = self.roll_max_iter;
        [baseVector, baseMoves] = self.generator(targetNode.boardSpace, targetNode.player, build=False);
        
        score = 0;
        while iterations < max_iterations:
            depth = 0;
            max_depth = self.roll_max_depth; 
            
            #iterate down from target node
            children = np.where(baseVector==1)[0];
            currentPlayer = targetNode.player;
            previous_board = np.copy(targetNode.boardSpace);
            
            while depth < max_depth:
                # check if legal moves exist
                if(len(children) == 0):
                    if(currentPlayer == self.player):
                        score += -1;
                    else:
                        score += 1;
                    break;
                    
                #pick a random child node
                sample = random.choice(children);
                rollout_move = self.indexMove(previous_board, random.choice(children), currentPlayer);
                move_value = self.winLoss(rollout_move);
                
                #if game over
                if(move_value != 0):
                    score += move_value;
                    break;
                
                currentPlayer = 1 - currentPlayer;
                [vector, children] = self.generator(rollout_move, currentPlayer, build=False);
                previous_board = rollout_move;
                children = np.where(vector==1)[0];
                depth += 1;
            
            iterations += 1;
        
        return [score, iterations];
    
    def get_ucb(self, node):
        greedy = node.wins/node.games;
        learned = node.pos_value * self.neural_weight;
        explorative = self.weight * np.sqrt(np.log(node.parent.visits)/node.visits)
        return greedy + learned + explorative;
        

class Node():
    def __init__(self, boardSpace, value, parent, player):
        #score keeping
        self.games = 1;
        self.wins = 0;
        #ucb values
        self.pos_value = value;
        self.visits = 1;
        #helpful variables
        self.boardSpace = boardSpace;
        self.parent = parent;
        self.player = player; #whos turn is it now
        self.children = [];
        self.inactive_children = [];
        return;

    def visit(self):
        self.visits += 1;
        if(self.parent is not None):
            self.parent.visits += 1;
        return;
    
    def expand(self, moveGenerator, evaluator, active_children):
        expansionModifier = 0.98;
        expansionNodes = 2;
        # update visits
        self.visit();
        
        if(len(self.inactive_children) == 0):
        
            # find all legal moves
            [vector, legalMoves, next_player] = moveGenerator(self.boardSpace,self.player);
            if(len(legalMoves) == 0):
                return active_children;
            values = evaluator(legalMoves);
            # create nodes in active search and as children
            for i,x in enumerate(legalMoves):
                # create new node for legal moves
                newNode = Node(x, values[i]*0.98, self, next_player[i]); #penalty to promote searching other branches
                self.children.append(newNode);
                
            self.inactive_children = list(range(0,len(legalMoves)));
            
        #add only a few nodes
        i=0;
        num_children = len(self.children);
        while(i<=expansionNodes):
            if(len(self.inactive_children) == 0):
                break;
            best_value = 0;
            best_child = self.inactive_children[0];
            for x in self.inactive_children:
                value = self.children[x].pos_value;
                if value > best_value:
                    best_value = value;
                    best_child = x;
                    
            self.inactive_children.remove(best_child);
            active_children.append(self.children[best_child]);
            i+=1;
                
        return [active_children, len(self.inactive_children)];
        
    def backprop(self, wins, games):
        self.wins += wins;
        self.games += games;
        if(self.parent is not None):
            self.parent.backprop(wins, games);
        return;
        
        