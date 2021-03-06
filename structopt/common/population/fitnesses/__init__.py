import functools
import logging
import importlib
import numpy as np

import structopt
from . import LAMMPS, FEMSIM
from structopt.tools import root, single_core, parallel


class Fitnesses(object):
    """Holds the parameters for each fitness module and defines a utility function to compute the fitnesses for each fitness module."""

    @single_core
    def __init__(self, parameters):
        self.parameters = parameters
        self.modules = [globals()[module] for module in self.parameters]


    @parallel
    def fitness(self, population):
        """Perform the fitness calculations on an entire population.

        Args:
            population (Population): the population to evaluate
        """
        fitnesses = np.zeros((len(population),), dtype=np.float)
        # Run each fitness module on the population
        for i, module in enumerate(self.modules):
            module_name = module.__name__.split('.')[-1]
            module_parameters = self.parameters[module_name]

            if logging.parameters.rank == 0:
                print("Running fitness {} on the entire population".format(module_name))

            parameters = getattr(module_parameters, 'kwargs')
            fits = module.fitness(population, parameters=parameters)

            # Calculate the full objective function with weights
            weight = getattr(module_parameters, 'weight')
            fits = np.multiply(fits, weight)
            fitnesses = np.add(fitnesses, fits)

        self.post_processing(fitnesses)
        return fitnesses

    @single_core
    def post_processing(self, fitnesses):
        logger = logging.getLogger("output")
        logger.info("Total fitnesses for the population: {} (rank {})".format(fitnesses, logging.parameters.rank))

