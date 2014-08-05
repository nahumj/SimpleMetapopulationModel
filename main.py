"""
Main file
"""
import random
import collections
import numpy

NUMBER_OF_SUBPOPULATIONS = 10
SUBPOPULATION_SIZE = 100
ANCESTOR_FITNESS = 1
ANCESTOR_MUTATION_RATE = 0.1
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
    def __init__(self, organisms):
        """
        Creates a subpopulation from an iterable of organisms
        """
        self.size = len(organisms)
        self.organisms = collections.Counter(organisms)

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
        """
        Seperates the fitnesses from their abundance, then multiplies them,
        then draws from that multinomial distribution to generate the next
        generation.
        """

        self.organisms = self._choose_organisms(self.size,
                weighted_by_fitness=True)
        # Remove mutant classes with zero abundances
        self.organisms += collections.Counter()

    def _choose_organisms(self, number_of_organsims, weighted_by_fitness):
        """
        Selects organisms in proportion to their abundances (with optional
        weighing by fitness)
        """
        items = list(self.organisms.items())
        fitnesses, abundances = zip(*self.organisms.items())
        if weighted_by_fitness:
            probabilities = numpy.multiply(fitnesses, abundances)
        else:
            probabilities = abundances
        children = choose_weighted(number_of_organsims, probabilities)
        fitness_abundance_pairs = zip(fitnesses, children)
        return collections.Counter(dict(fitness_abundance_pairs))

    def emigration(self, number_of_organisms):
        """
        Returns a list of random organisms removed from this population.
        """
        emigrants = self._choose_organisms(number_of_organisms,
                weighted_by_fitness=False)
        self.organisms -= emigrants
        return emigrants.elements()

    def __repr__(self):
        return repr(self.organisms.items())

def choose_weighted(number, values):
    """
    Chooses number of times weightes by the value array
    """
    probabilities = normalize(values)
    return numpy.random.multinomial(number, probabilities)

def normalize(array):
    "Adjusts numpy array sum to 1"
    return array / numpy.sum(array)


if __name__ == "__main__":
    sub = Subpopulation([ANCESTOR_FITNESS] * 100)
    sub.mutate()
    sub.select()
    print(sub)
    print(list(sub.emigration(10)))
    print(sub)

