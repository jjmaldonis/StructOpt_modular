import sys
import random
import logging

import structopt
from structopt.common.population import Population


class ParticleSwarmOptimization(object):
    """Defines methods to run a particle swarm optimization using the functions in the rest of the library."""

    def __init__(self, population, convergence):
        self.logger = logging.getLogger('default')

        self.population = population
        self.convergence = convergence

        self.generation = 0
        #bounds = self.init_velo
        bounds = 1.0
        nindiv = len(self.population)
        natoms = len(self.population[0].positions)
        #self.velocities = [[[random.uniform(-bounds/2,bounds/2) for j in range(3)] for n in range(natoms)] for i in range(nindiv)]
        self.best_swarm = self.population[0].copy()
        self.best_particles = [self.population[i].copy() for i in range(len(self.population))]

        
        # Prep output monitoring

        # Set starting convergence
        self.converged = False


    def run(self):
        if logging.parameters.rank == 0:
            print("Starting main Opimizer loop!")
        while not self.converged:
            self.step()
        if logging.parameters.rank == 0:
            print("Finished!")


    def step(self):
        if logging.parameters.rank == 0:
            print("Starting generation {}".format(self.generation))
        sys.stdout.flush()
        
        self.population.relax()        
        fits = self.population.fitness()

        if self.generation > 0:
            for i in range(len(self.population)):
                if fits[i] < self.best_particles[i]._fitness:
                    self.best_particles[i] = self.population[i].copy()
                    if self.best_particles[i]._fitness < self.best_swarm._fitness:
                        self.best_swarm = self.best_particles[i].copy()
        
        self.population.pso_moves(best_swarm, best_particles)
        self.check_convergence()
        self.population.generation += 1
        self.generation += 1

    def check_convergence(self):
        if self.generation >= self.convergence.maxgen:
            self.converged = True
        else:
            self.converged = False
    

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass


if __name__ == "__main__":
    import sys
    import structopt
    import numpy as np

    parameters = structopt.setup(sys.argv[1])

    random.seed(parameters.seed)
    np.random.seed(parameters.seed)

    population = Population(parameters=parameters)

    with structopt.ParticleSwarmOptimization(population=population,
                                    convergence=parameters.convergence
                                    ) as optimizer:
        optimizer.run()

