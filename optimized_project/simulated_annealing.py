import networkx as nx
from initial_solution import *
import numpy as np 
import math
import random
from nodes_generator import NodeGenerator
from animated_visualizer import *

class SimulatedAnnealing:
    def __init__(self, original_graph, temp, alpha, stopping_temp, stopping_iter, matrix_cost, B):
        ''' animate the solution over time

            Parameters
            ----------
            coords: array_like
                list of coordinates
            temp: float
                initial temperature
            alpha: float
                rate at which temp decreases
            stopping_temp: float
                temperature at which annealing process terminates
            stopping_iter: int
                interation at which annealing process terminates

        '''
        self.temp = temp
        self.alpha = alpha
        self.stopping_temp = stopping_temp
        self.stopping_iter = stopping_iter

        self.iteration = 1
        self.original_graph = original_graph
        self.sample_size = nx.number_of_nodes(self.original_graph)
        self.dist_matrix = matrix_cost
        self.budget = B
        
        self.graph = generate_random_tree(self.original_graph)
        # self.graph = mst(self.original_graph, self.dist_matrix)
        self.curr_solution = self.graph
        self.best_solution = self.curr_solution
        
        self.curr_weight = self.weight(self.curr_solution)
        self.initial_weight = self.curr_weight
        self.min_weight = self.curr_weight

        self.curr_diameter = self.calculate_diameter(self.curr_solution)
        self.initial_diameter = self.curr_diameter
        self.min_diameter = self.curr_diameter

        self.weight_list = [self.curr_weight]
        # self.diameter_list = [self.curr_diameter]
        
        self.solution_history = [self.curr_diameter]
        print('==============(LOG)==================')
        print('Initial weight: ', self.curr_weight)
        print('Initial diameter: ', self.curr_diameter)
        
    def weight(self, candidate):
        '''
        Calculate weight
        '''
        total_cost = 0
        for i,j in candidate.edges():
            total_cost += self.dist_matrix[i,j]

        return total_cost

    def calculate_diameter(self, candidate):
        e = nx.eccentricity(candidate)
        return e[max(e, key=e.get)]
    
    def acceptance_probability(self, candidate_weight):
        '''
        Acceptance probability using boltzmann:
        '''
        return math.exp(-abs(candidate_weight - self.curr_weight) / self.temp)

    def accept(self, candidate):
        '''
        Accept with probability 1 if candidate solution is better than
        current solution, else accept with probability equal to the
        acceptance_probability()
        '''
        
        
        candidate_diameter = self.calculate_diameter(candidate)
        candidate_weight = self.weight(candidate)
        
        penalty = 2
        if self.curr_weight <= candidate_weight:
            candidate_diameter += penalty
            
            if candidate_weight < self.min_weight:
                self.min_weight = candidate_weight
            
            if candidate_diameter < self.curr_diameter:
                candidate_diameter -= penalty
                self.curr_diameter = candidate_diameter
                self.curr_solution = candidate
                if candidate_diameter < self.min_diameter:
                    self.min_diameter = candidate_diameter
                    self.best_solution = candidate    
            else:
                candidate_diameter -= penalty
                if random.random() < self.acceptance_probability(candidate_diameter):
                    self.curr_diameter = candidate_diameter
                    self.curr_weight = candidate_weight
                    self.curr_solution = candidate
        else:
            # and candidate_weight <= self.budget
            if candidate_weight < self.min_weight:
                self.min_weight = candidate_weight
            
            if candidate_diameter < self.curr_diameter:
                self.curr_diameter = candidate_diameter
                self.curr_solution = candidate
            if candidate_diameter < self.min_diameter:
                self.min_diameter = candidate_diameter
                self.best_solution = candidate
            else:
                if random.random() < self.acceptance_probability(candidate_diameter):
                    self.curr_diameter = candidate_diameter
                    self.curr_solution = candidate
            

    def anneal(self):
        '''
        Annealing process 
        '''
        while self.temp >= self.stopping_temp and self.iteration < self.stopping_iter:
            candidate = NodeGenerator(self.original_graph, self.curr_solution).generate()

            self.accept(candidate)
            self.temp *= self.alpha
            self.iteration += 1
            # self.weight_list.append(self.curr_weight)
            # self.diameter_list.append(self.curr_solution)
            self.solution_history.append(self.calculate_diameter(self.curr_solution))

        
        print('Minimum weight: ', self.min_weight, " ", 'Improvement: ',
              round((self.initial_weight - self.min_weight) / (self.initial_weight), 4) * 100, '%')
        print('Minimum diameter: ', self.min_diameter, " ", 'Improvement: ',
              round((self.initial_diameter - self.min_diameter) / (self.initial_diameter), 4) * 100, '%')
        print('Tempo total(s): ')
        print('=====================================')

    def animateSolutions(self):        
        animateTSP(self.solution_history)

    def plotLearning(self):
        tam = len(self.solution_history)

        fig = plt.figure(figsize=(18, 8))
        plt.plot([i for i in range(tam, 0, -1)], self.solution_history)

        line_init = plt.axhline(y=self.initial_diameter, color='r', linestyle='--')
        line_min = plt.axhline(y=self.min_diameter, color='g', linestyle='--')
        
        # print(self.solution_history)
        plt.xlim(tam, self.temp)
        # plt.ylim(min(self.solution_history)-1, max(self.solution_history)+1)
        
        
        plt.legend([line_init, line_min], ['Initial Diameter', 'Optimized Diameter'])
        plt.ylabel('Diameter')
        plt.xlabel('Temperature')
        plt.show()