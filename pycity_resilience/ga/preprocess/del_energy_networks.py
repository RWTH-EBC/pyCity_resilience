#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to delete energy networks in city
"""
from __future__ import division

#  TODO: Move to pyCity_calc
def del_energy_network_in_city(city):
    """
    Deletes all energy networks (heating, heating_and_deg, electricity) on
    city object.

    Parameters
    ----------
    city : object
        City object instance of pyCity_calc
    """

    list_edge_tuple_del = []

    for (u, v, ntype) in city.edges.data('network_type', default=None):
        if (ntype == 'heating' or ntype == 'heating_and_deg'
            or ntype == 'electricity'):
            list_edge_tuple_del.append((u, v))

    city.remove_edges_from(list_edge_tuple_del)
