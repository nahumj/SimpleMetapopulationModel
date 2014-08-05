"""
Main file
"""
import random
import collections
import numpy

NUMBER_OF_SUBPOPULATIONS = 10
SUBPOPULATION_SIZE = 1000
ANCESTOR_FITNESS = 1
ANCESTOR_MUTATION_RATE = 0.001
MIGRATION_RATE = 0.001
MUTANT_MEAN_FITNESS = 1

def get_new_mutant_fitness():
    return random.expovariate(MUTANT_MEAN_FITNESS)

def create_initial_metapopulation():
    subpopulations = []
    for i in range(NUMBER_OF_SUBPOPULATIONS):
        subpopulation = Subpopulation()
        subpopulation.add_individuals([ANCESTOR_FITNESS] * SUBPOPULATION_SIZE)
        subpopulations.append(subpopulation)
    return Metapopulation(subpopulations)

class Metapopulation(object):
    def __init__(self, subpopulations):
        self.subpopulations = subpopulations

    def migrate(self):
        """
        Collects an equal number of migrants from every subpopulation,
        then shuffles and returns the same number of random organisms back.
        """
        number_of_migrants = int(SUBPOPULATION_SIZE * MIGRATION_RATE)
        migrants = Subpopulation()
        for subpopulation in self.subpopulations:
            migrants.immigration(subpopulation.emigration(number_of_migrants))
        for subpopulation in self.subpopulations:
            immigrant_subpopulation = migrants.emigration(
                    number_of_migrants)
            subpopulation.immigration(immigrant_subpopulation)

    def advance_generation(self):
        for subpopulation in self.subpopulations:
            subpopulation.select()
            subpopulation.mutate()
        self.migrate()

    def __repr__(self):
        return "{}".format(self.subpopulations)

    def get_mean_fitness(self):
        sum_fitnesses = sum(subpopulation.get_mean_fitness()
                for subpopulation in self.subpopulations)
        return sum_fitnesses / len(self.subpopulations)

class Subpopulation(object):
    def __init__(self):
        """
        Creates an empty subpopulation.
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

        self.organisms = self._choose_organisms(self.size,
                weighted_by_fitness=True)
        # Remove mutant classes with zero abundances
        self.organisms += collections.Counter()

    def _choose_organisms(self, number_of_organsims, weighted_by_fitness):
        """
        Selects organisms in proportion to their abundances (with optional
        weighing by fitness). Returns a counter of organisms.
        """
        items = list(self.organisms.items())
        fitnesses, abundances = zip(*self.organisms.items())
        if weighted_by_fitness:
            probabilities = numpy.multiply(fitnesses, abundances)
        else:
            probabilities = abundances
        children = choose_weighted_with_replacement(number_of_organsims,
                probabilities)
        fitness_abundance_pairs = zip(fitnesses, children)
        return collections.Counter(dict(fitness_abundance_pairs))

    def emigration(self, number_of_organisms):
        """
        Returns an iterable of random organisms removed from this population.
        """
        emigrants = Subpopulation()
        emigrants.size = number_of_organisms
        emigrants.organisms = self._choose_organisms(number_of_organisms,
                weighted_by_fitness=False)
        self.organisms -= emigrants.organisms
        self.size -= emigrants.size
        return emigrants

    def immigration(self, immigrants):
        """
        Adds a given subpopulation to this subpopulation.
        """
        self.size += immigrants.size
        self.organisms += immigrants.organisms

    def __repr__(self):
        return repr(self.organisms.items())

    def get_mean_fitness(self):
        items = list(self.organisms.items())
        fitnesses, abundances = zip(*self.organisms.items())
        fitness_density = numpy.multiply(fitnesses, abundances)
        return sum(fitness_density) / self.size

def choose_weighted_with_replacement(number, values):
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
    return choose_weighted_with_replacement(number, values)
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

    draw_locations = {}
    while len(draw_locations) < number:
        location = choose_location()
        if location in draw_locations:
            continue
        draw_locations.add(location)
    category_indices = zip(*draw_locations)[0]
    print(category_indices)



def normalize(array):
    """
    Adjusts numpy array sum to 1
    """
    return array / numpy.sum(array)


if __name__ == "__main__":
    meta = create_initial_metapopulation()
    for i in range(50):
        meta.advance_generation()
        print(meta.get_mean_fitness())

