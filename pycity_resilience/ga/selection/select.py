#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script with selection function
"""
from __future__ import division

import random
from deap import tools


def get_opt_pareto_values(pareto_fronts, objective):
    """
    Return the best objective function values of the first paretofront

    Parameters
    ----------
    pareto_fronts : list
        List of pareto fronts
    objective : str
        objective : str
        Objective function
         Options:
         'mc_risk_av_ann_co2_to_net_energy':
         'ann_and_co2_to_net_energy_ref_test'
         'ann_and_co2_ref_test'
         'mc_risk_av_ann_and_co2'
         'mc_mean_ann_and_co2'
         'mc_risk_friendly_ann_and_co2'
         'mc_min_std_of_ann_and_co2'
         'mc_dimless_eco_em_2d_mean'
         'mc_dimless_eco_em_2d_risk_av'
         'mc_dimless_eco_em_2d_risk_friendly'
         'mc_dimless_eco_em_2d_std'
         'ann_and_co2_dimless_ref'
         'mc_dimless_eco_em_3d_mean'
         'mc_dimless_eco_em_3d_risk_av'
         'mc_dimless_eco_em_3d_risk_friendly'
         'mc_dimless_eco_em_3d_std'
         'ann_and_co2_dimless_ref_3d'

    Returns
    -------
    tuple_res : tuple
        4d results tuple
        (min_ann, min_co2, int(idx_ann), int(idx_co2))
        min_ann : float
            Minimum annuity
        min_co2 : float
            Minimum CO2
        idx_ann : int
            Index of min_ann value on pareto front
        idx_co2 : int
            Index of min_co2 value on pareto front
    """

    #  Objectives for minimization
    if (objective == 'mc_risk_av_ann_co2_to_net_energy'
            or objective == 'ann_and_co2_to_net_energy_ref_test'
            or objective == 'ann_and_co2_ref_test'
            or objective == 'mc_risk_av_ann_and_co2'
            or objective == 'mc_mean_ann_and_co2'
            or objective == 'mc_risk_friendly_ann_and_co2'
            or objective == 'mc_min_std_of_ann_and_co2'
            or objective == 'mc_dimless_eco_em_2d_mean'
            or objective == 'mc_dimless_eco_em_2d_risk_av'
            or objective == 'mc_dimless_eco_em_2d_risk_friendly'
            or objective == 'ann_and_co2_dimless_ref'
            or objective == 'mc_dimless_eco_em_2d_std'
    ):

        #  Initial, dummy values
        min_ann = 100000000000000
        min_co2 = 100000000000000
        idx_ann = None
        idx_co2 = None

        for i in range(len(pareto_fronts[0])):
            #  If fitness value is better (smaller)
            if min_ann > pareto_fronts[0][i].fitness.values[0]:
                #  Save new best objective function value
                min_ann = pareto_fronts[0][i].fitness.values[0]
                idx_ann = i
            # If fitness value is better (smaller)
            if min_co2 > pareto_fronts[0][i].fitness.values[1]:
                #  Save new best objective function value
                min_co2 = pareto_fronts[0][i].fitness.values[1]
                idx_co2 = i

        return (min_ann, min_co2, idx_ann, idx_co2)

    elif (objective == 'mc_dimless_eco_em_3d_mean'
          or objective == 'mc_dimless_eco_em_3d_risk_av'
          or objective == 'mc_dimless_eco_em_3d_risk_friendly'
          or objective == 'ann_and_co2_dimless_ref_3d'
          or objective == 'mc_dimless_eco_em_3d_std'
    ):

        #  Initial, dummy values
        min_ann = 100000000000000
        min_co2 = 100000000000000
        max_beta_el = -10000000000000
        idx_ann = None
        idx_co2 = None
        idx_beta_el = None

        for i in range(len(pareto_fronts[0])):
            #  If fitness value is better (smaller)
            if min_ann > pareto_fronts[0][i].fitness.values[0]:
                #  Save new best objective function value
                min_ann = pareto_fronts[0][i].fitness.values[0]
                idx_ann = i
            # If fitness value is better (smaller)
            if min_co2 > pareto_fronts[0][i].fitness.values[1]:
                #  Save new best objective function value
                min_co2 = pareto_fronts[0][i].fitness.values[1]
                idx_co2 = i
            # If fitness value is better (larger)
            if max_beta_el < pareto_fronts[0][i].fitness.values[2]:
                #  Save new best objective function value
                max_beta_el = pareto_fronts[0][i].fitness.values[2]
                idx_beta_el = i

        return (min_ann, min_co2, max_beta_el, idx_ann, idx_co2, idx_beta_el)

    else:
        msg = 'Unknown/not implemented objective in get_opt_pareto_values!'
        raise NotImplementedError(msg)



def do_selection(parents, invalid_ind, nb_ind, objective, frac_pareto=0.8):
    """
    Perform selection of new population

    Parameters
    ----------
    parents : object
        Parent population
    invalid_ind : object
        Invalid individuals
    nb_ind : int
        Number of individuals in population
    objective : str
        Objective function
         Options:
         'mc_risk_av_ann_co2_to_net_energy':
         'ann_and_co2_to_net_energy_ref_test'
         'ann_and_co2_ref_test'
         'mc_risk_av_ann_and_co2'
         'mc_mean_ann_and_co2'
         'mc_risk_friendly_ann_and_co2'
         'mc_min_std_of_ann_and_co2'
         'mc_dimless_eco_em_2d_mean'
         'mc_dimless_eco_em_2d_risk_av'
         'mc_dimless_eco_em_2d_risk_friendly'
         'mc_dimless_eco_em_2d_std'
         'ann_and_co2_dimless_ref'
         'mc_dimless_eco_em_3d_mean'
         'mc_dimless_eco_em_3d_risk_av'
         'mc_dimless_eco_em_3d_risk_friendly'
         'mc_dimless_eco_em_3d_std'
         'ann_and_co2_dimless_ref_3d'
    frac_pareto : float, optional
        Pareto fraction (default: 0.8)

    Returns
    -------
    newoffspring : object
        Population object with new offspring of parent population
    """
    pareto_fronts = tools.sortNondominated(parents, len(parents))

    if len(pareto_fronts[0]) >= nb_ind * frac_pareto:
        if len(invalid_ind) >= (1 - frac_pareto) * nb_ind:
            #  Dummy value of reduced parent population
            reduced_parents = []

            if (objective == 'mc_risk_av_ann_co2_to_net_energy'
                    or objective == 'ann_and_co2_to_net_energy_ref_test'
                    or objective == 'ann_and_co2_ref_test'
                    or objective == 'mc_risk_av_ann_and_co2'
                    or objective == 'mc_mean_ann_and_co2'
                    or objective == 'mc_risk_friendly_ann_and_co2'
                    or objective == 'mc_min_std_of_ann_and_co2'
                    or objective == 'mc_dimless_eco_em_2d_mean'
                    or objective == 'mc_dimless_eco_em_2d_risk_av'
                    or objective == 'mc_dimless_eco_em_2d_risk_friendly'
                    or objective == 'ann_and_co2_dimless_ref'
                    or objective == 'mc_dimless_eco_em_2d_std'):

                #  Get best objective function values of pareto frontiers
                (min_ann, min_co2, idx_ann, idx_co2)\
                    = get_opt_pareto_values(pareto_fronts=pareto_fronts,
                                            objective=objective)

                if idx_ann is None or idx_co2 is None:
                    #  Could not find minimum values: Keep parents generation
                    reduced_parents = parents

                else:

                    reduced_parents.append(pareto_fronts[0][idx_ann])
                    reduced_parents.append(pareto_fronts[0][idx_co2])

                    #  Cleanup indexes (reserve to prevent index "shifting")
                    for del_index in sorted([idx_ann, idx_co2], reverse=True):
                        del pareto_fronts[0][del_index]

                    #  Reduce pareto frontier
                    for i in range(int(nb_ind * frac_pareto) - 2):
                        chosen_ind = random.choice(pareto_fronts[0])
                        reduced_parents.append(chosen_ind)
                        pareto_fronts[0].remove(chosen_ind)

            elif (objective == 'mc_dimless_eco_em_3d_mean'
                  or objective == 'mc_dimless_eco_em_3d_risk_av'
                  or objective == 'mc_dimless_eco_em_3d_risk_friendly'
                  or objective == 'ann_and_co2_dimless_ref_3d'
                  or objective == 'mc_dimless_eco_em_3d_std'):

                (min_ann, min_co2, max_beta_el,
                 idx_ann, idx_co2, idx_beta_el) = \
                    get_opt_pareto_values(pareto_fronts=pareto_fronts,
                                            objective=objective)

                if idx_ann is None or idx_co2 is None or idx_beta_el is None:
                    #  Could not find minimum values: Keep parents generation
                    reduced_parents = parents

                else:

                    reduced_parents.append(pareto_fronts[0][idx_ann])
                    reduced_parents.append(pareto_fronts[0][idx_co2])

                    if idx_beta_el != idx_ann and idx_beta_el != idx_co2:
                        reduced_parents.append(pareto_fronts[0][idx_beta_el])
                        val = 3
                    else:
                        val = 2

                    list_del_idx = []
                    list_cand = [idx_ann, idx_co2, idx_beta_el]
                    for elem in list_cand:
                        if elem not in list_del_idx:
                            list_del_idx.append(elem)

                    #  Cleanup indexes (reserve to prevent index "shifting")
                    for del_index in sorted(list_del_idx,
                                            reverse=True):
                        del pareto_fronts[0][del_index]

                    #  Reduce pareto frontier
                    for i in range(int(nb_ind * frac_pareto) - val):
                        if len(pareto_fronts[0]) > 1:  # Workaround for #260
                            chosen_ind = random.choice(pareto_fronts[0])
                            reduced_parents.append(chosen_ind)
                            pareto_fronts[0].remove(chosen_ind)
                        else:
                            reduced_parents = parents

        else:
            reduced_parents = parents

    else:
        reduced_parents = parents

    #  print information about
    print('Current inds and fitness values:')
    for ind in reduced_parents + invalid_ind:
        print(ind)
        print('fitness', ind.fitness.values)
    print()

    #  Select new offspring with NSGA2 algorithm
    newoffspring = tools.selNSGA2(reduced_parents + invalid_ind, nb_ind)

    return newoffspring
