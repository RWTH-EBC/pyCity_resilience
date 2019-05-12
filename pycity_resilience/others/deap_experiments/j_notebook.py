#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The problem is very simple, we search for a 1 filled solution
"""
from __future__ import division

import random
from deap import base, creator, tools, algorithms

#  Type creation (default: Fitness and individual)
#  #################################################################
#  Create Fitness
#  Maximizing --> replacing virtual weights by attribute 1.0;
creator.create("FitnessMax", base.Fitness, weights=(1.0,))

#  Alternative: creator.create("FitnessMin", base.Fitness, weights=(-1.0,))

#  Creates individual, inheritance of list
#  Holds fitnesss value of FitnessMax type
creator.create("Individual", list, fitness=creator.FitnessMax)

#  Created classes are made available in creater module

#  Initialize objects of new classes
#  ################################################################
ind = creator.Individual([1, 0, 1, 1, 0])

print(ind)
print(type(ind))
print(type(ind.fitness))
print()

#  Toolbox
#  ################################################################
#  Container holding functions, that are stored under their name aliases

toolbox = base.Toolbox()

#  Function to call random integer between 0 and 1
toolbox.register("attr_bool", random.randint, 0, 1)

#  Uses tools.initRepeat to fill individual with random 0, 1 integers
toolbox.register("individual", tools.initRepeat,
                 creator.Individual, toolbox.attr_bool, n=10)

#  Generate population of individuals
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

bit = toolbox.attr_bool()
ind = toolbox.individual()
pop = toolbox.population(n=3)

print("bit is of type %s and has value\n%s" % (type(bit), bit))
print(
    "ind is of type %s and contains %d bits\n%s" % (type(ind), len(ind), ind))
print("pop is of type %s and contains %d individuals\n%s" % (
type(pop), len(pop), pop))
print()

#  Evaluate function
#  ################################################################

#  Count nb of 1 in individual
def evalOneMax(individual):
    return sum(individual),

#  Genetic Operators
#  ################################################################
#  Registering the operators and their default arguments in the toolbox

toolbox.register("evaluate", evalOneMax)
toolbox.register("mate", tools.cxTwoPoint)

#  indpb: Probability of each attribute to be mutated
toolbox.register("mutate", tools.mutFlipBit, indpb=0.10)
toolbox.register("select", tools.selTournament, tournsize=3)

ind = toolbox.individual()
print(ind)
toolbox.mutate(ind)
print(ind)

mutant = toolbox.clone(ind)
print(mutant is ind)
print(mutant == ind)

#  Evolving the population
#  ################################################################

def main():
    import numpy

    pop = toolbox.population(n=50)
    hof = tools.HallOfFame(1)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", numpy.mean)
    stats.register("min", numpy.min)
    stats.register("max", numpy.max)

    pop, logbook = algorithms.eaSimple(pop, toolbox, cxpb=0.5, mutpb=0.2,
                                       ngen=10, stats=stats, halloffame=hof,
                                       verbose=True)

    return pop, logbook, hof


if __name__ == "__main__":
    pop, log, hof = main()
    print(
        "Best individual is: %s\nwith fitness: %s" % (hof[0], hof[0].fitness))

    import matplotlib.pyplot as plt

    gen, avg, min_, max_ = log.select("gen", "avg", "min", "max")
    plt.plot(gen, avg, label="average")
    plt.plot(gen, min_, label="minimum")
    plt.plot(gen, max_, label="maximum")
    plt.xlabel("Generation")
    plt.ylabel("Fitness")
    plt.legend(loc="lower right")
    plt.show()