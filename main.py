"""
Main file
"""
import random
import collections

NUMBER_OF_SUBPOPULATIONS = 10
SUBPOPULATION_SIZE = 100

def mutation_generator():
    while True:
        yield random.expovariate(1)

def create_initial_population():
    metapopulation = []
    for i in range(NUMBER_OF_SUBPOPULATIONS):
        subpopulation()

class Metapopulation(object):
    def __init__(self, subpopulations):
        self.subpopulations = subpopulations

    def migrate(self):
        pass

class Subpopulation(object):
    def __init__(self, ancestor, size):
        self.organisms = collections.Counter()
        self.organisms[ancestor] = size

    def mutate(self):
        pass

    def select(self):
        pass

    def __repr__(self):
        return repr(self.organisms.items())




if __name__ == "__main__":
    sub = Subpopulation(0.4, 10)
    print(sub)
