#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script holding crossover manipulation of population
"""
from __future__ import division

import copy
import random
import warnings
import random
import numpy as np

import pycity_resilience.ga.verify.check_validity as checkval
import pycity_resilience.ga.analyse.analyse as analyse

from deap import tools


def do_crossover(ind1, ind2, dict_max_pv_area, dict_restr=None,
                 list_cx_combis=None, do_copy=True, perform_checks=True,
                 dict_sh=None, pv_min=None, pv_step=1, use_pv=False,
                 add_pv_prop=0, prevent_boi_lhn=True, dict_heatloads=None):
    """
    Executes a two-point crossover on the input
    individuals. The two individuals are modified in place and both keep
    their original length.
    The cx operation is bound to a restriction, that only certain combinations
    of items can be crossovered thus enabling onepoint crossover if
    len(list_cx_combis)=1

    Parameters
    ----------
    ind1 : dict
        First individuum
    ind2 : dict
        Second individuum
    dict_max_pv_area : dict (of floats)
        Dictionary holding building nodes as keys and max. usable pv areas
        in m2 as values
    dict_restr : dict, optional
        Dict holding possible energy system sizes (default: None)
    list_cx_combis : list (of lists), optional
        List of lists holding possible crossover variations (default: None).
        If None, uses default values ['chp', 'boiler', 'hp_aw', 'hp_ww',
             'eh', 'bat', 'pv', 'tes'],
            ['chp'], ['boiler'], ['hp_aw'], ['hp_ww'],
            ['eh'], ['bat'], ['pv'],
            ['tes'], ['lhn']]
    do_copy : bool, optional
        If True, makes copies of origin ind1 and ind2
    perform_checks : bool, optional
        Defines, if individuums should be checked on plausibility (default:
        True). Canb be deactivated to increase speed (check is also performed
        before running evaluation)
    dict_sh : dict, optional
        Dictionary holding building node ids as keys and maximum space heating
        power values in Watt as dict values (default: None). If not None,
        used for size limitation. If None, dict_restr is used for sizing.
        (default: None)
    pv_min : float, optional
        Minimum possible PV area per building in m2 (default: None)
    pv_step : float, optional
        Defines discrete step of Pv sizing in m2 (default: 1). E.g.
        If minimum PV size is 8 m2, 9, 10, 11...up to max. rooftop area can
        be chosen as PV size.
    use_pv : bool, optional
        Defines, if PV can be used (default: False)
    add_pv_prop : float, optional
        Defines additional probability of PV being changed, if only thermal
        mutation has been applied (defauft: 0). E.g. if boiler system has
        been changed to CHP, there is a change of add_pv_prob that also PV
        is mutated.
    prevent_boi_lhn : bool, optional
        Prevent boi/eh LHN combinations (without CHP) (default: True).
        If True, adds CHPs to LHN systems without CHP
    dict_heatloads : dict, optional
        Dict holding building ids as keys and design heat loads in Watt
        as values (default: None)

    Returns
    -------
    (ind1, ind2)
    """

    list_ind1_ids = analyse.get_build_ids_ind(ind1)
    list_ind2_ids = analyse.get_build_ids_ind(ind2)

    if sorted(list_ind1_ids) != sorted(list_ind2_ids):
        msg = 'ind1 and ind2 do not have the same keys! Check input values!'
        raise AssertionError(msg)

    if do_copy:
        ind1 = copy.deepcopy(ind1)
        ind2 = copy.deepcopy(ind2)

    if list_cx_combis is None:
        list_cx_combis = [
            ['chp', 'boi', 'hp_aw', 'hp_ww',
             'eh', 'bat', 'pv', 'tes'],
            ['chp'], ['boi'], ['hp_aw'], ['hp_ww'],
            ['eh'], ['bat'], ['pv'],
            ['tes']]# , ['lhn']]

    cx_not_done = True
    counter = 0

    #  Try to crossover until crossover was applied
    while cx_not_done:

        list_esys_key = random.choice(list_cx_combis)
        # list which energy systems shall be crossovered

        # get a list of nodes from individual
        nodes = analyse.get_build_ids_ind(ind=ind1)

        #  Randomly select crossover nodes
        node1 = random.choice(nodes)
        node2 = random.choice(nodes)

        #  Perform crossover mutation
        if len(list_esys_key) > 1:
            # Complete Crossover: Switch all values between two buildings
            for key in list_esys_key:
                # apply crossover
                if ind1[node1] != ind2[node2]:
                    ind1[node1][key], ind2[node2][key] = ind2[node2][key], \
                                                         ind1[node1][key]
                    cx_not_done = False
        else:
            # Single value Crossover: Only switch one value
            # get str from list
            key = list_esys_key[0]

            if key == 'chp' or key == 'boi' or key == 'hp_aw' \
                    or key == 'hp_ww' or key == 'eh' or key == 'tes':
                # check if none of the values is equal to zero
                if ind1[node1][key] != 0:
                    if ind2[node2][key] != 0:
                        # check if values which will be crossovered are not
                        # the same
                        if ind2[node2][key] != ind1[node1][key]:
                            ind1[node1][key], ind2[node2][key] = ind2[node2][
                                                                     key], \
                                                                 ind1[node1][
                                                                     key]
                            cx_not_done = False

            elif key == 'bat' or key == 'pv':
                # crossover bat or pv
                # check if values which will be crossovered are not
                # the same
                if ind2[node2][key] != ind1[node1][key]:
                    ind1[node1][key], ind2[node2][key] = ind2[node2][key], \
                                                         ind1[node1][key]
                    cx_not_done = False

        counter += 1
        if counter >= 20:
            # if tried to crossover more than 20 times stop trying and abort
            # crossover
            cx_not_done = False
            warnings.warn('Crossover aborted (reached more than 20 tries).')

    # Check configuration
    #  #############################################################

    if perform_checks:
        checkval.run_all_checks(ind=ind1, dict_max_pv_area=dict_max_pv_area,
                                dict_restr=dict_restr, dict_sh=dict_sh,
                                pv_min=pv_min, pv_step=pv_step, use_pv=use_pv,
                                add_pv_prop=add_pv_prop,
                                prevent_boi_lhn=prevent_boi_lhn,
                                dict_heatloads=dict_heatloads)
        checkval.run_all_checks(ind=ind2, dict_max_pv_area=dict_max_pv_area,
                                dict_restr=dict_restr, dict_sh=dict_sh,
                                pv_min=pv_min, pv_step=pv_step, use_pv=use_pv,
                                add_pv_prop=add_pv_prop,
                                prevent_boi_lhn=prevent_boi_lhn,
                                dict_heatloads=dict_heatloads)

    print('Performed crossover changes')

    return (ind1, ind2)


def cx_tournament(pop, prob_cx, dict_max_pv_area, dict_restr, nb_part=4,
                  perform_checks=True, dict_sh=None,
                  pv_min=None, pv_step=1, use_pv=False, add_pv_prop=0,
                  prevent_boi_lhn=True, dict_heatloads=None):
    """
    Performs crossover on individuusm, which have been selected by selNSGA2
    tournament.

    Parameters
    ----------
    pop : list
        List of individuum dicts (ind) / population
    prob_cx : float
        Probability of crossover being applied
    dict_max_pv_area : dict
        Dict holding maximum usable PV area values in m2 per building
    dict_restr : dict
        Dict holding possible energy system sizes
    nb_part : int
        Number of individuums which take part in single tournament
    perform_checks : bool, optional
        Defines, if individuums should be checked on plausibility (default:
        True). Canb be deactivated to increase speed (check is also performed
        before running evaluation)
    dict_sh : dict, optional
        Dictionary holding building node ids as keys and maximum space heating
        power values in Watt as dict values (default: None). If not None,
        used for size limitation. If None, dict_restr is used for sizing.
        (default: None)
    pv_min : float, optional
        Minimum possible PV area per building in m2 (default: None)
    pv_step : float, optional
        Defines discrete step of Pv sizing in m2 (default: 1). E.g.
        If minimum PV size is 8 m2, 9, 10, 11...up to max. rooftop area can
        be chosen as PV size.
    use_pv : bool, optional
        Defines, if PV can be used (default: False)
    add_pv_prop : float, optional
        Defines additional probability of PV being changed, if only thermal
        mutation has been applied (defauft: 0). E.g. if boiler system has
        been changed to CHP, there is a change of add_pv_prob that also PV
        is mutated.
    prevent_boi_lhn : bool, optional
		Prevent boi/eh LHN combinations (without CHP) (default: True).
		If True, adds CHPs to LHN systems without CHP
	dict_heatloads : dict, optional
        Dict holding building ids as keys and design heat loads in Watt
        as values (default: None)

    Returns
    -------
    offspring : list
        List of individuum dicts (ind) / population
    """

    offspring = []

    for i in range(int(round(len(pop) / 2))):

        #  Randomly select participants
        list_participants = np.random.choice(pop, size=nb_part)

        #  Determine the tournament winners
        list_win = tools.selNSGA2(list_participants, 2)

        #  Copy winning individuums
        ind1 = copy.deepcopy(list_win[0])
        ind2 = copy.deepcopy(list_win[1])

        #  Perform crossover on individuums
        if random.random() < prob_cx:
            ind1, ind2 = do_crossover(ind1=ind1, ind2=ind2,
                                      dict_max_pv_area=dict_max_pv_area,
                                      perform_checks=perform_checks,
                                      dict_restr=dict_restr, dict_sh=dict_sh,
                                      pv_min=pv_min, pv_step=pv_step,
                                      use_pv=use_pv,
                                      add_pv_prop=add_pv_prop,
                                      prevent_boi_lhn=prevent_boi_lhn,
                                      dict_heatloads=dict_heatloads
                                      )

            #  Delete old fitness values
            del ind1.fitness.values
            del ind2.fitness.values

        #  Add crossovered individuums to offspring
        offspring.append(ind1)
        offspring.append(ind2)

    return offspring
