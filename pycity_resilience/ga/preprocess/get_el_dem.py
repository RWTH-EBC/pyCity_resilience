#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

"""
from __future__ import division


def get_dict_el_dem_city(city):
    """
    Returns dict holding building ids as keys and electric energy demands as
    values

    Parameters
    ----------
    city : object
        City object of pyCity_calc

    Returns
    -------
    dict_el_dem : dict
        Dict. holding building ids as keys and electric energy demands per
        building in kWh/a as values
    """

    dict_el_dem = {}

    list_build_ids = city.get_list_build_entity_node_ids()

    for n in list_build_ids:
        build = city.nodes[n]['entity']
        el_dem = build.get_annual_el_demand()
        dict_el_dem[n] = el_dem

    return dict_el_dem


def get_id_and_max_el_dem(dict_el_dem):
    """
    Returns id (key in dict_el_dem) and max. el. demand (value in dict_el_dem)

    Parameters
    ----------
    dict_el_dem : dict
        Dict. holding building ids as keys and electric energy demands per
        building in kWh/a as values

    Returns
    -------
    tup_res : tuple
        2d tuple holding building id of building with max. annual el. demand
        and corresponding el. demand value in kWh (id, el_dem)
    """

    id = max(dict_el_dem, key=dict_el_dem.get)
    el_dem = dict_el_dem[id]

    return (id, el_dem)


if __name__ == '__main__':

    dict_test = {1001: 20000, 1002: 30000, 1003: 15000}

    (id, el_dem) = get_id_and_max_el_dem(dict_el_dem=dict_test)

    print('Id: ', id)
    print('El. demand in kWh/a: ', el_dem)
