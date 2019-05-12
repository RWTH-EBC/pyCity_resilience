#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to check if node in individuum dict is connected to LHN
"""
from __future__ import division


def has_lhn_connection(ind, id):
    """
    Returns True, if node n of individuum ind has LHN connection. Else: False.

    Parameters
    ----------
    ind : dict
        Individuum dict
    id : int
        ID of building node

    Returns
    -------
    has_lhn : bool
        True, if node n has LHn connection. False, if not connected to LHN
    """

    if id not in ind:
        msg = 'Node ' + str(id) + ' is not within individuum ' + str(ind)
        raise AssertionError(msg)

    if 'lhn' not in ind:
        msg = 'Individuum dict does not have lhn attribute. Check input data.'
        raise AssertionError(msg)

    has_lhn = False  # Assumes no connection to LHN

    if len(ind['lhn']) > 0:
        #  Has LHN network(s)
        for sublhn in ind['lhn']:  # Loop over subnetworks
            for n in sublhn:  # Loop over nodes in network
                if n == id:
                    has_lhn = True
                    return has_lhn

    return has_lhn


def get_all_lhn_ids(ind):
    """
    Returns list of ids of ind, which hold LHN connections

    Parameters
    ----------
    ind : dict
        Individuum dict

    Returns
    -------
    list_lhn_ids : list
        List holding ids of ind, which hold LHN connection
    """

    list_lhn_ids = []

    if len(ind['lhn']) > 0:
        for sublhn in ind['lhn']:
            for n in sublhn:
                list_lhn_ids.append(n)

    return list_lhn_ids


if __name__ == '__main__':

    ind = {1001: {}, 1002: {}, 1003: {}, 'lhn': [[1002, 1003]]}

    id = 1002

    assert has_lhn_connection(ind=ind, id=id) is True

    ind = {1001: {}, 1002: {}, 1003: {}, 'lhn': [[1003, 1004]]}

    assert has_lhn_connection(ind=ind, id=id) is False
