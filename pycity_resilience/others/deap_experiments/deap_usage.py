#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

"""
from __future__ import division


import random
import deap.base as base
import deap.creator as creator
import deap.tools as tools

#  Type creation
#  ######################################################

#  Example to create a FitnessMin class
creator.create("FitnessMin", base.Fitness, weights=(-1.0,))

#  Create an individual, that is derived from a list with a fitness attribute
creator.create("Individual", list, fitness=creator.FitnessMin)


#  Initialization --> Fill types with values
#  ######################################################

ind_size = 10

#  A toolbox for evolution that contains the evolutionary operators
toolbox = base.Toolbox()

#  Register a *function* in the toolbox under the name *alias*.
toolbox.register("attribute", random.random)
toolbox.register("individual", tools.initRepeat, creator.Individual,
                 toolbox.attribute, n=ind_size)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

#  Operators
#  ######################################################
def evaluate(individual):
    return sum(individual),

toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=1, indpb=0.1)
toolbox.register("select", tools.selTournament, tournsize=3)
toolbox.register("evaluate", evaluate)

def main():
    pop = toolbox.population(n=50)
    CXPB, MUTPB, NGEN = 0.5, 0.2, 40

    # Evaluate the entire population
    fitnesses = map(toolbox.evaluate, pop)
    for ind, fit in zip(pop, fitnesses):
        ind.fitness.values = fit

    for g in range(NGEN):
        # Select the next generation individuals
        offspring = toolbox.select(pop, len(pop))
        # Clone the selected individuals
        offspring = map(toolbox.clone, offspring)

        # Apply crossover and mutation on the offspring
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < CXPB:
                toolbox.mate(child1, child2)
                del child1.fitness.values
                del child2.fitness.values

        for mutant in offspring:
            if random.random() < MUTPB:
                toolbox.mutate(mutant)
                del mutant.fitness.values

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        # The population is entirely replaced by the offspring
        pop[:] = offspring

    return pop

if __name__ == '__main__':

    pop = main()
    print(pop)