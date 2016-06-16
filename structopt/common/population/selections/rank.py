import random
from copy import deepcopy
import numpy as np
import scipy.stats

def rank(population, fits, prob, p_min=None, repeat_pairs=False):
    """Selection function that chooses pairs of structures 
    based on linear ranking.

    See "Grefenstette and Baker 1989 Whitley 1989".
    
    Parameters
    ----------
    population : StructOpt population object
        An object inherited from list that contains 
        StructOpt individual objects.
    fits : list
        A list of fitnesses of the population
    prob : float
        The probability of making the crossover
    p_min : float
        The probability of choosing the lowest ranked individual.
        Ideally this should be above 1/nindiv
    repeat_pairs : bool
        If True, repeat parents happen. Turning on False increases
        the diveristy of the population.

    Returns
    -------
    out : list
        A list of pairs of crossover pairs.
    """

    # Get ranks of each population value based on its fitness
    ranks = scipy.stats.rankdata(fits)

    # Work with indexes of the population instead of the population
    inds_population = range(len(population))

    # Get probabilities based on linear ranking
    if p_min==None:
        p_min = 1.0 / len(population) ** 2
    N = len(fits)
    eta_min = p_min * N
    eta_max = 2 - eta_min
    p_max = eta_max / N
    p = p_min + (p_max - p_min)*(N - ranks)/(N - 1)

    # Construct list of parents
    n_pairs = int(len(fits) / 2)
    pairs_ind = []

    for i in range(n_pairs):
        # Choose the first parent based on probabilties
        ind_father = np.random.choice(inds_population, p=p)

        # Choose the second parent based on renormalized probabilities
        # First remove the father from the population
        inds_population_temp, p_temp = list(inds_population), list(p)
        ind_del = inds_population.index(ind_father)
        del inds_population_temp[ind_del]
        del p_temp[ind_del]

        # Now remove mothers that would make repeat father/mother pairs
        if not repeat_parents:
            for pair in deepcopy(pairs_ind):
                if ind_father in pair:
                    del pair[pair.index(ind_father)]
                    ind_mother = pair[0]
                    ind_del = inds_population.index(ind_mother)
                    del inds_population_temp[ind_del]
                    del p_temp[ind_del]

        p_temp /= sum(p_temp)
        ind_mother = np.random.choice(new_fits, p=new_p)

        pairs_ind.append([ind_father, ind_mother])

    # Construct the parents from the indices
    pairs = [[population[i], population[j]] for i, j in pairs]
    return pairs
    
    # Delete these lines when the thing is done
    pairs = []
    for pair in combinations(population, 2):
        if random.random() < prob:
            pairs.append(pair)
    return pairs    
