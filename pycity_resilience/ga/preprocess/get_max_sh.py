#!/usr/bin/env python
# coding=utf-8
"""
Script to generate dict holding maximum space heating power values for
each building node
"""
from __future__ import division

import os
import pickle

import pycity_calc.toolbox.dimensioning.dim_functions as dimfunc


def get_dict_max_sh_city(city):
    """
    Returns dictionary holding maximum space heating power values in Watt
    for each building node

    Parameters
    ----------
    city : object
        City object of pyCity_calc

    Returns
    -------
    dict_sh : dict
        Dictionary holding building node ids as keys and maximum space heating
        power values in Watt as dict values
    """

    list_build_nodes = city.get_list_build_entity_node_ids()

    dict_sh = {}

    for n in list_build_nodes:
        build = city.nodes[n]['entity']
        sh_power = dimfunc.get_max_power_of_building(building=build,
                                                     get_therm=True,
                                                     with_dhw=False)

        dict_sh[n] = sh_power

    return dict_sh


if __name__ == '__main__':
    #  Get workspace path
    #  #############################################################
    this_path = os.path.dirname(os.path.abspath(__file__))
    src_path = os.path.dirname(os.path.dirname(os.path.dirname(this_path)))
    path_workspace = os.path.join(src_path, 'workspace')
    #  #############################################################

    city_name = 'city_2_build_with_esys.pkl'

    city_path = os.path.join(path_workspace, 'city_objects', 'with_esys',
                             city_name)

    city = pickle.load(open(city_path, mode='rb'))

    dict_sh = get_dict_max_sh_city(city=city)

    for key in dict_sh.keys():
        print('Key: ', key)
        print('Space heating power in kW: ', round(dict_sh[key]/1000, 2))
        print()
