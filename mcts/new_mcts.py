from __future__ import division, print_function
import time, math, random, sys, utility
from useroracle import UserOracle
from copy import deepcopy

from train import parse_row
from model import ValueNetwork
vn = ValueNetwork('value_network_5items.h5')

# Antti Oulasvirta
# Nov 19, 2019
# Based on https://github.com/int8/monte-carlo-tree-search/tree/dd56e9440b43c64f1640af09704d8237d8049189/mctspy, https://github.com/pbsinclair42/MCTS/blob/master/mcts.py

# Rollout policy: random
def random_policy(state, oracle):
    total_rewards = [0.0,0.0,0.0]
    while not oracle.is_terminal(state):
        try:
            adaptation = random.choice(state.menu_state.possible_adaptations())
        except IndexError:
            raise Exception("Non-terminal state has no possible adaptations: " + str(state))
        state = state.take_adaptation(adaptation)
        if state.exposed:
            rewards = oracle.get_individual_rewards(state)[0]
            total_rewards = [a + b for a,b in zip(total_rewards, rewards)]                
    return total_rewards

# MCTS node
class TreeNode():
    exploration_const = 1/math.sqrt(2)
    def __init__(self, state, weights, parent = None):
        self.state = state # Menu now
        self.parent = parent
        self.num_visits = 0 # For tracking n in UCT
        self.total_rewards = [0.0,0.0,0.0] # For tracking q in UCT
        self.children = {} #Dictionary of format [adaptation, TreeNode]
        self.fully_expanded = False # Is it expanded already?
        self.weights = weights


    def Q(self):
        return sum([a * b for a,b in zip(self.weights,self.total_rewards)])/(1+self.num_visits)
    
    def U(self):
        return self.exploration_const * math.sqrt(math.log(self.parent.num_visits) / (1+self.num_visits))

    def best_child(self):
        return max(self.children.values(), key=lambda node: node.Q() + node.U())
    
    def select_leaf(self):
        current = self
        while current.fully_expanded:
            current = current.best_child()
        return current

    def expand(self):
        self.fully_expanded = True
        for adaptation in self.state.menu_state.possible_adaptations():
            self.add_child(adaptation)
    
    def add_child(self, adaptation):
        self.children[adaptation] = TreeNode(self.state.take_adaptation(adaptation), self.weights, parent = self)
    
    def backup(self, reward_estimates):
        current = self
        while current is not None:
            current.num_visits += 1
            current.total_rewards = [a+b for a,b in zip(current.total_rewards, reward_estimates)]
            current = current.parent
        
    def __str__(self):
        return str(self.state) + "," + str(self.total_rewards)

def search(state, oracle, weights, time_limit = None, num_iterations = 20):
    root = TreeNode(state, weights)
    rollout = random_policy
    if time_limit != None:
        end_time = time.time() + time_limit/1000
        while time.time() < end_time:
            leaf = root.select_leaf()
            reward_estimates = rollout(root.state, oracle)
            leaf.backup(reward_estimates)
            leaf.expand()

    else:
        for _ in range(num_iterations):
            leaf = root.select_leaf()
            reward_estimates = rollout(root.state, oracle)
            leaf.backup(reward_estimates)
            leaf.expand()
    
    # Finished building the MCTS tree in the given limit
    best_num_visits = 0
    best_adaptations = []
    for adaptation,child in root.children.items():
        if child.num_visits > best_num_visits:
            best_num_visits = child.num_visits
            best_adaptations = [adaptation]
        elif child.num_visits == best_num_visits:
            best_num_visits = child.num_visits
            best_adaptations.append(adaptation)
    
    # best_child = random.choice(best_nodes)
    best_adaptation = random.choice(best_adaptations)
    return best_adaptation

