#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

"""
from __future__ import division

import warnings

def get_dict_usable_pv_areas(city, list_build_ids=None):
    """
    Extract dictionary holding building nodes as keys and max. usable pv areas
    in m2 as values

    Parameters
    ----------
    city : object
        City object of pyCity_calc

    Returns
    -------
    dict_max_pv_area : dict (of floats)
        Dictionary holding building nodes as keys and max. usable pv areas
        in m2 as values
    """

    dict_max_pv_area = {}

    if list_build_ids is None:
        #  Extract building ids form city
        list_build_ids = city.get_list_build_entity_node_ids()

    for n in list_build_ids:
        build = city.nodes[n]['entity']
        if build.roof_usabl_pv_area is None:
            msg = 'Usable PV area of building ' + str(n) + ' is None! Thus,' \
                                                           ' it is set to zero'
            warnings.warn(msg)
            pv_use_area = 0
        else:
            pv_use_area = build.roof_usabl_pv_area + 0.0

        dict_max_pv_area[n] = pv_use_area

    return dict_max_pv_area


def get_net_foor_area(city, list_build_ids=None):
    """
    Extract dictionary holding building nodes as keys and net floor areas
    in m2 as values

    Parameters
    ----------
    city : object
        City object of pyCity_calc

    Returns
    -------
    dict_nfa : dict (of floats)
        Dictionary holding building nodes as keys and net floor areas
        in m2 as values
    """

    dict_nfa = {}

    if list_build_ids is None:
        #  Extract building ids form city
        list_build_ids = city.get_list_build_entity_node_ids()

    for n in list_build_ids:
        build = city.nodes[n]['entity']
        if build.net_floor_area is None:
            msg = 'Net floor area of building ' \
                  + str(n) + ' is None!'
            warnings.warn(msg)
            nfa = None
        else:
            nfa = build.net_floor_area + 0.0

        dict_nfa[n] = nfa

    return dict_nfa
