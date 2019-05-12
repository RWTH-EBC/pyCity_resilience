#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Parse city information to individuum of GA run
"""
from __future__ import division

import pycity_calc.toolbox.networks.network_ops as netop

import pycity_resilience.ga.verify.check_validity as checkval


def parse_city_to_ind_dict(city, list_build_ids=None,
                           check_validity=True):
    """
    Returns GA individuum dict with city information

    Parameters
    ----------
    city : object
        City object of pyCity_calc. Should hold demand energy systems
    list_build_ids : list (of ints)
        List with building node ids (default: None). If None, searches for
        all building node ids in city.
    check_validity : bool, optional
        Checks if generated dict_ind is valid (default: True)

    Returns
    -------
    dict_ind : dict
        Dictionary to form individuum for GA run
    """

    dict_ind = {}

    if list_build_ids is None:
        list_build_ids = city.get_list_build_entity_node_ids()

    #  Initialize empty dicts for every building node id
    for n in list_build_ids:#
        dict_ind[n] = {}

    #  Add energy system
    for n in list_build_ids:
        build = city.nodes[n]['entity']

        if build.bes.hasBattery:
            dict_ind[n]['bat'] = build.bes.battery.capacity  # in Joule
        else:
            dict_ind[n]['bat'] = 0

        if build.bes.hasBoiler:
            dict_ind[n]['boi'] = build.bes.boiler.qNominal  # in Watt
        else:
            dict_ind[n]['boi'] = 0

        if build.bes.hasChp:
            dict_ind[n]['chp'] = build.bes.chp.qNominal  # in Watt
        else:
            dict_ind[n]['chp'] = 0

        if build.bes.hasElectricalHeater:
            dict_ind[n]['eh'] = build.bes.electricalHeater.qNominal  # in Watt
        else:
            dict_ind[n]['eh'] = 0

        if build.bes.hasHeatpump:
            #  Distinguish between air/water (aw) and water/water (ww) hp
            if build.bes.heatpump.hp_type == 'aw':
                dict_ind[n]['hp_aw'] = build.bes.heatpump.qNominal  # in Watt
                dict_ind[n]['hp_ww'] = 0
            elif build.bes.heatpump.hp_type == 'ww':
                dict_ind[n]['hp_ww'] = build.bes.heatpump.qNominal  # in Watt
                dict_ind[n]['hp_aw'] = 0
            else:  # pragma: no cover
                msg = 'Unknown heat pump hp_type. Can only be aw or ww.'
                raise AssertionError(msg)
        else:
            dict_ind[n]['hp_aw'] = 0
            dict_ind[n]['hp_ww'] = 0

        if build.bes.hasPv:
            dict_ind[n]['pv'] = build.bes.pv.area  # in m2
        else:
            dict_ind[n]['pv'] = 0

        if build.bes.hasTes:
            dict_ind[n]['tes'] = build.bes.tes.capacity  # in kg
        else:
            dict_ind[n]['tes'] = 0

    #  Add LHN information
    list_lhn_subnetworks = netop.\
        get_list_with_energy_net_con_node_ids(city=city,
                                              build_node_only=True)

    if list_lhn_subnetworks is None:
        list_lhn_subnetworks = []
    else:
        #  Sort original list_lhn_subnetworks
        list_lhn_subnetworks.sort()

    dict_ind['lhn'] = list_lhn_subnetworks

    #  Check_validity
    if check_validity:  # pragma: no cover
        if checkval.check_ind_is_valid(ind=dict_ind) is False:
            msg = 'Generated dict_ind is invalid!'
            raise AssertionError(msg)

    return dict_ind

def hand_over_dict(dict_ind=None, city=None, list_build_ids=None):
    """
    Hand over individual city dict to GA. If dict is None and city is set,
    generates dict out of city object.

    parse_city_to_ind_dict would be enough to generate individuum dicts.
    However, hand_over_dicts allows to also hand over other dicts in a simply
    way.

    Parameters
    ----------
    dict_ind : dict
        Dict for city individuum (default: None). If None, tries to generate
        dict_ind based on given city object
    city : object
        City object of pyCity_calc. Should hold energy systems (default: None)
    list_build_ids : list (of ints)
        List with building node ids (default: None). If None, searches for
        all building node ids in city.

    Returns
    -------
    dict_ind : dict
        Dict for city individuum (default: None). If None, tries to generate
        dict_ind based on given city object
    """

    if dict_ind is None:

        if city is None:  # pragma: no cover
            msg = 'City cannot be None, if dict_ind is None. You have to ' \
                  'hand over a city object instance!'
            raise AssertionError(msg)
        else:
            dict_ind = parse_city_to_ind_dict(city=city,
                                              list_build_ids=list_build_ids)

    return dict_ind
