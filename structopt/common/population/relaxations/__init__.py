import logging
import functools
import importlib

import structopt
from . import LAMMPS
from . import hard_sphere_cutoff
from structopt.tools import root, single_core, parallel


class Relaxations(object):
    """Holds the parameters for each relaxation module and defines a utility function to run the relaxations for each relaxation module."""

    @single_core
    def __init__(self, parameters):

        # Store the relaxation modules in a list based on their specified order
        self.parameters = parameters
        modules = [globals()[module] for module in self.parameters]
        orders = [self.parameters[module]['order'] for module in self.parameters]
        modules_orders = list(zip(modules, orders))
        modules_orders = sorted(modules_orders, key=lambda modules_orders: modules_orders[1])
        self.modules = list(zip(*modules_orders))[0]

    @parallel
    def relax(self, population):
        """Relax the entire population using all the input relaxation methods.

        Args:
            population (Population): the population to relax
        """
        logger = logging.getLogger("default")
        to_relax = [individual for individual in population if not individual._relaxed]
        logger.info("Found {} individuals to relax on core {}: {}".format(len(to_relax), logging.parameters.rank, to_relax))
        #print("Found {} individuals to relax on core {}: {}".format(len(to_relax), logging.parameters.rank, to_relax))
        for i, module in enumerate(self.modules):
            if logging.parameters.rank == 0:
                print("Running relaxation {} on the entire population".format(module.__name__.split('.')[-1]))
            parameters = getattr(self.parameters[module.__name__.split('.')[-1]], 'kwargs')
            module.relax(population, parameters=parameters)

        for individual in population:
            individual._relaxed = True

        return None


    @single_core
    def post_processing(self):
        pass

