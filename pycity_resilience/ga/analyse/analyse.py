#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

"""
from __future__ import division

import copy

import pycity_calc.toolbox.networks.network_ops as netop


def get_build_ids_ind(ind):
    """
    Returns list of building node ids of dict (without 'lhn' key)

    Parameters
    ----------
    ind : dict
        Individuum dict

    Returns
    -------
    list_ids : list
        List of building node ids on ind
    """

    list_ids = copy.copy(list(ind.keys()))
    if 'lhn' in list_ids:
        list_ids.remove('lhn')

    return list_ids


def get_build_ids_without_th_supply(ind, list_search=None):
    """
    Returns list of building node ids, which do not have internal thermal
    supply/no thermal energy supply units (but can be connected to LHN).

    Parameters
    ----------
    ind : dict
        Individuum dict
    list_search : list, optional
        List of ids, which should be used for search (default: None).
        If set to None, uses all keys in ind dict to search for ids without
        thermal energy supply.

    Returns
    -------
    list_no_th_sup : list
        List holding building ids without own thermal supply units
    """

    if list_search is None:
        list_search = get_build_ids_ind(ind=ind)

    list_no_th_sup = []

    for n in list_search:
        #  Assume that building has no thermal supply, until supply is found
        has_th_sup = False

        if ind[n]['boi'] > 0:
            has_th_sup = True
        elif ind[n]['chp'] > 0:
            has_th_sup = True
        elif ind[n]['hp_aw'] > 0:
            has_th_sup = True
        elif ind[n]['hp_ww'] > 0:
            has_th_sup = True
        elif ind[n]['eh'] > 0:
            has_th_sup = True

        if has_th_sup is False:
            list_no_th_sup.append(n)

    return list_no_th_sup


def get_ids_sorted_by_dist(id, dict_pos, list_av=None, max_dist=None):
    """
    Return (new) list of ids sorted by distance to reference point n
    (list does NOT include n itself!).

    Parameters
    ----------
    id : int
        Reference point id
    dict_pos : dict
        Dict holding building node ids as keys and shapely point objects (2d)
        as values
    list_av : list, optional
        List of available building node ids for LHN connection (default: None).
        If None, uses all nodes in dict_pos
    max_dist : float, optional
        Maximum allowed distance in m from building to building, which
        can be connected to LHN (default: None).

    Returns
    -------
    list_sorted : list
        List of sorted node ids (sorted by distance to reference point n)
    """

    if id not in dict_pos.keys():
        msg = 'Reference node ' + str(id) + ' is not in dict_pos.keys()!'
        raise AssertionError(msg)

    if list_av is None:
        list_av = list(dict_pos.keys())
    else:
        for n in list_av:
            if n not in dict_pos.keys():
                msg = 'Node ' + str(n) + ' is not in dict_pos.keys()!'
                raise AssertionError(msg)

    if id in list_av:
        list_av.remove(id)

    list_sorted = copy.copy(list_av)

    #  Get position of reference point
    p1 = dict_pos[id]

    list_dist = []
    for i in range(len(list_av)):
        p2 = dict_pos[list_av[i]]
        dist = netop.calc_point_distance(point_1=p1, point_2=p2)
        list_dist.append(dist)

    # Sort dist_list and node_list by dist_list distance values
    tuple_dist, tuple_sorted = zip(*sorted(zip(list_dist, list_sorted)))

    #  Convert to lists
    list_dist = list(tuple_dist)
    list_sorted = list(tuple_sorted)

    if max_dist is not None:
        list_sorted_max = []
        #  Erase all dist values larger than max_dist
        for i in range(len(list_dist)):
            if list_dist[i] < max_dist:
                list_sorted_max.append(list_sorted[i])
            else:
                break
        # Overwrite
        list_sorted = list_sorted_max

    return list_sorted


def get_ids_closest_dist_to_list_of_build(list_ref, list_search, dict_pos,
                                          max_dist=None):
    """
    Returns dict with node ids as keys and distances as values
    (distances to set of reference nodes)

    Parameters
    ----------
    list_ref : list (of ints)
        List with reference node ids, used as reference points for distance
        calculation
    list_search list (of ints):
        List with search nodes
    dict_pos : dict
        Dict holding building node ids as keys and shapely point objects (2d)
        as values
    max_dist : float, optional
        Maximum allowed distance in m from building to building, which
        can be connected to LHN (default: None).

    Returns
    -------
    dict_dist : dict
        Dict with node ids as keys and distances as values (distances to set
        of reference nodes)
    """

    #  Dict to add node u ids as values and with distance to set of nodes n
    #  as values
    dict_dist = {}

    for n in list_ref:  # Loop over reference nodes
        for u in list_search:
            if n != u:
                p1 = dict_pos[n]
                p2 = dict_pos[u]
                dist = netop.calc_point_distance(point_1=p1, point_2=p2)
                #  If node u not  in dict_dist, add it
                if u not in dict_dist.keys():
                    dict_dist[u] = dist
                else:  # If already existent, check if distance is smaller
                    if dict_dist[u] > dist:
                        dict_dist[u] = dist

    if max_dist is not None:
        #  copy dict_dist
        dict_dist_copy = copy.copy(dict_dist)

        #  Delete entries with distance above max_dist
        for key in dict_dist.keys():
            if dict_dist[key] > max_dist:
                #  Save key for deletion
                del dict_dist_copy[key]

        # Overwrite dict_dist with cleaned-up one
        dict_dist = dict_dist_copy

    return dict_dist


def get_list_ids_sorted_by_dist_to_ref_list(list_ref, list_search, dict_pos,
                                            max_dist=None):
    """
    Returns list of tuples holding building ids (index 0) and min. distance
    (index 1) of node to reference nodes of list_ref.

    Parameters
    ----------
    list_ref : list (of ints)
        List with reference node ids, used as reference points for distance
        calculation
    list_search list (of ints):
        List with search nodes
    dict_pos : dict
        Dict holding building node ids as keys and shapely point objects (2d)
        as values
    max_dist : float, optional
        Maximum allowed distance in m from building to building, which
        can be connected to LHN (default: None).

    Returns
    -------
    list_sorted : list (of tuples)
        List holding tuples with building id and distance
        (sorted building ids of list_search (sorted by distance
        to nodes in list_ref))
    """
    dict_dist = \
        get_ids_closest_dist_to_list_of_build(list_ref=list_ref,
                                              list_search=list_search,
                                              dict_pos=dict_pos,
                                              max_dist=max_dist)

    list_sorted = list(sorted(dict_dist.items(),
                              key=lambda dict_dist: dict_dist[1]))

    return list_sorted
