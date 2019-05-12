#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to extract position as dict
"""
from __future__ import division


def get_build_pos(city):
    """
    Returns dict with building node ids as keys

    Parameters
    ----------
    city : object
        City object of pyCity_calc

    Returns
    -------
    dict_pos : dict
        Dict holding building node ids as keys and shapely point objects (2d)
        as values
    """

    #  Get list with building node ids
    list_build_ids = city.get_list_build_entity_node_ids()

    #  Initialize empty dict
    dict_pos = {}

    for n in list_build_ids:
        pos = city.nodes[n]['position']
        dict_pos[n] = pos

    return dict_pos
