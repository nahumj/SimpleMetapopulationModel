"""
Main file
"""
import random
import collections
import numpy

NUMBER_OF_SUBPOPULATIONS = 10
SUBPOPULATION_SIZE = 100
ANCESTOR_FITNESS = 0.1
ANCESTOR_MUTATION_RATE = 0.01
MIGRATION_RATE = 0.001
MUTANT_MEAN_FITNESS = 1

def get_new_mutant_fitness():
    return random.expovariate(MUTANT_MEAN_FITNESS)

def create_initial_population():
    subpopulations = []
    for i in range(NUMBER_OF_SUBPOPULATIONS):
        subpopulations.append(Subpopulation(SUBPOPULATION_SIZE))
    return Metapopulation(subpopulations)

class Metapopulation(object):
    def __init__(self, subpopulations):
        self.subpopulations = subpopulations

    def migrate(self):
        pass

class Subpopulation(object):
    def __init__(self, size):
        self.organisms = collections.Counter()
        self.organisms[ANCESTOR_FITNESS] = size

    def mutate(self):
        """
        Determines the number of ancestor to mutant mutations by drawing
        from a binomial distribution. Then for each mutant determines its
        new fitness and adjusts the Counter appropiately.
        """
        number_of_ancestors = self.organisms[ANCESTOR_FITNESS]
        number_of_mutants = numpy.random.binomial(number_of_ancestors,
                ANCESTOR_MUTATION_RATE)
        for _ in range(number_of_mutants):
            self.organisms[ANCESTOR_FITNESS] -= 1
            mutant_fitness = get_new_mutant_fitness()
            self.organisms[mutant_fitness] += 1

    def select(self):
        pass

    def __repr__(self):
        return repr(self.organisms.items())




if __name__ == "__main__":
    sub = Subpopulation(1000)
    print(sub)
    sub.mutate()
    print(sub)
