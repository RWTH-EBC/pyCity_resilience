#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to perform changes to LHN structure:
- Generation of LHN (all buildings or subnetwork)
- Delete LHN
- Mutation of LHN (adding/removing nodes, change feeders...)
"""
from __future__ import division

import copy
import random
import warnings
import numpy as np

import pycity_resilience.ga.analyse.analyse as analyse
import pycity_resilience.ga.evolution.esys_changes as esyschanges
import pycity_resilience.ga.evolution.mutation_esys as mutateesys
import pycity_resilience.ga.analyse.find_lhn as findlhn
import pycity_resilience.ga.clustering.cluster as clust


def add_lhn_all_build(ind, dict_restr, pv_min, dict_max_pv_area,
                      prob_feed=[0.7, 0.3], dict_sh=None, add_pv_prop=0,
                      add_bat_prob=0,
                      dict_heatloads=None):
    """
    Add LHN to all buildings with one or multiple feeder nodes

    Parameters
    ----------
    ind : dict
        Individuum dict
    dict_restr : dict
        Dict holding possible energy system sizes
    pv_min : float
        Minimum possible PV area per building in m2
    dict_max_pv_area : dict
        Dict holding maximum usable PV area values in m2 per building
    prob_feed : list, optional
        2d list holding probabilities to add single feeder (index 0) or
        multiple feeders (index 1) (default: [0.7, 0.3])
    dict_sh : dict, optional
        Dictionary holding building node ids as keys and maximum space heating
        power values in Watt as dict values (default: None). If not None,
        used for size limitation. If None, dict_restr is used for sizing.
    add_pv_prop : float, optional
        Defines additional probability of PV being changed, if only thermal
        mutation has been applied (defauft: 0). E.g. if boiler system has
        been changed to CHP, there is a change of add_pv_prob that also PV
        is mutated.
    add_bat_prob : float, optional
        Defines additional probability ofBAT being changed, if only thermal
        mutation has been applied (defauft: 0). E.g. if boiler system has
        been changed to CHP, there is a change of add_pv_prob that also BAT
        is mutated.
    dict_heatloads : dict, optional
        Dict holding building ids as keys and design heat loads in Watt
        as values (default: None)
    """

    #  Get list with building ids (delete key 'lhn')
    list_ids = analyse.get_build_ids_ind(ind=ind)

    #  Add single LHN to all building nodes
    ind['lhn'] = [copy.copy(list_ids)]

    #  Add, at least, one feeder node. Set other thermal
    #  supply systems to zero
    select_single_or_multi = \
        np.random.choice(a=['single', 'multi'], p=prob_feed)

    #  List possible feeder ids (all buildings)
    list_possible_feed = copy.copy(list_ids)

    if select_single_or_multi == 'single':
        #  Add single feeder, set other to zero
        add_single_feeder(ind=ind, dict_restr=dict_restr, pv_min=pv_min,
                          dict_max_pv_area=dict_max_pv_area,
                          list_possible_feed=list_possible_feed,
                          other_no_th_sup=True, dict_sh=dict_sh,
                          add_pv_prop=add_pv_prop, add_bat_prob=add_bat_prob,
                          dict_heatloads=dict_heatloads)

    elif select_single_or_multi == 'multi':
        #  Add multiple feeder nodes
        add_multiple_feeders(ind=ind, dict_restr=dict_restr, pv_min=pv_min,
                             dict_max_pv_area=dict_max_pv_area,
                             list_possible_feed=list_possible_feed,
                             other_no_th_sup=True,
                             dict_sh=dict_sh, add_pv_prop=add_pv_prop,
                             add_bat_prob=add_bat_prob,
                             dict_heatloads=dict_heatloads)


def del_lhn(ind, dict_restr, pv_min, dict_max_pv_area,
            prob_del=[0.7, 0.3], list_options=None,
            list_lhn_to_stand_alone=None, dict_sh=None,
            add_pv_prop=0, add_bat_prob=0,
            dict_heatloads=None):
    """
    Delete single or multiple LHN systems in ind.

    Parameters
    ----------
    ind : dict
        Individuum dict
    dict_restr : dict
        Dict holding possible energy system sizes
    pv_min : float
        Minimum possible PV area per building in m2
    dict_max_pv_area : dict
        Dict holding maximum usable PV area values in m2 per building
    prob_del : list, optional
        2d list holding probabilities to delete single LHN (index 0) or
        multiple LHN (index 1) (default: [0.7, 0.3])
    list_options : list (of str), optional
        List holding strings with energy system options (default: None).
        If None, uses default values ['boi', 'boi_tes', 'chp_boi_tes',
        'chp_boi_eh_tes', 'hp_aw_eh', 'hp_ww_eh', 'hp_aw_boi', 'hp_ww_boi',
        'hp_aw_eh_boi', 'hp_ww_eh_boi', 'bat', 'pv']
    list_lhn_to_stand_alone : list (of floats)
        List holding probability factors for energy system options in
        list_options (default: None).
        If None, uses default values [0.1, 0.15, 0.25, 0.05, 0.125, 0.125,
        0.05, 0.05, 0.05, 0.05, 0, 0]
    dict_sh : dict, optional
        Dictionary holding building node ids as keys and maximum space heating
        power values in Watt as dict values (default: None). If not None,
        used for size limitation. If None, dict_restr is used for sizing.
    add_pv_prop : float, optional
        Defines additional probability of PV being changed, if only thermal
        mutation has been applied (defauft: 0). E.g. if boiler system has
        been changed to CHP, there is a change of add_pv_prob that also PV
        is mutated.
    add_bat_prob : float, optional
        Defines additional probability of BAT being changed, if only thermal
        mutation has been applied (defauft: 0). E.g. if boiler system has
        been changed to CHP, there is a change of add_pv_prob that also BAT
        is mutated.
    dict_heatloads : dict, optional
        Dict holding building ids as keys and design heat loads in Watt
        as values (default: None)
    """
    if list_options is None:
        list_options = ['boi', 'boi_tes', 'chp_boi_tes', 'chp_boi_eh_tes',
                        'hp_aw_eh', 'hp_ww_eh', 'hp_aw_boi', 'hp_ww_boi',
                        'hp_aw_eh_boi', 'hp_ww_eh_boi', 'bat', 'pv']

    if list_lhn_to_stand_alone is None:
        #  Prevent bat and PV usage, as stand-alone building requires
        #  thermal supply
        list_lhn_to_stand_alone = [0.1, 0.15, 0.25, 0.05, 0.125, 0.125,
                                   0.05, 0.05, 0.05, 0.05, 0, 0]

    assert abs(sum(list_lhn_to_stand_alone) - 1) < 0.0000000001

    #  If individuum has no LHN, exits function
    if ind['lhn'] == []:  # pragma: no cover
        msg = 'Individuum dict has no LHN. Thus, LHN cannot be deleted. ' \
              'Going to exit function.'
        warnings.warn(msg)
        return

    if len(ind['lhn']) == 1:
        #  Only one LHN
        prob_del = [1, 0]

    # Delete, at least, one LHN. Set other thermal
    #  supply systems to zero
    select_single_or_multi = \
        np.random.choice(a=['single', 'multi'], p=prob_del)

    if select_single_or_multi == 'single':
        #  Delete single LHN

        #  Randomly select LHN index of list to be deleted
        idx_lhn = random.randint(0, len(ind['lhn']) - 1)

        #  Save list of building ids, which are going to loose LHN connection
        list_new_esys = copy.copy(ind['lhn'][idx_lhn])

        #  Delete list by index
        del ind['lhn'][idx_lhn]

    elif select_single_or_multi == 'multi':

        #  Select random number of LHN networks to be deleted
        #  (between 2 and max. nb. of LHNs)
        if len(ind['lhn']) == 2:
            nb_lhn_del = 2
        else:
            nb_lhn_del = random.randint(2, len(ind['lhn']))

        # Generate list of indexes
        list_idxs = list(range(0, int(len(ind['lhn']))))

        #  Select random indexes of LHN networks
        list_idx_del = np.random.choice(list_idxs, size=nb_lhn_del,
                                        replace=False)

        list_new_esys = []

        for idx in list_idx_del:
            for n in ind['lhn'][idx]:  # Loop over building ids
                #  Save building ids
                list_new_esys.append(n)

        # Delete lists by index (sort to prevent index "changes")
        for idx in sorted(list_idx_del, reverse=True):
            # Delete LHN list by index
            del ind['lhn'][idx]

    if list_options is None:
        list_options = ['boi', 'boi_tes', 'chp_boi_tes', 'chp_boi_eh_tes',
                        'hp_aw_eh', 'hp_ww_eh', 'hp_aw_boi', 'hp_ww_boi',
                        'hp_aw_eh_boi', 'hp_ww_eh_boi', 'bat', 'pv']

    # Add energy systems to buildings without LHN connection
    for i in list_new_esys:
        mutateesys. \
            mut_esys_config_single_build(ind=ind, n=i,
                                         dict_restr=dict_restr,
                                         pv_min=pv_min,
                                         dict_max_pv_area=
                                         dict_max_pv_area,
                                         list_options=list_options,
                                         list_opt_prob=list_lhn_to_stand_alone,
                                         dict_sh=dict_sh,
                                         add_pv_prop=add_pv_prop,
                                         add_bat_prob=add_bat_prob,
                                         dict_heatloads=dict_heatloads)


def add_lhn(ind, dict_restr, pv_min, dict_max_pv_area, dict_pos,
            list_prob_lhn=[0.5, 0.5], max_dist=None, prob_feed=[0.7, 0.3],
            prob_gen_method=[0.5, 0.3, 0.2], dict_sh=None, add_pv_prop=0,
            add_bat_prob=0, dict_heatloads=None):
    """
    Add single or multiple LHN systems to

    Parameters
    ----------
    ind : dict
        Individuum dict
    dict_restr : dict
        Dict holding possible energy system sizes
    pv_min : float
        Minimum possible PV area per building in m2
    dict_max_pv_area : dict
        Dict holding maximum usable PV area values in m2 per building
    dict_pos : dict
        Dict holding building node ids as keys and shapely point objects (2d)
        as values
    list_prob_lhn : list, optional
        2d list holding probabilities to add single LHN (index 0) or
        multiple LHN (index 1) (default: [0.5, 0.5])
    max_dist : float, optional
        Maximum allowed distance in m from building to building, which
        can be connected to LHN (default: None)
    prob_feed : list, optional
        2d list holding probabilities to add single feeder (index 0) or
        multiple feeders (index 1) (default: [0.7, 0.3])
    prob_gen_method : list, optional
        List holding probabilities for different LHN generation mode:
        index 0: Random generation
        index 1: Kmeans generation
        (default: [0.5, 0.3, 0.2])
    dict_sh : dict, optional
        Dictionary holding building node ids as keys and maximum space heating
        power values in Watt as dict values (default: None). If not None,
        used for size limitation. If None, dict_restr is used for sizing.
    add_pv_prop : float, optional
        Defines additional probability of PV being changed, if only thermal
        mutation has been applied (defauft: 0). E.g. if boiler system has
        been changed to CHP, there is a change of add_pv_prob that also PV
        is mutated.
    add_bat_prob : float, optional
        Defines additional probability ofBAT being changed, if only thermal
        mutation has been applied (defauft: 0). E.g. if boiler system has
        been changed to CHP, there is a change of add_pv_prob that also BAT
        is mutated.
    dict_heatloads : dict, optional
        Dict holding building ids as keys and design heat loads in Watt
        as values (default: None)
    """

    #  Get list of building node ids
    list_build_ids = analyse.get_build_ids_ind(ind=ind)

    #  Get list of all buildings, which are already connected to LHN(s)
    list_lhn_ids = findlhn.get_all_lhn_ids(ind=ind)

    #  Check if, at least, two nodes are available for LHN generation
    #  Otherwise, warn user and leave function
    if len(ind) - 1 - len(list_lhn_ids) < 2:  # pragma: no cover
        msg = 'Sub-LHN cannot be generated, as ind has less than 2 nodes left.'
        warnings.warn(msg)
        return

    # Choose if single or multiple LHN should be generated
    select_single_or_multi = \
        np.random.choice(a=['single', 'multi'], p=list_prob_lhn)

    select_method = np.random.choice(a=['reg', 'kmeans', 'meanshift'],
                                     p=prob_gen_method)

    if select_single_or_multi == 'single':
        #  Add single LHN

        if select_method == 'reg':

            add_single_lhn(ind=ind,
                           dict_restr=dict_restr,
                           pv_min=pv_min,
                           dict_max_pv_area=dict_max_pv_area,
                           dict_pos=dict_pos,
                           max_dist=max_dist,
                           prob_feed=prob_feed,
                           dict_sh=dict_sh, add_pv_prop=add_pv_prop,
                           add_bat_prob=add_bat_prob,
                           dict_heatloads=dict_heatloads)

        elif select_method == 'kmeans':

            # Get list of available building nodes to be connected to LHN
            list_av_ids = list(set(list_build_ids) - set(list_lhn_ids))

            if int(len(list_av_ids) / 3) == 1:
                nb_clusters = 1
            elif int(len(list_av_ids) / 3) == 2:
                nb_clusters = 2
            elif int(len(list_av_ids) / 3) > 2:
                #  Select random number of desired clusters
                nb_clusters = random.randint(2, int(len(list_av_ids) / 3))
            else:
                return

            # Use kmeans algorithm to generate LHN
            dict_clusters = clust. \
                kmeans_clustering(dict_pos=dict_pos, list_av_ids=list_av_ids,
                                  nb_clusters=nb_clusters)

            #  If kmeans could not find a solution, exit function
            if dict_clusters is None:  # pragma: no cover
                msg = 'Kmeans did not find a solution. Going to exit function'
                warnings.warn(msg)
                return

            #  Randomly select a new LHN network from cluster
            idx_new = random.randint(0, int(len(dict_clusters) - 1))

            #  New list of LHN ids
            list_lhn_new = dict_clusters[idx_new]

            #  Add lists as single LHN
            ind['lhn'].append(list_lhn_new)

            #  Add single or multi feeders

            #  Add, at least, one feeder node. Set other thermal
            #  supply systems to zero
            select_single_or_multi = \
                np.random.choice(a=['single', 'multi'], p=prob_feed)

            if select_single_or_multi == 'single':
                #  Add single feeder, set other to zero
                add_single_feeder(ind=ind, dict_restr=dict_restr,
                                  pv_min=pv_min,
                                  dict_max_pv_area=dict_max_pv_area,
                                  list_possible_feed=list_lhn_new,
                                  other_no_th_sup=True, dict_sh=dict_sh,
                                  add_pv_prop=add_pv_prop,
                                  add_bat_prob=add_bat_prob,
                                  dict_heatloads=dict_heatloads
                                  )

            elif select_single_or_multi == 'multi':
                #  Add multiple feeder nodes
                add_multiple_feeders(ind=ind, dict_restr=dict_restr,
                                     pv_min=pv_min,
                                     dict_max_pv_area=dict_max_pv_area,
                                     list_possible_feed=list_lhn_new,
                                     other_no_th_sup=True,
                                     dict_sh=dict_sh,
                                     add_pv_prop=add_pv_prop,
                                     add_bat_prob=add_bat_prob,
                                     dict_heatloads=dict_heatloads
                                     )

        elif select_method == 'meanshift':

            # Get list of available building nodes to be connected to LHN
            list_av_ids = list(set(list_build_ids) - set(list_lhn_ids))

            try:
                # Use kmeans algorithm to generate LHN
                dict_clusters = clust. \
                    meanshift_clustering(dict_pos=dict_pos,
                                         list_av_ids=list_av_ids)
            except:
                msg = 'Meanshift clustering failed. Thus, cannot add LHN. ' \
                      'Return None.'
                warnings.warn(msg)
                return

            #  Randomly select a new LHN network from cluster
            idx_new = random.randint(0, int(len(dict_clusters) - 1))

            #  New list of LHN ids
            list_lhn_new = dict_clusters[idx_new]

            #  Add lists as single LHN
            ind['lhn'].append(list_lhn_new)

            #  Add single or multi feeders

            #  Add, at least, one feeder node. Set other thermal
            #  supply systems to zero
            select_single_or_multi = \
                np.random.choice(a=['single', 'multi'], p=prob_feed)

            if select_single_or_multi == 'single':
                #  Add single feeder, set other to zero
                add_single_feeder(ind=ind, dict_restr=dict_restr,
                                  pv_min=pv_min,
                                  dict_max_pv_area=dict_max_pv_area,
                                  list_possible_feed=list_lhn_new,
                                  other_no_th_sup=True, dict_sh=dict_sh,
                                  add_pv_prop=add_pv_prop,
                                  add_bat_prob=add_bat_prob,
                                  dict_heatloads=dict_heatloads
                                  )

            elif select_single_or_multi == 'multi':
                #  Add multiple feeder nodes
                add_multiple_feeders(ind=ind, dict_restr=dict_restr,
                                     pv_min=pv_min,
                                     dict_max_pv_area=dict_max_pv_area,
                                     list_possible_feed=list_lhn_new,
                                     other_no_th_sup=True,
                                     dict_sh=dict_sh,
                                     add_pv_prop=add_pv_prop,
                                     add_bat_prob=add_bat_prob,
                                     dict_heatloads=dict_heatloads
                                     )

    elif select_single_or_multi == 'multi':
        #  Add multiple LHN

        if select_method == 'reg':

            # Get list of available building nodes to be connected to LHN
            list_av_ids = list(set(list_build_ids) - set(list_lhn_ids))

            #  Random nb. of LHNs, which should be generated
            if int(len(list_av_ids) / 3) == 1:
                nb_lhn = 1
            elif int(len(list_av_ids) / 3) == 2:
                nb_lhn = 2
            elif int(len(list_av_ids) / 3) > 2:
                nb_lhn = random.randint(2, int(len(list_av_ids) / 3))
            else:
                return

            # Loop over desired number of new LHN
            for i in range(nb_lhn):
                #  Add single lhn until no more LHN can be added
                add_single_lhn(ind=ind,
                               dict_restr=dict_restr,
                               pv_min=pv_min,
                               dict_max_pv_area=dict_max_pv_area,
                               dict_pos=dict_pos,
                               max_dist=max_dist,
                               prob_feed=prob_feed,
                               dict_sh=dict_sh, add_pv_prop=add_pv_prop,
                               add_bat_prob=add_bat_prob,
                               dict_heatloads=dict_heatloads)

        elif select_method == 'kmeans':

            # Get list of available building nodes to be connected to LHN
            list_av_ids = list(set(list_build_ids) - set(list_lhn_ids))

            if int(len(list_av_ids) / 3) == 1:
                nb_clusters = 1
            elif int(len(list_av_ids) / 3) == 2:
                nb_clusters = 2
            elif int(len(list_av_ids) / 3) > 2:
                #  Select random number of desired clusters
                nb_clusters = random.randint(2, int(len(list_av_ids) / 3))
            else:
                return

            # Use kmeans algorithm to generate LHN
            dict_clusters = clust. \
                kmeans_clustering(dict_pos=dict_pos, list_av_ids=list_av_ids,
                                  nb_clusters=nb_clusters)

            #  If kmeans could not find a solution, exit function
            if dict_clusters is None:  # pragma: no cover
                msg = 'Kmeans did not find a solution. Going to exit function'
                warnings.warn(msg)
                return

            # Loop over dict id lists
            for key in dict_clusters:
                list_sublhn = dict_clusters[key]

                #  Add lists as single LHN
                ind['lhn'].append(list_sublhn)

                #  Add single or multi feeders

                #  Add, at least, one feeder node. Set other thermal
                #  supply systems to zero
                select_single_or_multi = \
                    np.random.choice(a=['single', 'multi'], p=prob_feed)

                if select_single_or_multi == 'single':
                    #  Add single feeder, set other to zero
                    add_single_feeder(ind=ind, dict_restr=dict_restr,
                                      pv_min=pv_min,
                                      dict_max_pv_area=dict_max_pv_area,
                                      list_possible_feed=list_sublhn,
                                      other_no_th_sup=True, dict_sh=dict_sh,
                                      add_pv_prop=add_pv_prop,
                                      add_bat_prob=add_bat_prob,
                                      dict_heatloads=dict_heatloads
                                      )

                elif select_single_or_multi == 'multi':
                    #  Add multiple feeder nodes
                    add_multiple_feeders(ind=ind, dict_restr=dict_restr,
                                         pv_min=pv_min,
                                         dict_max_pv_area=dict_max_pv_area,
                                         list_possible_feed=list_sublhn,
                                         other_no_th_sup=True,
                                         dict_sh=dict_sh,
                                         add_pv_prop=add_pv_prop,
                                         add_bat_prob=add_bat_prob,
                                         dict_heatloads=dict_heatloads
                                         )

        elif select_method == 'meanshift':

            # Get list of available building nodes to be connected to LHN
            list_av_ids = list(set(list_build_ids) - set(list_lhn_ids))

            try:
                # Use kmeans algorithm to generate LHN
                dict_clusters = clust. \
                    meanshift_clustering(dict_pos=dict_pos,
                                         list_av_ids=list_av_ids)
            except:
                msg = 'Meanshift clustering failed. Thus, cannot add LHN. ' \
                      'Return None.'
                warnings.warn(msg)
                return

            # Loop over dict id lists
            for key in dict_clusters:
                list_sublhn = dict_clusters[key]

                #  Add lists as single LHN
                ind['lhn'].append(list_sublhn)

                #  Add single or multi feeders

                #  Add, at least, one feeder node. Set other thermal
                #  supply systems to zero
                select_single_or_multi = \
                    np.random.choice(a=['single', 'multi'], p=prob_feed)

                if select_single_or_multi == 'single':
                    #  Add single feeder, set other to zero
                    add_single_feeder(ind=ind, dict_restr=dict_restr,
                                      pv_min=pv_min,
                                      dict_max_pv_area=dict_max_pv_area,
                                      list_possible_feed=list_sublhn,
                                      other_no_th_sup=True,
                                      dict_sh=dict_sh,
                                      add_pv_prop=add_pv_prop,
                                      add_bat_prob=add_bat_prob,
                                      dict_heatloads=dict_heatloads
                                      )

                elif select_single_or_multi == 'multi':
                    #  Add multiple feeder nodes
                    add_multiple_feeders(ind=ind, dict_restr=dict_restr,
                                         pv_min=pv_min,
                                         dict_max_pv_area=dict_max_pv_area,
                                         list_possible_feed=list_sublhn,
                                         other_no_th_sup=True,
                                         dict_sh=dict_sh,
                                         add_pv_prop=add_pv_prop,
                                         add_bat_prob=add_bat_prob,
                                         dict_heatloads=dict_heatloads
                                         )


def add_single_lhn(ind, dict_restr, pv_min, dict_max_pv_area, dict_pos,
                   max_dist=None, prob_feed=[0.7, 0.3], dict_sh=None,
                   add_pv_prop=0, add_bat_prob=0,
                   dict_heatloads=None):
    """
    Tries to add single LHN to ind dict. If not enough nodes are left or
    LHN systems would cross, exits function.

    Parameters
    ----------
    ind : dict
        Individuum dict
    dict_restr : dict
        Dict holding possible energy system sizes
    pv_min : float
        Minimum possible PV area per building in m2
    dict_max_pv_area : dict
        Dict holding maximum usable PV area values in m2 per building
    dict_pos : dict
        Dict holding building node ids as keys and shapely point objects (2d)
        as values
    max_dist : float, optional
        Maximum allowed distance in m from building to building, which
        can be connected to LHN (default: None)
    prob_feed : list, optional
        2d list holding probabilities to add single feeder (index 0) or
        multiple feeders (index 1) (default: [0.7, 0.3])
    dict_sh : dict, optional
        Dictionary holding building node ids as keys and maximum space heating
        power values in Watt as dict values (default: None). If not None,
        used for size limitation. If None, dict_restr is used for sizing.
    add_pv_prop : float, optional
        Defines additional probability of PV being changed, if only thermal
        mutation has been applied (defauft: 0). E.g. if boiler system has
        been changed to CHP, there is a change of add_pv_prob that also PV
        is mutated.
    add_bat_prob : float, optional
        Defines additional probability ofBAT being changed, if only thermal
        mutation has been applied (defauft: 0). E.g. if boiler system has
        been changed to CHP, there is a change of add_pv_prob that also BAT
        is mutated.
    dict_heatloads : dict, optional
        Dict holding building ids as keys and design heat loads in Watt
        as values (default: None)
    """

    assert abs(sum(prob_feed) - 1) < 0.000000001

    #  Get list of building node ids
    list_build_ids = analyse.get_build_ids_ind(ind=ind)

    #  Get list of all buildings, which are already connected to LHN(s)
    list_lhn_ids = findlhn.get_all_lhn_ids(ind=ind)

    #  Check if, at least, two nodes are available for LHN generation
    #  Otherwise, warn user and leave function
    if len(ind) - 1 - len(list_lhn_ids) < 2:  # pragma: no cover
        msg = 'Sub-LHN cannot be generated, as ind has less than 2 nodes left.'
        warnings.warn(msg)
        return

    # Get list of available building nodes to be connected to LHN
    list_av_ids = list(set(list_build_ids) - set(list_lhn_ids))

    #  Randomly select available node to start LHN generation
    start_id = list_av_ids.pop(random.randrange(len(list_av_ids)))

    #  Get list with available neighbor node ids
    #  sorted by distance to start_id
    list_next_ids = analyse. \
        get_ids_sorted_by_dist(id=start_id, dict_pos=dict_pos,
                               list_av=list_av_ids, max_dist=max_dist)

    #  Check if, at least, two nodes are available for LHN generation
    #  Otherwise, warn user and leave function
    if len(list_next_ids) == []:  # pragma: no cover
        msg = 'Sub-LHN cannot be generated, as list_next_ids is empty.'
        warnings.warn(msg)
        return

    if len(list_next_ids) > 1:
        # Select random number of nodes of list_next_ids
        nb_lhn = random.randrange(1, int(len(list_next_ids)))
    else:
        nb_lhn = 1

    # Dummy list
    list_new_lhn = []
    #  Add neighbors
    for i in range(nb_lhn):
        list_new_lhn.append(list_next_ids[i])

    # Add start id
    list_new_lhn.append(start_id)

    # Add list of new LHN nodes to ind['lhn']
    ind['lhn'].append(list_new_lhn)

    #  Add single or multi feeders

    #  Add, at least, one feeder node. Set other thermal
    #  supply systems to zero
    select_single_or_multi = \
        np.random.choice(a=['single', 'multi'], p=prob_feed)

    if select_single_or_multi == 'single':
        #  Add single feeder, set other to zero
        add_single_feeder(ind=ind, dict_restr=dict_restr, pv_min=pv_min,
                          dict_max_pv_area=dict_max_pv_area,
                          list_possible_feed=list_new_lhn,
                          other_no_th_sup=True, dict_sh=dict_sh,
                          add_pv_prop=add_pv_prop, add_bat_prob=add_bat_prob,
                          dict_heatloads=dict_heatloads)

    elif select_single_or_multi == 'multi':
        #  Add multiple feeder nodes
        add_multiple_feeders(ind=ind, dict_restr=dict_restr, pv_min=pv_min,
                             dict_max_pv_area=dict_max_pv_area,
                             list_possible_feed=list_new_lhn,
                             other_no_th_sup=True,
                             dict_sh=dict_sh, add_pv_prop=add_pv_prop,
                             add_bat_prob=add_bat_prob,
                             dict_heatloads=dict_heatloads)


def add_single_feeder(ind, dict_restr, pv_min, dict_max_pv_area,
                      list_possible_feed, other_no_th_sup=False,
                      dict_sh=None, add_pv_prop=0, add_bat_prob=0,
                      dict_heatloads=None):
    """
    Add single feeder building to LHN. Set all other nodes within
    list_possible_feed to no thermal supply.

    Parameters
    ----------
    ind : dict
        Individuum dict
    dict_restr : dict
        Dict holding possible energy system sizes
    pv_min : float
        Minimum possible PV area per building in m2
    dict_max_pv_area : dict
        Dict holding maximum usable PV area values in m2 per building
    list_possible_feed : list
        List with possible feeder ids
    other_no_th_sup : bool, optional
        If True, sets all other nodes in list_possible_feed to no thermal
        supply (default: False)
    dict_sh : dict, optional
        Dictionary holding building node ids as keys and maximum space heating
        power values in Watt as dict values (default: None). If not None,
        used for size limitation. If None, dict_restr is used for sizing.
    add_pv_prop : float, optional
        Defines additional probability of PV being changed, if only thermal
        mutation has been applied (defauft: 0). E.g. if boiler system has
        been changed to CHP, there is a change of add_pv_prob that also PV
        is mutated.
    add_bat_prob : float, optional
        Defines additional probability of BAT being changed, if only thermal
        mutation has been applied (defauft: 0). E.g. if boiler system has
        been changed to CHP, there is a change of add_pv_prob that also BAT
        is mutated.
    dict_heatloads : dict, optional
        Dict holding building ids as keys and design heat loads in Watt
        as values (default: None)
    """

    #  Take first index of ind['lhn'], as it is a list of lists
    #  (in this case with only one list element with all building nodes)
    feeder_id = random.choice(list_possible_feed)

    #  If space heating reference values are given and all other nodes should
    #  be set to no thermal supply, calculate lower SH reference value
    if dict_sh is not None and other_no_th_sup:
        #  Calculate minimum required space heating power of feeder node
        sh_power_min = 0
        #  Sum up space heating power demands
        for n in list_possible_feed:
            sh_power_min += dict_sh[n]
    else:
        sh_power_min = None

    #  Mutate feeder node with CHP, boiler, tes combi
    mutateesys.mut_esys_config_single_build(ind=ind, n=feeder_id,
                                            dict_restr=dict_restr,
                                            pv_min=pv_min,
                                            dict_max_pv_area=
                                            dict_max_pv_area,
                                            list_options=None,
                                            list_opt_prob=None,
                                            list_lhn_opt=None,
                                            list_lhn_prob=
                                            [0.7, 0.3, 0, 0, 0],
                                            dict_sh=dict_sh,
                                            sh_power_min=sh_power_min,
                                            add_pv_prop=add_pv_prop,
                                            add_bat_prob=add_bat_prob,
                                            dict_heatloads=dict_heatloads
                                            )

    if other_no_th_sup:
        #  Set all other LHN nodes to no thermal supply
        list_lhn_no_th = list(set(list_possible_feed) - set([feeder_id]))

        for n in list_lhn_no_th:
            esyschanges.set_th_supply_off(ind=ind, n=n)


def add_multiple_feeders(ind, dict_restr, pv_min, dict_max_pv_area,
                         list_possible_feed, other_no_th_sup=False,
                         dict_sh=None, add_pv_prop=0, add_bat_prob=0,
                         dict_heatloads=None):
    """
    Add multiple feeder nodes to LHN. Set all other nodes within
    list_possible_feed to no thermal supply.

    Parameters
    ----------
    ind : dict
        Individuum dict
    dict_restr : dict
        Dict holding possible energy system sizes
    pv_min : float
        Minimum possible PV area per building in m2
    dict_max_pv_area : dict
        Dict holding maximum usable PV area values in m2 per building
    list_possible_feed : list
        List with possible feeder ids
    other_no_th_sup : bool, optional
        If True, sets all other nodes in list_possible_feed to no thermal
        supply (default: False)
    dict_sh : dict, optional
        Dictionary holding building node ids as keys and maximum space heating
        power values in Watt as dict values (default: None). If not None,
        used for size limitation. If None, dict_restr is used for sizing.
    add_pv_prop : float, optional
        Defines additional probability of PV being changed, if only thermal
        mutation has been applied (defauft: 0). E.g. if boiler system has
        been changed to CHP, there is a change of add_pv_prob that also PV
        is mutated.
    add_bat_prob : float, optional
        Defines additional probability ofBAT being changed, if only thermal
        mutation has been applied (defauft: 0). E.g. if boiler system has
        been changed to CHP, there is a change of add_pv_prob that also BAT
        is mutated.
    dict_heatloads : dict, optional
        Dict holding building ids as keys and design heat loads in Watt
        as values (default: None)
    """

    if len(list_possible_feed) > 2:
        nb_feeders = random.randint(2, len(list_possible_feed))
    else:
        nb_feeders = 2

    list_feeders = random.sample(list_possible_feed, nb_feeders)

    for n in list_feeders:
        #  Mutate feeder node with CHP, boiler, tes combi
        mutateesys.mut_esys_config_single_build(ind=ind, n=n,
                                                dict_restr=dict_restr,
                                                pv_min=pv_min,
                                                dict_max_pv_area=
                                                dict_max_pv_area,
                                                list_options=None,
                                                list_opt_prob=None,
                                                list_lhn_opt=None,
                                                list_lhn_prob=
                                                [0.7, 0.3, 0, 0, 0],
                                                dict_sh=dict_sh,
                                                add_pv_prop=add_pv_prop,
                                                add_bat_prob=add_bat_prob,
                                                dict_heatloads=dict_heatloads)

        if other_no_th_sup:
            #  Set all other LHN nodes to no thermal supply
            list_lhn_no_th = list(set(list_possible_feed) - set(list_feeders))

            for n in list_lhn_no_th:
                esyschanges.set_th_supply_off(ind=ind, n=n)


def add_lhn_node(ind, idx_lhn, dict_restr,
                 dict_pos, max_dist=None, prob_nodes=[0.7, 0.3],
                 prob_lhn_mut=0.8, prob_no_th_sup=0.9, prob_closest=0.7,
                 dict_sh=None,
                 dict_heatloads=None):
    """
    Add single or multiple LHN nodes to network

    Parameters
    ----------
    ind : dict
        Individuum dictionary holding node ids with energy system dicts
        and 'lhn' with list of LHN subnetworks
    idx_lhn : int
        Index of LHN list ind['lhn], where node(s) should be added
    dict_restr : dict
        Dict holding possible energy system sizes
    dict_pos : dict
        Dict holding building node ids as keys and shapely point objects (2d)
        as values
    max_dist : float, optional
        Maximum allowed distance in m from building to building, which
        can be connected to LHN (default: None)
    prob_nodes : list, optional
        List holding probabilities that only one node is added (index 0)
        or multiple nodes can be added (index 1) (default: [0.7, 0.3])
    prob_lhn_mut : float, optional
        Defines probability of mutation being performed (e.g. 0.8 --> 80 %
        probability that LHN is mutated (default: 0.8)
    prob_no_th_sup : float, optional
        Probability that new node is no feeder (e.g. 0.9 --> 90 % probability
        that new node is not a feeder (default: 0.9)
    prob_closest : float, optional
        Probability, that closest node is added (e.g. 0.7 --> 70 % probability
        that closest node is added)
    dict_sh : dict, optional
        Dictionary holding building node ids as keys and maximum space heating
        power values in Watt as dict values (default: None). If not None,
        used for size limitation. If None, dict_restr is used for sizing.
    dict_heatloads : dict, optional
        Dict holding building ids as keys and design heat loads in Watt
        as values (default: None)
    """

    if len(ind['lhn']) == 0:  # pragma: no cover
        msg = 'ind has no LHN. Cannot add any new LHN node.'
        warnings.warn(msg)
        return

    if random.random() > prob_lhn_mut:  # pragma: no cover
        return  # Exit function

    # Get list of building node ids
    list_build_ids = analyse.get_build_ids_ind(ind=ind)

    #  Get list of all buildings, which are already connected to LHN(s)
    list_lhn_ids = findlhn.get_all_lhn_ids(ind=ind)

    # Get list of available building nodes to be connected to LHN
    list_av_ids = list(set(list_build_ids) - set(list_lhn_ids))

    if list_av_ids == []:  # pragma: no cover
        msg = 'No more nodes available to be added to LHN. Exit function.'
        warnings.warn(msg)
        return

    # Get list of LHN nodes of chosen LHN network
    list_sublhn = ind['lhn'][idx_lhn]

    #  Get dict with node ids as keys and distances (to list_sublhn nodes)
    #  as values
    list_tup_sorted = analyse. \
        get_list_ids_sorted_by_dist_to_ref_list(list_ref=list_sublhn,
                                                list_search=list_av_ids,
                                                dict_pos=dict_pos,
                                                max_dist=max_dist)

    #  Get maximum possible number of nodes, which could be added
    nb_new_lhn_max = len(list_tup_sorted)

    if nb_new_lhn_max == 0:  # pragma: no cover
        msg = 'nb_new_lhn_max is zero. Cannot add more nodes. Exit function.'
        warnings.warn(msg)
        return

    # Decide if one or multiple nodes should be added
    select_single_or_multi = \
        np.random.choice(a=['single', 'multi'], p=prob_nodes)

    if select_single_or_multi == 'single':
        #  Add single node

        if random.random() <= prob_closest or nb_new_lhn_max == 1:

            #  Take closest node to reference LHN
            new_id = list_tup_sorted[0][0]

        else:  # Take random node

            new_id = list_tup_sorted[random.
                randint(1, int(len(list_tup_sorted) - 1))][0]

        ind['lhn'][idx_lhn].append(new_id)

        #  Define, if new node is feeder or not
        if random.random() <= prob_no_th_sup:
            #  No thermal feeder
            esyschanges.set_th_supply_off(ind=ind, n=new_id)
        else:
            #  Add CHP feeder
            esyschanges.gen_chp_boi_tes(ind=ind, n=new_id,
                                        dict_restr=dict_restr,
                                        dict_sh=dict_sh,
                                        dict_heatloads=dict_heatloads
                                        )

    elif select_single_or_multi == 'multi':
        #  Add multiple nodes

        #  Select random number of available nodes
        if nb_new_lhn_max > 2:
            nb_new_lhn = random.randint(2, int(nb_new_lhn_max))
        elif nb_new_lhn_max == 2:
            nb_new_lhn = 2
        elif nb_new_lhn_max == 1:
            nb_new_lhn = 1

        for i in range(nb_new_lhn):
            #  Take closest node to reference LHN
            new_id = list_tup_sorted[i][0]
            ind['lhn'][idx_lhn].append(new_id)

            #  Define, if new node is feeder or not
            if random.random() <= prob_no_th_sup:
                #  No thermal feeder
                esyschanges.set_th_supply_off(ind=ind, n=new_id)
            else:
                #  Add CHP feeder
                esyschanges.gen_chp_boi_tes(ind=ind, n=new_id,
                                            dict_restr=dict_restr,
                                            dict_sh=dict_sh,
                                            dict_heatloads=dict_heatloads
                                            )


def del_lhn_node(ind, idx_lhn, dict_restr, pv_min, dict_max_pv_area,
                 dict_pos, prob_nodes=[0.7, 0.3],
                 prob_lhn_mut=0.8, list_options=None,
                 list_lhn_to_stand_alone=None,
                 dict_sh=None, add_pv_prop=0, add_bat_prob=0,
                 dict_heatloads=None):
    """
    Delete single or multiple LHN nodes

    Parameters
    ----------
    ind : dict
        Individuum dictionary holding node ids with energy system dicts
        and 'lhn' with list of LHN subnetworks
    idx_lhn : int
        Index of LHN list ind['lhn], where node(s) should be added
    dict_restr : dict
        Dict holding possible energy system sizes
    pv_min : float
        Minimum possible PV area per building in m2
    dict_max_pv_area : dict
        Dict holding maximum usable PV area values in m2 per building
    dict_pos : dict
        Dict holding building node ids as keys and shapely point objects (2d)
        as values
    prob_nodes : list, optional
        List holding probabilities that only one node is deleted (index 0)
        or multiple nodes are deleted(index 1) (default: [0.7, 0.3])
    prob_lhn_mut : float, optional
        Defines probability of mutation being performed (e.g. 0.8 --> 80 %
        probability that LHN is mutated (default: 0.8)
    list_options : list (of str), optional
        List holding strings with energy system options (default: None).
        If None, uses default values ['boi', 'boi_tes', 'chp_boi_tes',
        'chp_boi_eh_tes', 'hp_aw_eh', 'hp_ww_eh', 'hp_aw_boi', 'hp_ww_boi',
        'hp_aw_eh_boi', 'hp_ww_eh_boi', 'bat', 'pv']
    list_lhn_to_stand_alone : list (of floats)
        List holding probability factors for energy system options in
        list_options (default: None).
        If None, uses default values [0.1, 0.15, 0.25, 0.05, 0.125, 0.125,
        0.05, 0.05, 0.05, 0.05, 0, 0]
    dict_sh : dict, optional
        Dictionary holding building node ids as keys and maximum space heating
        power values in Watt as dict values (default: None). If not None,
        used for size limitation. If None, dict_restr is used for sizing.
    add_pv_prop : float, optional
        Defines additional probability of PV being changed, if only thermal
        mutation has been applied (defauft: 0). E.g. if boiler system has
        been changed to CHP, there is a change of add_pv_prob that also PV
        is mutated.
    add_bat_prob : float, optional
        Defines additional probability ofBAT being changed, if only thermal
        mutation has been applied (defauft: 0). E.g. if boiler system has
        been changed to CHP, there is a change of add_pv_prob that also BAT
        is mutated.
    dict_heatloads : dict, optional
        Dict holding building ids as keys and design heat loads in Watt
        as values (default: None)
    """
    if list_options is None:
        list_options = ['boi', 'boi_tes', 'chp_boi_tes', 'chp_boi_eh_tes',
                        'hp_aw_eh', 'hp_ww_eh', 'hp_aw_boi', 'hp_ww_boi',
                        'hp_aw_eh_boi', 'hp_ww_eh_boi', 'bat', 'pv']

    if list_lhn_to_stand_alone is None:
        #  Prevent bat and PV usage, as stand-alone building requires
        #  thermal supply
        list_lhn_to_stand_alone = [0.1, 0.15, 0.25, 0.05, 0.125, 0.125,
                                   0.05, 0.05, 0.05, 0.05, 0, 0]

    assert abs(sum(list_lhn_to_stand_alone) - 1) < 0.0000000001

    if len(ind['lhn']) == 0:  # pragma: no cover
        msg = 'ind has no LHN. Cannot delete any LHN node.'
        warnings.warn(msg)
        return

    if random.random() > prob_lhn_mut:  # pragma: no cover
        return  # Exit function

    # Get info about nb. of existing nodes in chosen LHN system
    nb_nodes = len(ind['lhn'][idx_lhn])

    if nb_nodes <= 2:  # pragma: no cover
        msg = 'Lhn has less than 3 nodes left. Thus, cannot delete nodes.'
        warnings.warn(msg)
        return

    # Decide if one or multiple nodes should be added
    select_single_or_multi = \
        np.random.choice(a=['single', 'multi'], p=prob_nodes)

    if nb_nodes == 3:  # Can only delete one node
        select_single_or_multi = 'single'

    if select_single_or_multi == 'single':

        #  Choose random node id
        id_del = np.random.choice(a=ind['lhn'][idx_lhn])

        #  TODO: Add method to erase node which is "out of center"

        #  Delete id from list
        ind['lhn'][idx_lhn].remove(id_del)

        #  Add energy system to stand-alone building
        mutateesys. \
            mut_esys_config_single_build(ind=ind, n=id_del,
                                         dict_restr=dict_restr,
                                         pv_min=pv_min,
                                         dict_max_pv_area=
                                         dict_max_pv_area,
                                         list_opt_prob=list_lhn_to_stand_alone,
                                         dict_sh=dict_sh,
                                         add_pv_prop=add_pv_prop,
                                         add_bat_prob=add_bat_prob,
                                         dict_heatloads=dict_heatloads)

    elif select_single_or_multi == 'multi':

        #  Select random number of nodes to be deleted (requires, at lest,
        #  2 nodes to be left
        if nb_nodes > 4:
            nb_del = random.randint(2, int(nb_nodes - 2))
        else:
            nb_del = 2

        # Draw random sample from available nodes
        list_ids_del = np.random.choice(a=ind['lhn'][idx_lhn], size=nb_del,
                                        replace=False)

        for n in list_ids_del:
            #  Delete id from list
            ind['lhn'][idx_lhn].remove(n)

            #  Add energy system to stand-alone building
            mutateesys. \
                mut_esys_config_single_build(ind=ind, n=n,
                                             dict_restr=dict_restr,
                                             pv_min=pv_min,
                                             dict_max_pv_area=
                                             dict_max_pv_area,
                                             list_opt_prob=
                                             list_lhn_to_stand_alone,
                                             add_pv_prop=add_pv_prop,
                                             add_bat_prob=add_bat_prob,
                                             dict_heatloads=dict_heatloads)


def add_lhn_feeder_node(ind, idx_lhn, dict_restr, pv_min, dict_max_pv_area,
                        prob_feed=[0.7, 0.3], prob_lhn_mut=0.8, dict_sh=None,
                        add_pv_prop=0, add_bat_prob=0,
                        dict_heatloads=None):
    """
    Add single or multiple LHN feeder node to LHN (LHN mutation)

    Parameters
    ----------
    ind : dict
        Individuum dictionary holding node ids with energy system dicts
        and 'lhn' with list of LHN subnetworks
    idx_lhn : int
        Index of LHN list ind['lhn], where node(s) should be added
    dict_restr : dict
        Dict holding possible energy system sizes
    pv_min : float
        Minimum possible PV area per building in m2
    dict_max_pv_area : dict
        Dict holding maximum usable PV area values in m2 per building
    prob_feed : list, optional
        List holding probabilities that only one feeder is added (index 0)
        or multiple feeders are added (index 1) (default: [0.7, 0.3])
    prob_lhn_mut : float, optional
        Defines probability of mutation being performed (e.g. 0.8 --> 80 %
        probability that LHN is mutated (default: 0.8)
    dict_sh : dict, optional
        Dictionary holding building node ids as keys and maximum space heating
        power values in Watt as dict values (default: None). If not None,
        used for size limitation. If None, dict_restr is used for sizing.
    add_pv_prop : float, optional
        Defines additional probability of PV being changed, if only thermal
        mutation has been applied (defauft: 0). E.g. if boiler system has
        been changed to CHP, there is a change of add_pv_prob that also PV
        is mutated.
    add_bat_prob : float, optional
        Defines additional probability ofBAT being changed, if only thermal
        mutation has been applied (defauft: 0). E.g. if boiler system has
        been changed to CHP, there is a change of add_pv_prob that also BAT
        is mutated.
    dict_heatloads : dict, optional
        Dict holding building ids as keys and design heat loads in Watt
        as values (default: None)
    """

    if len(ind['lhn']) == 0:  # pragma: no cover
        msg = 'ind has no LHN. Cannot add feeder node.'
        warnings.warn(msg)
        return

    if random.random() > prob_lhn_mut:  # pragma: no cover
        return  # Exit function

    # Get information about nodes in sublhn, which are no feeders, yet
    list_no_th_sup = analyse. \
        get_build_ids_without_th_supply(ind=ind,
                                        list_search=ind['lhn'][idx_lhn])

    if len(list_no_th_sup) == 0:  # pragma: no cover
        msg = 'No buildings without th. esys found. Cannot add feeder node.'
        warnings.warn(msg)
        return

    # If only one node is available, set select_single_or_multi to single
    if len(list_no_th_sup) == 1:
        select_single_or_multi = 'single'
    else:
        #  Decide, if one feeder or multiple feeders should be added
        select_single_or_multi = \
            np.random.choice(a=['single', 'multi'], p=prob_feed)

    if select_single_or_multi == 'single':
        #  Add single feeder
        add_single_feeder(ind=ind, dict_restr=dict_restr, pv_min=pv_min,
                          dict_max_pv_area=dict_max_pv_area,
                          list_possible_feed=list_no_th_sup,
                          dict_sh=dict_sh, add_pv_prop=add_pv_prop,
                          add_bat_prob=add_bat_prob,
                          dict_heatloads=dict_heatloads
                          )

    elif select_single_or_multi == 'multi':
        #  Add multiple feeder nodes
        add_multiple_feeders(ind=ind, dict_restr=dict_restr, pv_min=pv_min,
                             dict_max_pv_area=dict_max_pv_area,
                             list_possible_feed=list_no_th_sup,
                             dict_sh=dict_sh, add_pv_prop=add_pv_prop,
                             add_bat_prob=add_bat_prob,
                             dict_heatloads=dict_heatloads
                             )


def del_lhn_feeder(ind, idx_lhn, prob_feed=[0.7, 0.3], prob_lhn_mut=0.8):
    """
    Delete feeder node(s) in LHN system (mutate LHN)

    Parameters
    ----------
    ind : dict
        Individuum dictionary holding node ids with energy system dicts
        and 'lhn' with list of LHN subnetworks
    idx_lhn : int
        Index of LHN list ind['lhn], where node(s) should be added
    prob_feed : list, optional
        List holding probabilities that only one feeder is deleted (index 0)
        or multiple feeders are deleted (index 1) (default: [0.7, 0.3])
    prob_lhn_mut : float, optional
        Defines probability of mutation being performed (e.g. 0.8 --> 80 %
        probability that LHN is mutated (default: 0.8)
    """

    if len(ind['lhn']) == 0:  # pragma: no cover
        msg = 'ind has no LHN. Cannot add feeder node.'
        warnings.warn(msg)
        return

    if random.random() > prob_lhn_mut:  # pragma: no cover
        return  # Exit function

    # Get information about nodes in sublhn, which are no feeders
    list_no_th_sup = analyse. \
        get_build_ids_without_th_supply(ind=ind,
                                        list_search=ind['lhn'][idx_lhn])

    #  Get list of building node ids, which are feeders
    list_feeders = list(set(ind['lhn'][idx_lhn]) - set(list_no_th_sup))

    if len(list_feeders) <= 1:  # pragma: no cover
        msg = 'Only one feeder left. Cannot delete feeder node.'
        warnings.warn(msg)
        return

    # If only one node is available, set select_single_or_multi to single
    if len(list_feeders) == 2:
        select_single_or_multi = 'single'
    else:
        #  Decide, if one feeder or multiple feeders should be added
        select_single_or_multi = \
            np.random.choice(a=['single', 'multi'], p=prob_feed)

    if select_single_or_multi == 'single':
        #  Delete single feeder

        #  Select random node id of existing feeders
        id_del = np.random.choice(a=list_feeders)

        #  Remove feeder
        esyschanges.set_th_supply_off(ind=ind, n=id_del)

    elif select_single_or_multi == 'multi':
        #  Delete multiple feeder nodes

        if len(list_feeders) == 3:
            nb_del_fed = 2
        else:
            # Select random number of feeder nodes to be deleted
            nb_del_fed = random.randint(2, int(len(list_feeders) - 1))

        # Select random sample ids
        list_del_fed = np.random.choice(a=list_feeders, size=nb_del_fed,
                                        replace=False)

        #  Delete feeders
        for n in list_del_fed:
            #  Remove feeder
            esyschanges.set_th_supply_off(ind=ind, n=n)


def change_lhn_feeder_node(ind, idx_lhn, dict_restr, pv_min, dict_max_pv_area,
                           prob_feed=[0.7, 0.3], prob_lhn_mut=0.8,
                           dict_sh=None, add_pv_prop=0, add_bat_prob=0,
                           dict_heatloads=None):
    """
    Change position of single or multiple feeder nodes in LHN
    (LHN mutation)

    Parameters
    ----------
    ind : dict
        Individuum dictionary holding node ids with energy system dicts
        and 'lhn' with list of LHN subnetworks
    idx_lhn : int
        Index of LHN list ind['lhn], where node(s) should be added
    dict_restr : dict
        Dict holding possible energy system sizes
    pv_min : float
        Minimum possible PV area per building in m2
    dict_max_pv_area : dict
        Dict holding maximum usable PV area values in m2 per building
    prob_feed : list, optional
        List holding probabilities that only one feeder is changed (index 0)
        or multiple feeders are changed (index 1) (default: [0.7, 0.3])
    prob_lhn_mut : float, optional
        Defines probability of mutation being performed (e.g. 0.8 --> 80 %
        probability that LHN is mutated (default: 0.8)
    dict_sh : dict, optional
        Dictionary holding building node ids as keys and maximum space heating
        power values in Watt as dict values (default: None). If not None,
        used for size limitation. If None, dict_restr is used for sizing.
    add_pv_prop : float, optional
        Defines additional probability of PV being changed, if only thermal
        mutation has been applied (defauft: 0). E.g. if boiler system has
        been changed to CHP, there is a change of add_pv_prob that also PV
        is mutated.
    add_bat_prob : float, optional
        Defines additional probability ofBAT being changed, if only thermal
        mutation has been applied (defauft: 0). E.g. if boiler system has
        been changed to CHP, there is a change of add_pv_prob that also BAT
        is mutated.
    dict_heatloads : dict, optional
        Dict holding building ids as keys and design heat loads in Watt
        as values (default: None)
    """

    if len(ind['lhn']) == 0:  # pragma: no cover
        msg = 'ind has no LHN. Cannot add feeder node.'
        warnings.warn(msg)
        return

    if random.random() > prob_lhn_mut:
        return  # Exit function

    # Get information about nodes in sublhn, which are no feeders
    list_no_th_sup = analyse. \
        get_build_ids_without_th_supply(ind=ind,
                                        list_search=ind['lhn'][idx_lhn])

    #  Get list of building node ids, which are feeders
    list_feeders = list(set(ind['lhn'][idx_lhn]) - set(list_no_th_sup))

    if len(list_no_th_sup) == 0:  # pragma: no cover
        msg = 'All nodes are feeders. Cannot change feeder position in LHN.'
        warnings.warn(msg)
        return

    if len(list_feeders) == 0:  # pragma: no cover
        msg = 'LHN has currently no feeders. Thus, cannot change feeder ' \
              'position.'
        warnings.warn(msg)
        return

    # If only one node is available, set select_single_or_multi to single
    if len(list_feeders) == 1 or len(list_no_th_sup) == 1:
        select_single_or_multi = 'single'
    elif len(list_feeders) > 1 and len(list_no_th_sup) > 1:
        #  Decide, if one feeder or multiple feeders should be added
        select_single_or_multi = \
            np.random.choice(a=['single', 'multi'], p=prob_feed)
    elif len(list_feeders) >= 1 and len(list_no_th_sup) >= 1:
        select_single_or_multi = 'single'
    else:
        return

    if select_single_or_multi == 'single':
        #  Change single feeder

        #  Sample id (Add new feeder)
        id_feed_new = np.random.choice(a=list_no_th_sup)

        #  Sample id (Delete old feeder)
        id_feed_del = np.random.choice(a=list_feeders)

        #  Add new feeder
        add_single_feeder(ind=ind, dict_restr=dict_restr, pv_min=pv_min,
                          dict_max_pv_area=dict_max_pv_area,
                          list_possible_feed=[id_feed_new],
                          dict_sh=dict_sh, add_pv_prop=add_pv_prop,
                          add_bat_prob=add_bat_prob,
                          dict_heatloads=dict_heatloads)

        #  Delete old feeder
        esyschanges.set_th_supply_off(ind=ind, n=id_feed_del)

    elif select_single_or_multi == 'multi':
        #  Change multiple feeder nodes

        if len(list_feeders) == 2 and len(list_no_th_sup) == 2:
            nb_fed_change = 2
        elif len(list_feeders) > 2 and len(list_no_th_sup) > 2:
            # Select random number of feeder nodes to be deleted

            #  Select smaller list
            if len(list_feeders) <= len(list_no_th_sup):
                nb_change_max = len(list_feeders)
            else:
                nb_change_max = len(list_no_th_sup)

            nb_fed_change = random.randint(2, int(nb_change_max))
        else:
            msg = 'Number of feeder nodes or nodes without thermal energy ' \
                  'supply are lower than 2. ' \
                  'Cannot change feeder position in LHN.'
            warnings.warn(msg)
            return

        # Draw sample of feeders to be added
        list_ids_new = np.random.choice(a=list_no_th_sup, size=nb_fed_change,
                                        replace=False)
        #  Draw sample of feeders to be deleted
        list_ids_del = np.random.choice(a=list_feeders, size=nb_fed_change,
                                        replace=False)

        for i in range(len(list_ids_del)):
            id_new = list_ids_new[i]
            id_del = list_ids_del[i]

            #  Add new feeder
            add_single_feeder(ind=ind, dict_restr=dict_restr, pv_min=pv_min,
                              dict_max_pv_area=dict_max_pv_area,
                              list_possible_feed=[id_new], dict_sh=dict_sh,
                              add_pv_prop=add_pv_prop,
                              add_bat_prob=add_bat_prob,
                              dict_heatloads=dict_heatloads)

            #  Delete old feeder
            esyschanges.set_th_supply_off(ind=ind, n=id_del)
