#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to parse dictionary information to individuum
"""
from __future__ import division


def parse_dict_info_to_ind(dict_ind, ind):
    """
    Add dictionary infos to individuum object

    Parameters
    ----------
    dict_ind : dict
        Dict holding individuum info
    ind : object
        Individuum object of deap toolbox
    """

    for key in dict_ind.keys():  #  Loop over keys (node nb. and 'lhn')
        if key != 'lhn':
            #  Loop over energy systems
            for esys_key in dict_ind[key]:
                ind[key][esys_key] = dict_ind[key][esys_key]
        else:
            ind[key] = dict_ind[key]
