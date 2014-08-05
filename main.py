"""
Main file
"""
import random

NUMBER_OF_SUBPOPULATIONS = 10
SUBPOPULATION_SIZE = 100
random_gen = random.Random()

def mutation_generator():
    while True:
        yield random.expovariate(1)

if __name__ == "__main__":
    mut_gen = mutation_generator()
    for i in range(10):
        print(next(mut_gen))

