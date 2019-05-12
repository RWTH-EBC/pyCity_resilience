#!/usr/bin/env python
# coding=utf-8
"""
Script estimates design heat load for space heating AND hot water supply
for residential buildings, based on Recknagel 2015
"""
from __future__ import division

import warnings
import pycity_resilience.ga.preprocess.pv_areas as pvareas


def main():
    nfa = 700
    build_standard = 'old'

    heat_load = est_sh_dhw_design_hl(nfa=nfa,
                                     build_standard=build_standard)

    print('Heat load estimation in kW:')
    print(round(heat_load) / 1000)


def est_sh_dhw_design_hl(nfa, build_standard='old'):
    """
    Estimates design heat load for space heating AND hot water, based on
    Sprenger, Eberhard; Recknagel, Hermann; Albers, Karl-Josef (2016):
    Taschenbuch für Heizung + Klimatechnik 2017/2018. 78. Aufl. München:
    DIV Deutscher Industrieverlag.
    Online verfügbar unter
    http://scifo.de/nc/kundenbereich/pdf-ansicht/media/download/Product/?tx_acmmam_acmmam%5Buid%5D%5Buid%5D=10324.

    Parameters
    ----------
    nfa : float
        Net floor area (heated area) in m2
    build_standard : str, optional
        String defining building standard (default: 'old')
        Options:
        - 'old': Around 150 W/m2
        - 'average': Around 100 W/m2
        - 'modern': Around 50 W/m2

    Returns
    -------
    heat_load : float
        Estimator of design heat load for space heating and hot water in Watt
    """

    assert nfa > 0
    if build_standard not in ['old', 'average', 'modern']:
        msg = 'Unknown building_standard input ' + str(build_standard)
        raise AssertionError(msg)

    if nfa < 100:
        msg = 'Net floor areas below 100 m2 might lead to invalid results!'
        warnings.warn(msg)

    if build_standard == 'old':
        heat_load = nfa * 150
    elif build_standard == 'average':
        if nfa >= 200:
            heat_load = nfa * 100
        else:
            heat_load = nfa * 150
    elif build_standard == 'modern':
        if nfa >= 900:
            heat_load = nfa * 50
        elif nfa <= 200:
            heat_load = nfa * 150
        elif nfa <= 400:
            heat_load = nfa * 100
        elif nfa <= 900:
            heat_load = nfa * 70

    return heat_load


def calc_heat_load_per_building(city, build_standard='old'):
    """
    Estimate building design heat load for space heating and hot water
    for each building

    Parameters
    ----------
    city : object
        City object of pyCity_calc
    build_standard : str, optional
        String defining building standard (default: 'old')
        Options:
        - 'old': Around 150 W/m2
        - 'average': Around 100 W/m2
        - 'modern': Around 50 W/m2

    Returns
    -------
    dict_heatloads : dict
        Dict holding building ids as keys and design heat loads in Watt
        as values
    """

    #  Get net floor areas of each building
    dict_nfa = pvareas.get_net_foor_area(city=city)

    dict_heatloads = {}

    for key in dict_nfa.keys():
        heat_load = est_sh_dhw_design_hl(nfa=dict_nfa[key],
                                         build_standard=build_standard)
        dict_heatloads[key] = heat_load

    return dict_heatloads


if __name__ == '__main__':
    main()
