#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to parse info of ga individuum to city object
"""
from __future__ import division

import copy

import pycity_calc.toolbox.dimensioning.dim_networks as dimnet
import pycity_calc.toolbox.networks.network_ops as netop

import pycity_resilience.ga.verify.check_validity as checkval


def parse_ind_dict_to_city(dict_ind, city, list_build_ids=None,
                           use_street=False, check_validity=True,
                           copy_city=True):
    """
    Parses individuum dict info to city object

    Parameters
    ----------
    dict_ind : dict
        Dictionary to form individuum for GA run
    city : object
        City object of pyCity_calc (going to be modified)
    list_build_ids : list (of ints)
        List with building node ids (default: None). If None, searches for
        all building node ids in city.
    use_street : bool, optional
        Use street networks to route LHN pipelines (default: False)
        Requires street nodes and edges on city graph, is use_street == True
    check_validity : bool, optional
        Checks if dict_ind is valid (default: True)
    copy_city : bool, optional
        If True, make copy of original city object

    Return
    ------
    city : object
        City object of pyCity_calc holding esys of dict_ind
    """

    if copy_city:  # Make deepcopy of city
        city = copy.deepcopy(city)

    assert dict_ind != {}
    assert dict_ind is not None

    #  Check_validity
    if check_validity:  # pragma: no cover
        if checkval.check_ind_is_valid(ind=dict_ind) is False:
            msg = 'Generated dict_ind is invalid!'
            raise AssertionError(msg)

    #  If no list of building node ids is given, get list by looping over city
    if list_build_ids is None:
        list_build_ids = city.get_list_build_entity_node_ids()

    # Add energy system to city
    for n in list_build_ids:
        build = city.nodes[n]['entity']

        if dict_ind[n]['bat'] > 0:
            build.bes.hasBattery = True
            build.bes.battery.capacity = dict_ind[n]['bat']  # in Joule
            build.bes.battery.self_discharge = 0
        else:
            build.bes.hasBattery = False
            build.bes.battery.capacity = 0.000000001  # in Joule

        if dict_ind[n]['boi'] > 0:
            build.bes.hasBoiler = True
            build.bes.boiler.qNominal = dict_ind[n]['boi']  # in Watt
        else:
            build.bes.hasBoiler = False
            build.bes.boiler.qNominal = 0.000000001 # in Watt

        if dict_ind[n]['chp'] > 0:
            build.bes.hasChp = True
            build.bes.chp.qNominal = dict_ind[n]['chp']  # in Watt
            build.bes.chp.run_precalculation(q_nominal=build.bes.chp.qNominal,
                                             eta_total=build.bes.chp.omega)
        else:
            build.bes.hasChp = False
            build.bes.chp.qNominal = 0.000000001 # in Watt
            build.bes.chp.pNominal = 0.000000001  # in Watt

        if dict_ind[n]['eh'] > 0:
            build.bes.hasElectricalHeater = True
            build.bes.electricalHeater.qNominal = dict_ind[n]['eh']  # in Watt
        else:
            build.bes.hasElectricalHeater = False
            build.bes.electricalHeater.qNominal = 0.000000001

        if dict_ind[n]['hp_aw'] > 0 and dict_ind[n]['hp_ww'] > 0:  # pragma: no cover
            msg = 'aw and ww cannot be larger than zero at the same time!'
            raise AssertionError(msg)

        if dict_ind[n]['hp_aw'] > 0:
            build.bes.hasHeatpump = True
            build.bes.heatpump.qNominal = dict_ind[n]['hp_aw']  # in Watt
            build.bes.heatpump.change_hp_type(hp_type='aw')
        elif dict_ind[n]['hp_ww'] > 0:
            build.bes.hasHeatpump = True
            build.bes.heatpump.qNominal = dict_ind[n]['hp_ww']  # in Watt
            build.bes.heatpump.change_hp_type(hp_type='ww')
        else:
            build.bes.hasHeatpump = False
            build.bes.heatpump.qNominal = 0.000000001

        if dict_ind[n]['pv'] > 0:
            build.bes.hasPv = True
            build.bes.pv.area = dict_ind[n]['pv']  # in m2
        else:
            build.bes.hasPv = False
            build.bes.pv.area = 0.000000001

        if dict_ind[n]['tes'] > 0:
            build.bes.hasTes = True
            build.bes.tes.capacity = dict_ind[n]['tes']  # in kg
            if dict_ind[n]['hp_aw'] > 0 or dict_ind[n]['hp_ww'] > 0:
                build.bes.tes.t_max = 40
                build.bes.tes.t_init = 35
                build.bes.tes.t_current = 35
            else:
                build.bes.tes.t_max = 60
                build.bes.tes.t_init = 55
                build.bes.tes.t_current = 55
        else:
            build.bes.hasTes = False
            build.bes.tes.capacity = 0.000000001

    # Add LHN networks
    #  ##################################################################
    #   Clear heating networks, if existent
    list_lhn_edges = netop.search_lhn_all_edges(city=city)
    city.remove_edges_from(list_lhn_edges)

    #  Add new subnetworks
    if dict_ind['lhn'] is not None and dict_ind['lhn'] != []:
        for list_sub_lhn in dict_ind['lhn']:
            #  Dimension new sub-LHN between given buildings
            dimnet.add_lhn_to_city(city=city, list_build_node_nb=list_sub_lhn,
                                   use_street_network=use_street)

    return city