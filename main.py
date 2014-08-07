"""
Main file: Ben's version
"""
import random
import collections
import numpy

NUMBER_OF_SUBPOPULATIONS = 10
SUBPOPULATION_SIZE = 1000
ANCESTOR_FITNESS = 1
ANCESTOR_MUTATION_RATE = 0.001
MIGRATION_RATE = 0.001
MUTANT_MEAN_FITNESS_EFFECT = 1

def get_new_mutant_fitness():
    return ANCESTOR_FITNESS + random.expovariate(MUTANT_MEAN_FITNESS_EFFECT)

def create_initial_metapopulation():
    subpopulations = []
    for i in range(NUMBER_OF_SUBPOPULATIONS):
        subpopulation = Population()
        subpopulation.add_individuals([ANCESTOR_FITNESS] * SUBPOPULATION_SIZE)
        subpopulations.append(subpopulation)
    return Metapopulation(subpopulations)

class Metapopulation(object):
    def __init__(self, subpopulations):
        """
        Creates a metapopulation composed of a list of subpopulations.
        """
        self.subpopulations = subpopulations

    def migrate(self):
        """
        Collects an equal number of migrants from every subpopulation,
        then shuffles and returns the same number of random organisms back.
        """
        number_of_migrants = int(SUBPOPULATION_SIZE * MIGRATION_RATE)
        migrants_pool = Population()
        for population in self.subpopulations:
            migrants_pool.immigration(population.emigration(number_of_migrants))
        for population in self.subpopulations:
            immigrants = migrants_pool.emigration(
                    number_of_migrants)
            population.immigration(immigrants)

    def advance_generation(self):
        """
        Hopefully self-explaining.
        """
        for population in self.subpopulations:
            population.select()
            population.mutate()
        self.migrate()

    def __repr__(self):
        return "{}".format(self.subpopulations)

    def get_mean_fitness(self):
        """
        Returns the population mean fitness
        """
        total_population = Population()
        for population in self.subpopulations:
            total_population.immigration(population)

        return total_population.get_mean_fitness()

class Population(object):
    def __init__(self):
        """
        Creates an empty population.
        """
        self.size = 0
        self.organisms = collections.Counter()

    def add_individuals(self, organisms):
        """
        Adds organisms from a list
        """
        self.size += len(organisms)
        self.organisms.update(organisms)


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
        fitnesses, abundances = self._get_fitnesses_and_abundances()
        probabilities = numpy.multiply(fitnesses, abundances)
        children = choose_with_replacement(self.size,
                probabilities)
        self._set_fitnesses_and_abundances(fitnesses, children)
        # Remove mutant classes with zero abundances
        self.organisms += collections.Counter()

    def _get_fitnesses_and_abundances(self):
        """
        Helper function that returns the vector of fitnesses and their
        abundances.
        """
        items = list(self.organisms.items())
        return zip(*self.organisms.items())

    def _set_fitnesses_and_abundances(self, fitnesses, abundances):
        """
        Helper function that sets the counter denoting the organisms'
        fitness and abundances. Note: doesn't adjust the size attribute.
        """
        fitness_abundance_pairs = zip(fitnesses, abundances)
        self.organisms = collections.Counter(dict(fitness_abundance_pairs))

    def emigration(self, number_of_organisms):
        """
        Returns an iterable of random organisms removed from this population.
        """
        emigrants = Population()
        emigrants.size = number_of_organisms
        fitnesses, abundances = self._get_fitnesses_and_abundances()
        new_abundances = choose_without_replacement(number_of_organisms,
                abundances)
        emigrants._set_fitnesses_and_abundances(fitnesses, new_abundances)
        self.organisms -= emigrants.organisms
        self.size -= emigrants.size
        return emigrants

    def immigration(self, immigrants):
        """
        Adds a given population to this population.
        """
        self.size += immigrants.size
        self.organisms += immigrants.organisms

    def __repr__(self):
        return repr(self.organisms)

    def get_mean_fitness(self):
        """
        Returns the population's mean fitness.
        """
        fitnesses, abundances = self._get_fitnesses_and_abundances()
        fitness_density = numpy.multiply(fitnesses, abundances)
        return sum(fitness_density) / self.size

def choose_with_replacement(number, values):
    """
    Chooses number of times weighted by the value array
    """
    probabilities = normalize(values)
    return numpy.random.multinomial(number, probabilities)

def choose_without_replacement(number, values):
    """
    Given a number of draws and a vector of items in each category, returns
    the number of draws which landed in each category as a vector.
    """
    total = sum(values)
    assert number <= total

    def choose_location():
        tally = 0
        category_index = 0
        random_value = random.random()
        while category_index < len(values) - 1:
            tally += values[category_index]
            if random_value < tally / total:
                break
            category_index += 1
        organism_index = random.randrange(values[category_index])
        return category_index, organism_index

    draw_locations = set()
    while len(draw_locations) < number:
        location = choose_location()
        if location in draw_locations:
            continue
        draw_locations.add(location)
    category_indices = list(zip(*draw_locations))[0]
    count_of_categories = collections.Counter(category_indices)
    draws = [0] * len(values)
    for category_index, abundance in count_of_categories.items():
        draws[category_index] = abundance
    return draws


def normalize(array):
    """
    adjusts numpy array sum to 1
    """
    return array / numpy.sum(array)


if __name__ == "__main__":
    meta = create_initial_metapopulation()
    for i in range(50):
        meta.advance_generation()
        print(meta.get_mean_fitness())
    print(meta)
