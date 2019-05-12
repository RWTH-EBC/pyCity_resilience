#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

"""
from __future__ import division

import os
import pickle
import copy
import random as rd
import numpy as np
import warnings
import math
import matplotlib.pylab as plt

import pycity_calc.toolbox.dimensioning.dim_functions as dimfunc
import pycity_calc.cities.scripts.energy_sys_generator as esysgen
import pycity_calc.cities.scripts.energy_network_generator as enetgen
import pycity_calc.simulation.energy_balance.city_eb_calc as citeb
import pycity_calc.economic.annuity_calculation as annu
import pycity_calc.economic.city_economic_calc as citecon
import pycity_calc.toolbox.modifiers.mod_resc_peak_load_day as modpeak

import pycity_resilience.ga.preprocess.get_pos as getpos
import pycity_resilience.ga.parser.parse_city_to_ind as parsecity
import pycity_resilience.ga.parser.parse_dict_to_ind as parsedictind
import pycity_resilience.ga.parser.parse_ind_to_city as parseindcit
import pycity_resilience.ga.preprocess.add_bes as addbes
import pycity_resilience.ga.preprocess.pv_areas as pvareas
import pycity_resilience.ga.evolution.mutation_esys as mutesys
import pycity_resilience.monte_carlo.run_mc as runmc
import pycity_resilience.ga.opt_ga as optga
import pycity_resilience.ga.clustering.cluster as clust
import pycity_resilience.ga.preprocess.del_energy_networks as delnet
import pycity_resilience.ga.verify.check_validity as checkval
import pycity_resilience.ga.evaluate.eval as eval
import pycity_resilience.ga.preprocess.get_max_sh as getmaxsh
import pycity_resilience.ga.preprocess.get_el_dem as getel
import pycity_resilience.ga.evolution.helpers.mod_esys_prob as modprob
import pycity_resilience.ga.analyse.analyse as analyse
import pycity_resilience.ga.preprocess.est_sh_dhw_design_heat_load as estdhl

from deap import base, creator, tools, algorithms


def find_nearest(arr, val):
    """
    Find closest value in arrary (arr) to val

    Parameters
    ----------
    arr : array-like
        Array holding search values
    val : float
        Value used for search

    Returns
    -------
    clostest_val : float
        Clostest value in arr to val
    """

    #  Convert input to numpy array
    arr = np.asarray(arr)

    idx = (np.abs(arr - val)).argmin()
    return arr[idx]


def cor_ind_esys_size_with_dict_restr(ind, dict_restr):
    """
    Uses restrictions of dict_restr (defining possible energy system size)
    to find closest energy system size for pre-calculated energy system size
    on ind.
    Thus, modifing ind object

    Parameters
    ----------
    ind : object
        Individuum object of deap toolbox
    dict_restr : dict
        Dict holding possible energy system sizes (used to find closest
        energy system size with chosen size of pre-dimensioning)
    """

    #  List of possible energy systems within dict_restr
    list_pos_esys = ['chp', 'boi', 'tes', 'hp_aw', 'hp_ww', 'eh', 'bat']

    #  Loop over building ids
    for key in ind.keys():
        if key != 'lhn':  # No LHN --> Building id
            #  Loop over possible energy systems
            for esys in list_pos_esys:
                if ind[key][esys] > 0:  # Has energy system with spec. size
                    #  Try to identify closest size in dict_restr
                    #  Get pointer to list of sizes
                    list_sizes = dict_restr[esys]

                    #  Current size
                    cur_size = ind[key][esys]

                    #  Find closest value in list_sizes
                    new_size = find_nearest(arr=list_sizes, val=cur_size)

                    print('Perform esys size correction with dict_restr')
                    print('Type: ', esys)
                    print('Old size: ', cur_size)
                    print('New size: ', new_size)
                    print('Delta: ', str(new_size - cur_size))
                    print('Percent: ', str((new_size - cur_size) * 100
                                           / cur_size))
                    print()

                    #  Overwrite prior esys size
                    ind[key][esys] = new_size


def mod_ind(city, method, ind, toolbox, dict_restr, use_chp=True, use_lhn=True,
            use_hp_aw=True, use_hp_ww=True, use_pv=True, dict_sh=None,
            list_options=None,
            list_opt_prob=None,
            list_lhn_opt=None,
            list_lhn_prob=None,
            list_lhn_to_stand_alone=None,
            dict_max_pv_area=None,
            do_upscale=False,
            use_size_restr=True,
            dict_heatloads=None
            ):
    """
    Modifies individuum ind with city information

    Parameters
    ----------
    city : object
        City object of pyCity_calc
    method : str
        method for generation of esys
    ind : object
        Individuum object of deap toolbox
    toolbox : object
        DEAP toolbox
    dict_restr : dict
        Dict holding possible energy system sizes (used to find closest
        energy system size with chosen size of pre-dimensioning)
    use_chp : bool, optional
        Defines, if CHP systems should be used (default: True)
    use_lhn : bool, optional
        Defines, if local heating networks (LHN) should be used (default: True)
    use_hp_aw : bool, optional
        Defines, if air water heat pumps systems should be used (default: True)
    use_hp_ww : bool, optional
        Defines, if water water heat pumps systems should be used
        (default: True)
    use_pv : bool, optional
        Defines, if PV systems should be used (default: True)
    dict_sh : dict, optional
        Dictionary holding building node ids as keys and maximum space heating
        power values in Watt as dict values (default: None). If not None,
        used for size limitation. If None, dict_restr is used for sizing.
    list_options : list (of str), optional
        List holding strings with energy system options (default: None).
        If None, uses default values ['boi', 'boi_tes', 'chp_boi_tes',
        'chp_boi_eh_tes', 'hp_aw_eh', 'hp_ww_eh', 'hp_aw_boi', 'hp_ww_boi',
        'hp_aw_eh_boi', 'hp_ww_eh_boi', 'bat', 'pv']
    list_opt_prob : list (of floats), optional
        List holding probability factors for energy system options in
        list_options (default: None).
        If None, uses default values [0.1, 0.1, 0.2, 0.05, 0.1, 0.1, 0.05,
        0.05, 0.05, 0.05, 0.05, 0.1]
    list_lhn_opt : list (of str), optional
        List holding strings with LHN mutation options (default: None).
        If None, uses default values ['chp_boi_tes', 'chp_boi_eh_tes',
        'bat', 'pv', 'no_th_supply']
    list_lhn_prob : list (of floats), optional
        List holding probability factors for LHN mutation options in
        list_lhn_opt (default: None).
        If None, uses default values [0.1, 0.05, 0.05, 0.2, 0.6]
    list_lhn_to_stand_alone : list (of floats)
        List holding probability factors for energy system options in
        list_options (default: None).
        If None, uses default values [0.1, 0.15, 0.25, 0.05, 0.125, 0.125,
        0.05, 0.05, 0.05, 0.05, 0, 0]
    dict_max_pv_area : dict, optional
        Dict holding maximum usable PV area values in m2 per building
        (default: None). Cannot be None, if 'randomized' choice is taken!
    do_upscale : bool, optional
        Boolean to define, if peak load devices should have the change to
        be upscaled (only for choice 'randomized'), (default: False)
    use_size_restr : bool, optional
        Defines, if pre-calculate values should be strictly rounded to values
        given by dict_restr (default: True)
    dict_heatloads : dict, optional
        Dict holding building ids as keys and design heat loads in Watt
        as values (default: None)
    """
    list_choices = ['boi_only', 'boi_tes_only', 'chp_with_overall_LHN',
                    'chp_decentral', 'hp_aw_decentral', 'hp_ww_decentral',
                    'chp_hp_50', 'randomized', 'kmeans',
                    'chp_with_overall_LHN_small_PV',
                    'chp_with_overall_LHN_medium_PV',
                    'chp_with_overall_LHN_large_PV',
                    'chp_with_overall_LHN_max_PV',
                    'kmeans_large_pv',
                    'hp_aw_decentral_large_pv',
                    'hp_ww_decentral_large_pv',
                    'boi_tes_large_pv',
                    'chp_with_overall_LHN_small_PV_el_node',
                    'chp_with_overall_LHN_medium_PV_el_node',
                    'chp_with_overall_LHN_large_PV_el_node',
                    'chp_with_overall_LHN_max_PV_el_node',
                    'kmeans_large_pv_el_node',
                    'boi_tes_max_pv',
                    'boi_tes_medium_pv',
                    'kmeans_boi',
                    'kmeans_boi_large_pv',
                    'kmeans_boi_max_pv',
                    'chp_lhn_50_hp_aw_50_large_pv',
                    'chp_lhn_50_hp_ww_50_large_pv',
                    'multi_chps_one_lhn_large_pv',
                    'multi_chps_one_lhn',
                    'half_chps_one_lhn_large_pv'
                    ]

    assert method in list_choices

    print('Chosen method for individuum modification: ', method)
    print('####################################################')

    #  Copy city object
    city_copy = copy.deepcopy(city)

    #  List of building entity node ids
    list_build_ids = city.get_list_build_entity_node_ids()

    #  Get dict with building positions
    dict_pos = getpos.get_build_pos(city=city)

    #  Get id of building with highest space heating power demand
    id_sh_high = dimfunc.get_id_max_th_power(city=city_copy,
                                             with_dhw=False,
                                             current_values=False,
                                             find_max=True,
                                             return_value=False)

    #  Get dict with building el. energy demands
    dict_el = getel.get_dict_el_dem_city(city)

    #  Get id of building with max. el. energy demand
    (id_el_dem_max, el_dem_max) = getel.get_id_and_max_el_dem(dict_el_dem=
                                                              dict_el)

    if method == 'randomized':
        print('Randomize choice. Selected:')
        list_choices.remove('randomized')

        #  Eliminate specific choices, based on energy system boolean flags
        if use_chp is False or use_lhn is False:
            list_choices.remove('chp_with_overall_LHN')
            list_choices.remove('kmeans_boi')
            list_choices.remove('multi_chps_one_lhn')
        if use_chp is False or use_lhn is False or use_hp_ww is False:
            list_choices.remove('kmeans')
        if use_chp is False or use_lhn is False or use_pv is False:
            list_choices.remove('kmeans_boi_max_pv')
            list_choices.remove('kmeans_boi_large_pv')
            list_choices.remove('chp_with_overall_LHN_small_PV')
            list_choices.remove('chp_with_overall_LHN_medium_PV')
            list_choices.remove('chp_with_overall_LHN_large_PV')
            list_choices.remove('chp_with_overall_LHN_max_PV')
            list_choices.remove('chp_with_overall_LHN_small_PV_el_node')
            list_choices.remove('chp_with_overall_LHN_medium_PV_el_node')
            list_choices.remove('chp_with_overall_LHN_large_PV_el_node')
            list_choices.remove('chp_with_overall_LHN_max_PV_el_node')
            list_choices.remove('multi_chps_one_lhn_large_pv')
            list_choices.remove('half_chps_one_lhn_large_pv')
        if (use_chp is False or use_lhn is False or use_pv is False or
                use_hp_aw is False):
            list_choices.remove('chp_lhn_50_hp_aw_50_large_pv')
        if (use_chp is False or use_lhn is False or use_pv is False or
                use_hp_ww is False):
            list_choices.remove('kmeans_large_pv')
            list_choices.remove('kmeans_large_pv_el_node')
            list_choices.remove('chp_lhn_50_hp_ww_50_large_pv')
        if use_chp is False:
            list_choices.remove('chp_decentral')
        if use_hp_aw is False:
            list_choices.remove('hp_aw_decentral')
        if use_hp_aw is False or use_pv is False:
            list_choices.remove('hp_aw_decentral_large_pv')
        if use_hp_ww is False:
            list_choices.remove('hp_ww_decentral')
        if use_hp_ww is False or use_pv is False:
            list_choices.remove('hp_ww_decentral_large_pv')
        if use_hp_aw is False or use_hp_ww is False or use_chp is False:
            list_choices.remove('chp_hp_50')
        if use_pv is False:
            list_choices.remove('boi_tes_max_pv')
            list_choices.remove('boi_tes_medium_pv')

        #  Select random method
        method = np.random.choice(list_choices, size=1)

    print('Call mod_ind() with method ' + str(method))
    print('##########################################')

    #  Add boilers, only
    if method == 'boi_only':

        #  Dummy energy system data list
        list_data = []

        # Add boilers, only, to city
        for n in list_build_ids:
            tup_esys = (n, 0, 1)  # Boiler (full part load)

            #  Add fitting esys system
            list_data.append(tup_esys)

        esysgen.gen_esys_for_city(city=city_copy, list_data=list_data,
                                  dhw_scale=True, tes_default=300)

    # Add boilers with TES, only
    elif method == 'boi_tes_only':

        #  Dummy energy system data list
        list_data = []

        # Add boilers, only, to city
        for n in list_build_ids:
            tup_esys = (n, 0, 2)  # Boiler with tes

            #  Add fitting esys system
            list_data.append(tup_esys)

        esysgen.gen_esys_for_city(city=city_copy, list_data=list_data,
                                  dhw_scale=True, tes_default=300)

    # Add CHP with overall LHN
    elif method == 'chp_with_overall_LHN':

        dict_data_entry = {'type': 'heating', 'method': 1,
                           'nodelist': copy.copy(list_build_ids)}

        dict_data = {1: dict_data_entry}

        #  Add LHN network to all buildings
        enetgen.add_energy_networks_to_city(city=city_copy,
                                            dict_data=dict_data)

        #  Dummy energy system data list
        list_data = []

        tup_esys = (id_sh_high, 1, 4)

        #  Add fitting esys system
        list_data.append(tup_esys)

        esysgen.gen_esys_for_city(city=city_copy, list_data=list_data,
                                  dhw_scale=True, tes_default=2000)

    # Add CHP with overall LHN and PV
    elif method == 'chp_with_overall_LHN_small_PV':

        dict_data_entry = {'type': 'heating', 'method': 1,
                           'nodelist': copy.copy(list_build_ids)}

        dict_data = {1: dict_data_entry}

        #  Add LHN network to all buildings
        enetgen.add_energy_networks_to_city(city=city_copy,
                                            dict_data=dict_data)

        #  Dummy energy system data list
        list_data = []

        tup_esys = (id_sh_high, 1, 4)
        #  Add fitting esys system
        list_data.append(tup_esys)

        #  Add PV
        for n in list_build_ids:
            pv_max = city.nodes[n]['entity'].roof_usabl_pv_area
            pv_area = round(pv_max * 1 / 4, 0)
            tup_esys = (n, 3, pv_area)
            list_data.append(tup_esys)

        esysgen.gen_esys_for_city(city=city_copy, list_data=list_data,
                                  dhw_scale=True, tes_default=2000)

    # Add CHP with overall LHN and PV
    elif method == 'chp_with_overall_LHN_medium_PV':

        dict_data_entry = {'type': 'heating', 'method': 1,
                           'nodelist': copy.copy(list_build_ids)}

        dict_data = {1: dict_data_entry}

        #  Add LHN network to all buildings
        enetgen.add_energy_networks_to_city(city=city_copy,
                                            dict_data=dict_data)

        #  Dummy energy system data list
        list_data = []

        tup_esys = (id_sh_high, 1, 4)
        #  Add fitting esys system
        list_data.append(tup_esys)

        #  Add PV
        for n in list_build_ids:
            pv_max = city.nodes[n]['entity'].roof_usabl_pv_area
            pv_area = round(pv_max * 1 / 2, 0)
            tup_esys = (n, 3, pv_area)
            list_data.append(tup_esys)

        esysgen.gen_esys_for_city(city=city_copy, list_data=list_data,
                                  dhw_scale=True, tes_default=2000)

    # Add CHP with overall LHN and PV
    elif method == 'chp_with_overall_LHN_large_PV':

        dict_data_entry = {'type': 'heating', 'method': 1,
                           'nodelist': copy.copy(list_build_ids)}

        dict_data = {1: dict_data_entry}

        #  Add LHN network to all buildings
        enetgen.add_energy_networks_to_city(city=city_copy,
                                            dict_data=dict_data)

        #  Dummy energy system data list
        list_data = []

        tup_esys = (id_sh_high, 1, 4)
        #  Add fitting esys system
        list_data.append(tup_esys)

        #  Add PV
        for n in list_build_ids:
            pv_max = city.nodes[n]['entity'].roof_usabl_pv_area
            pv_area = round(pv_max * 3 / 4, 0)
            tup_esys = (n, 3, pv_area)
            list_data.append(tup_esys)

        esysgen.gen_esys_for_city(city=city_copy, list_data=list_data,
                                  dhw_scale=True, tes_default=2000)

    # Add CHP with overall LHN and PV
    elif method == 'chp_with_overall_LHN_max_PV':

        dict_data_entry = {'type': 'heating', 'method': 1,
                           'nodelist': copy.copy(list_build_ids)}

        dict_data = {1: dict_data_entry}

        #  Add LHN network to all buildings
        enetgen.add_energy_networks_to_city(city=city_copy,
                                            dict_data=dict_data)

        #  Dummy energy system data list
        list_data = []

        tup_esys = (id_sh_high, 1, 4)
        #  Add fitting esys system
        list_data.append(tup_esys)

        #  Add PV
        for n in list_build_ids:
            pv_max = city.nodes[n]['entity'].roof_usabl_pv_area
            pv_area = math.ceil(pv_max)
            tup_esys = (n, 3, pv_area)
            list_data.append(tup_esys)

        esysgen.gen_esys_for_city(city=city_copy, list_data=list_data,
                                  dhw_scale=True, tes_default=2000)

    # Add decentralized CHPs, only (CHP into largest building)
    elif method == 'chp_decentral':

        #  Dummy energy system data list
        list_data = []

        # Add chps
        for n in list_build_ids:
            tup_esys = (n, 1, 4)

            #  Add fitting esys system
            list_data.append(tup_esys)

        esysgen.gen_esys_for_city(city=city_copy, list_data=list_data,
                                  dhw_scale=True, tes_default_chp=300)

    # Add decentralized aw HPs, only
    elif method == 'hp_aw_decentral':

        #  Dummy energy system data list
        list_data = []

        # Add boilers, only, to city
        for n in list_build_ids:
            tup_esys = (n, 2, 1)  # Boiler with tes

            #  Add fitting esys system
            list_data.append(tup_esys)

        esysgen.gen_esys_for_city(city=city_copy, list_data=list_data,
                                  dhw_scale=True, tes_default=300)

    # Add decentralized ww HPs, only
    elif method == 'hp_ww_decentral':

        #  Dummy energy system data list
        list_data = []

        # Add boilers, only, to city
        for n in list_build_ids:
            tup_esys = (n, 2, 2)

            #  Add fitting esys system
            list_data.append(tup_esys)

        esysgen.gen_esys_for_city(city=city_copy, list_data=list_data,
                                  dhw_scale=True, tes_default=300)

    # Add share of CHPs and HPs (around 50 %)
    elif method == 'chp_hp_50':

        #  Dummy energy system data list
        list_data = []

        #  Add CHPs
        for n in list_build_ids:

            if rd.random() <= 0.5:
                tup_esys = (n, 1, 4)  # Add CHP
            else:
                tup_esys = (n, 2, 1)  # Add HP

            # Add fitting esys system
            list_data.append(tup_esys)

        esysgen.gen_esys_for_city(city=city_copy, list_data=list_data,
                                  dhw_scale=True, tes_default_chp=300)

    #  Add subnetworks to city (with CHPs). Single buildings get HPs
    elif method == 'kmeans':

        ref_nb = int(len(list_build_ids) / 3)

        if ref_nb > 1:
            nb_clust = rd.randint(1, ref_nb)
        else:
            nb_clust = 1

        dict_clusters = clust.kmeans_clustering(dict_pos=dict_pos,
                                                list_av_ids=list_build_ids,
                                                nb_clusters=nb_clust)

        for key in dict_clusters.keys():

            #  Generate LHN with CHP system
            list_lhn_nodes = dict_clusters[key]

            if len(list_lhn_nodes) > 1:

                dict_data_entry = {'type': 'heating', 'method': 1,
                                   'nodelist': copy.copy(list_lhn_nodes)}

                dict_data = {1: dict_data_entry}

                #  Add LHN network to all buildings
                enetgen.add_energy_networks_to_city(city=city_copy,
                                                    dict_data=dict_data)

                #  Dummy energy system data list
                list_data = []

                #  If building with max. space heat demand is in list, use it
                if id_sh_high in list_lhn_nodes:
                    id_chp = id_sh_high
                #  If building with max. el. demand is in list, use it
                elif id_el_dem_max in list_lhn_nodes:
                    id_chp = id_el_dem_max
                else:
                    #  Random feeder node choice
                    id_chp = np.random.choice(list_lhn_nodes)

                tup_esys = (id_chp, 1, 4)

                #  Add fitting esys system
                list_data.append(tup_esys)

                esysgen.gen_esys_for_city(city=city_copy, list_data=list_data,
                                          dhw_scale=True, tes_default=2000)
            elif len(list_lhn_nodes) == 1:
                #  Generate HP
                list_data = []

                for n in list_lhn_nodes:
                    tup_esys = (n, 2, 2)

                    #  Add fitting esys system
                    list_data.append(tup_esys)

                esysgen.gen_esys_for_city(city=city_copy, list_data=list_data,
                                          dhw_scale=True, tes_default=300)

    #  Add subnetworks to city (with CHPs). Single buildings get HPs
    elif method == 'kmeans_large_pv':

        ref_nb = int(len(list_build_ids) / 3)

        if ref_nb > 1:
            nb_clust = rd.randint(1, ref_nb)
        else:
            nb_clust = 1

        dict_clusters = clust.kmeans_clustering(dict_pos=dict_pos,
                                                list_av_ids=list_build_ids,
                                                nb_clusters=nb_clust)

        for key in dict_clusters.keys():

            #  Generate LHN with CHP system
            list_lhn_nodes = dict_clusters[key]

            if len(list_lhn_nodes) > 1:

                dict_data_entry = {'type': 'heating', 'method': 1,
                                   'nodelist': copy.copy(
                                       list_lhn_nodes)}

                dict_data = {1: dict_data_entry}

                #  Add LHN network to all buildings
                enetgen.add_energy_networks_to_city(city=city_copy,
                                                    dict_data=dict_data)

                #  Dummy energy system data list
                list_data = []

                #  If building with max. space heat demand is in list, use it
                if id_sh_high in list_lhn_nodes:
                    id_chp = id_sh_high
                #  If building with max. el. demand is in list, use it
                elif id_el_dem_max in list_lhn_nodes:
                    id_chp = id_el_dem_max
                else:
                    #  Random feeder node choice
                    id_chp = np.random.choice(list_lhn_nodes)

                tup_esys = (id_chp, 1, 4)

                #  Add fitting esys system
                list_data.append(tup_esys)

                #  Add PV
                for n in list_lhn_nodes:
                    pv_max = city.nodes[n]['entity'].roof_usabl_pv_area
                    pv_area = round(pv_max * 3 / 4, 0)
                    tup_esys = (n, 3, pv_area)
                    list_data.append(tup_esys)

                esysgen.gen_esys_for_city(city=city_copy,
                                          list_data=list_data,
                                          dhw_scale=True,
                                          tes_default=2000)

            elif len(list_lhn_nodes) == 1:
                #  Generate HP
                list_data = []

                for n in list_lhn_nodes:
                    tup_esys = (n, 2, 2)

                    #  Add fitting esys system
                    list_data.append(tup_esys)

                    pv_max = city.nodes[n]['entity'].roof_usabl_pv_area
                    pv_area = round(pv_max * 3 / 4, 0)
                    tup_esys = (n, 3, pv_area)
                    list_data.append(tup_esys)

                esysgen.gen_esys_for_city(city=city_copy,
                                          list_data=list_data,
                                          dhw_scale=True,
                                          tes_default=300)

    # Add decentralized aw HPs, only
    elif method == 'hp_aw_decentral_large_pv':

        #  Dummy energy system data list
        list_data = []

        # Add boilers, only, to city
        for n in list_build_ids:
            tup_esys = (n, 2, 1)
            #  Add fitting esys system
            list_data.append(tup_esys)

            pv_max = city.nodes[n]['entity'].roof_usabl_pv_area
            pv_area = round(pv_max * 3 / 4, 0)
            tup_esys = (n, 3, pv_area)
            list_data.append(tup_esys)

        esysgen.gen_esys_for_city(city=city_copy, list_data=list_data,
                                  dhw_scale=True, tes_default=300)

    # Add decentralized ww HPs, only
    elif method == 'hp_ww_decentral_large_pv':

        #  Dummy energy system data list
        list_data = []

        # Add boilers, only, to city
        for n in list_build_ids:
            tup_esys = (n, 2, 2)
            #  Add fitting esys system
            list_data.append(tup_esys)

            pv_max = city.nodes[n]['entity'].roof_usabl_pv_area
            pv_area = round(pv_max * 3 / 4, 0)
            tup_esys = (n, 3, pv_area)
            list_data.append(tup_esys)

        esysgen.gen_esys_for_city(city=city_copy, list_data=list_data,
                                  dhw_scale=True, tes_default=300)

    #  BOI, TES and PV
    elif method == 'boi_tes_large_pv':

        #  Dummy energy system data list
        list_data = []

        # Add boilers, only, to city
        for n in list_build_ids:
            tup_esys = (n, 0, 2)  # Boiler with tes

            #  Add fitting esys system
            list_data.append(tup_esys)

            pv_max = city.nodes[n]['entity'].roof_usabl_pv_area
            pv_area = round(pv_max * 3 / 4, 0)
            tup_esys = (n, 3, pv_area)
            list_data.append(tup_esys)

        esysgen.gen_esys_for_city(city=city_copy, list_data=list_data,
                                  dhw_scale=True, tes_default=300)

    # Add CHP with overall LHN and PV
    elif method == 'chp_with_overall_LHN_small_PV_el_node':

        dict_data_entry = {'type': 'heating', 'method': 1,
                           'nodelist': copy.copy(list_build_ids)}

        dict_data = {1: dict_data_entry}

        #  Add LHN network to all buildings
        enetgen.add_energy_networks_to_city(city=city_copy,
                                            dict_data=dict_data)

        #  Dummy energy system data list
        list_data = []

        tup_esys = (id_el_dem_max, 1, 4)
        #  Add fitting esys system
        list_data.append(tup_esys)

        #  Add PV
        for n in list_build_ids:
            pv_max = city.nodes[n]['entity'].roof_usabl_pv_area
            pv_area = round(pv_max * 1 / 4, 0)
            tup_esys = (n, 3, pv_area)
            list_data.append(tup_esys)

        esysgen.gen_esys_for_city(city=city_copy, list_data=list_data,
                                  dhw_scale=True, tes_default=2000)

    # Add CHP with overall LHN and PV
    elif method == 'chp_with_overall_LHN_medium_PV_el_node':

        dict_data_entry = {'type': 'heating', 'method': 1,
                           'nodelist': copy.copy(list_build_ids)}

        dict_data = {1: dict_data_entry}

        #  Add LHN network to all buildings
        enetgen.add_energy_networks_to_city(city=city_copy,
                                            dict_data=dict_data)

        #  Dummy energy system data list
        list_data = []

        tup_esys = (id_el_dem_max, 1, 4)
        #  Add fitting esys system
        list_data.append(tup_esys)

        #  Add PV
        for n in list_build_ids:
            pv_max = city.nodes[n]['entity'].roof_usabl_pv_area
            pv_area = round(pv_max * 1 / 2, 0)
            tup_esys = (n, 3, pv_area)
            list_data.append(tup_esys)

        esysgen.gen_esys_for_city(city=city_copy, list_data=list_data,
                                  dhw_scale=True, tes_default=2000)

    # Add CHP with overall LHN and PV
    elif method == 'chp_with_overall_LHN_large_PV_el_node':

        dict_data_entry = {'type': 'heating', 'method': 1,
                           'nodelist': copy.copy(list_build_ids)}

        dict_data = {1: dict_data_entry}

        #  Add LHN network to all buildings
        enetgen.add_energy_networks_to_city(city=city_copy,
                                            dict_data=dict_data)

        #  Dummy energy system data list
        list_data = []

        tup_esys = (id_el_dem_max, 1, 4)
        #  Add fitting esys system
        list_data.append(tup_esys)

        #  Add PV
        for n in list_build_ids:
            pv_max = city.nodes[n]['entity'].roof_usabl_pv_area
            pv_area = round(pv_max * 3 / 4, 0)
            tup_esys = (n, 3, pv_area)
            list_data.append(tup_esys)

        esysgen.gen_esys_for_city(city=city_copy, list_data=list_data,
                                  dhw_scale=True, tes_default=2000)

    # Add CHP with overall LHN and PV
    elif method == 'chp_with_overall_LHN_max_PV_el_node':

        dict_data_entry = {'type': 'heating', 'method': 1,
                           'nodelist': copy.copy(list_build_ids)}

        dict_data = {1: dict_data_entry}

        #  Add LHN network to all buildings
        enetgen.add_energy_networks_to_city(city=city_copy,
                                            dict_data=dict_data)

        #  Dummy energy system data list
        list_data = []

        tup_esys = (id_el_dem_max, 1, 4)
        #  Add fitting esys system
        list_data.append(tup_esys)

        #  Add PV
        for n in list_build_ids:
            pv_max = city.nodes[n]['entity'].roof_usabl_pv_area
            pv_area = math.ceil(pv_max)
            tup_esys = (n, 3, pv_area)
            list_data.append(tup_esys)

        esysgen.gen_esys_for_city(city=city_copy, list_data=list_data,
                                  dhw_scale=True, tes_default=2000)

    #  Add subnetworks to city (with CHPs). Single buildings get HPs
    elif method == 'kmeans_large_pv_el_node':

        ref_nb = int(len(list_build_ids) / 3)

        if ref_nb > 1:
            nb_clust = rd.randint(1, ref_nb)
        else:
            nb_clust = 1

        dict_clusters = clust.kmeans_clustering(dict_pos=dict_pos,
                                                list_av_ids=list_build_ids,
                                                nb_clusters=nb_clust)

        for key in dict_clusters.keys():

            #  Generate LHN with CHP system
            list_lhn_nodes = dict_clusters[key]

            if len(list_lhn_nodes) > 1:

                dict_data_entry = {'type': 'heating', 'method': 1,
                                   'nodelist': copy.copy(
                                       list_lhn_nodes)}

                dict_data = {1: dict_data_entry}

                #  Add LHN network to all buildings
                enetgen.add_energy_networks_to_city(city=city_copy,
                                                    dict_data=dict_data)

                #  Dummy energy system data list
                list_data = []

                #  If building with max. space heat demand is in list, use it
                if id_sh_high in list_lhn_nodes:
                    id_chp = id_sh_high
                #  If building with max. el. demand is in list, use it
                elif id_el_dem_max in list_lhn_nodes:
                    id_chp = id_el_dem_max
                else:
                    #  Random feeder node choice
                    id_chp = np.random.choice(list_lhn_nodes)

                tup_esys = (id_chp, 1, 4)

                #  Add fitting esys system
                list_data.append(tup_esys)

                #  Add PV
                for n in list_lhn_nodes:
                    pv_max = city.nodes[n]['entity'].roof_usabl_pv_area
                    pv_area = round(pv_max * 3 / 4, 0)
                    tup_esys = (n, 3, pv_area)
                    list_data.append(tup_esys)

                esysgen.gen_esys_for_city(city=city_copy,
                                          list_data=list_data,
                                          dhw_scale=True,
                                          tes_default=2000)

            elif len(list_lhn_nodes) == 1:
                #  Generate HP
                list_data = []

                for n in list_lhn_nodes:
                    tup_esys = (n, 2, 2)

                    #  Add fitting esys system
                    list_data.append(tup_esys)

                    pv_max = city.nodes[n]['entity'].roof_usabl_pv_area
                    pv_area = round(pv_max * 3 / 4, 0)
                    tup_esys = (n, 3, pv_area)
                    list_data.append(tup_esys)

                esysgen.gen_esys_for_city(city=city_copy,
                                          list_data=list_data,
                                          dhw_scale=True,
                                          tes_default=300)

    #  BOI, TES and PV
    elif method == 'boi_tes_max_pv':

        #  Dummy energy system data list
        list_data = []

        # Add boilers, only, to city
        for n in list_build_ids:
            tup_esys = (n, 0, 2)  # Boiler with tes

            #  Add fitting esys system
            list_data.append(tup_esys)

            pv_max = city.nodes[n]['entity'].roof_usabl_pv_area
            pv_area = math.ceil(pv_max)
            tup_esys = (n, 3, pv_area)
            list_data.append(tup_esys)

        esysgen.gen_esys_for_city(city=city_copy, list_data=list_data,
                                  dhw_scale=True, tes_default=300)

    #  BOI, TES and PV
    elif method == 'boi_tes_medium_pv':

        #  Dummy energy system data list
        list_data = []

        # Add boilers, only, to city
        for n in list_build_ids:
            tup_esys = (n, 0, 2)  # Boiler with tes

            #  Add fitting esys system
            list_data.append(tup_esys)

            pv_max = city.nodes[n]['entity'].roof_usabl_pv_area
            pv_area = round(pv_max * 1 / 2, 0)
            tup_esys = (n, 3, pv_area)
            list_data.append(tup_esys)

        esysgen.gen_esys_for_city(city=city_copy, list_data=list_data,
                                  dhw_scale=True, tes_default=300)

    #  Add subnetworks to city (with CHPs). Single buildings get boiler
    elif method == 'kmeans_boi':

        ref_nb = int(len(list_build_ids) / 3)

        if ref_nb > 1:
            nb_clust = rd.randint(1, ref_nb)
        else:
            nb_clust = 1

        dict_clusters = clust.kmeans_clustering(dict_pos=dict_pos,
                                                list_av_ids=list_build_ids,
                                                nb_clusters=nb_clust)

        for key in dict_clusters.keys():

            #  Generate LHN with CHP system
            list_lhn_nodes = dict_clusters[key]

            if len(list_lhn_nodes) > 1:

                dict_data_entry = {'type': 'heating', 'method': 1,
                                   'nodelist': copy.copy(list_lhn_nodes)}

                dict_data = {1: dict_data_entry}

                #  Add LHN network to all buildings
                enetgen.add_energy_networks_to_city(city=city_copy,
                                                    dict_data=dict_data)

                #  Dummy energy system data list
                list_data = []

                #  If building with max. space heat demand is in list, use it
                if id_sh_high in list_lhn_nodes:
                    id_chp = id_sh_high
                #  If building with max. el. demand is in list, use it
                elif id_el_dem_max in list_lhn_nodes:
                    id_chp = id_el_dem_max
                else:
                    #  Random feeder node choice
                    id_chp = np.random.choice(list_lhn_nodes)

                tup_esys = (id_chp, 1, 4)

                #  Add fitting esys system
                list_data.append(tup_esys)

                esysgen.gen_esys_for_city(city=city_copy, list_data=list_data,
                                          dhw_scale=True, tes_default=2000)
            elif len(list_lhn_nodes) == 1:
                #  Generate boilers
                list_data = []

                for n in list_lhn_nodes:
                    tup_esys = (n, 0, 2)

                    #  Add fitting esys system
                    list_data.append(tup_esys)

                esysgen.gen_esys_for_city(city=city_copy, list_data=list_data,
                                          dhw_scale=True, tes_default=300)

    #  Add subnetworks to city (with CHPs). Single buildings get boiler
    elif method == 'kmeans_boi_large_pv':

        ref_nb = int(len(list_build_ids) / 3)

        if ref_nb > 1:
            nb_clust = rd.randint(1, ref_nb)
        else:
            nb_clust = 1

        dict_clusters = clust.kmeans_clustering(dict_pos=dict_pos,
                                                list_av_ids=list_build_ids,
                                                nb_clusters=nb_clust)

        for key in dict_clusters.keys():

            #  Generate LHN with CHP system
            list_lhn_nodes = dict_clusters[key]

            if len(list_lhn_nodes) > 1:

                dict_data_entry = {'type': 'heating', 'method': 1,
                                   'nodelist': copy.copy(list_lhn_nodes)}

                dict_data = {1: dict_data_entry}

                #  Add LHN network to all buildings
                enetgen.add_energy_networks_to_city(city=city_copy,
                                                    dict_data=dict_data)

                #  Dummy energy system data list
                list_data = []

                #  If building with max. space heat demand is in list, use it
                if id_sh_high in list_lhn_nodes:
                    id_chp = id_sh_high
                #  If building with max. el. demand is in list, use it
                elif id_el_dem_max in list_lhn_nodes:
                    id_chp = id_el_dem_max
                else:
                    #  Random feeder node choice
                    id_chp = np.random.choice(list_lhn_nodes)

                tup_esys = (id_chp, 1, 4)

                #  Add fitting esys system
                list_data.append(tup_esys)

                #  Add PV
                for n in list_lhn_nodes:
                    pv_max = city.nodes[n]['entity'].roof_usabl_pv_area
                    pv_area = round(pv_max * 3 / 4, 0)
                    tup_esys = (n, 3, pv_area)
                    list_data.append(tup_esys)

                esysgen.gen_esys_for_city(city=city_copy, list_data=list_data,
                                          dhw_scale=True, tes_default=2000)
            elif len(list_lhn_nodes) == 1:
                #  Generate boilers
                list_data = []

                for n in list_lhn_nodes:
                    tup_esys = (n, 0, 2)

                    #  Add fitting esys system
                    list_data.append(tup_esys)

                    pv_max = city.nodes[n]['entity'].roof_usabl_pv_area
                    pv_area = round(pv_max * 3 / 4, 0)
                    tup_esys = (n, 3, pv_area)
                    list_data.append(tup_esys)

                esysgen.gen_esys_for_city(city=city_copy, list_data=list_data,
                                          dhw_scale=True, tes_default=300)

    #  Add subnetworks to city (with CHPs). Single buildings get boiler
    elif method == 'kmeans_boi_max_pv':

        ref_nb = int(len(list_build_ids) / 3)

        if ref_nb > 1:
            nb_clust = rd.randint(1, ref_nb)
        else:
            nb_clust = 1

        dict_clusters = clust.kmeans_clustering(dict_pos=dict_pos,
                                                list_av_ids=list_build_ids,
                                                nb_clusters=nb_clust)

        for key in dict_clusters.keys():

            #  Generate LHN with CHP system
            list_lhn_nodes = dict_clusters[key]

            if len(list_lhn_nodes) > 1:

                dict_data_entry = {'type': 'heating', 'method': 1,
                                   'nodelist': copy.copy(list_lhn_nodes)}

                dict_data = {1: dict_data_entry}

                #  Add LHN network to all buildings
                enetgen.add_energy_networks_to_city(city=city_copy,
                                                    dict_data=dict_data)

                #  Dummy energy system data list
                list_data = []

                #  If building with max. space heat demand is in list, use it
                if id_sh_high in list_lhn_nodes:
                    id_chp = id_sh_high
                #  If building with max. el. demand is in list, use it
                elif id_el_dem_max in list_lhn_nodes:
                    id_chp = id_el_dem_max
                else:
                    #  Random feeder node choice
                    id_chp = np.random.choice(list_lhn_nodes)

                tup_esys = (id_chp, 1, 4)

                #  Add fitting esys system
                list_data.append(tup_esys)

                #  Add PV
                for n in list_lhn_nodes:
                    pv_max = city.nodes[n]['entity'].roof_usabl_pv_area
                    pv_area = math.ceil(pv_max)
                    tup_esys = (n, 3, pv_area)
                    list_data.append(tup_esys)

                esysgen.gen_esys_for_city(city=city_copy, list_data=list_data,
                                          dhw_scale=True, tes_default=2000)
            elif len(list_lhn_nodes) == 1:
                #  Generate boilers
                list_data = []

                for n in list_lhn_nodes:
                    tup_esys = (n, 0, 2)

                    #  Add fitting esys system
                    list_data.append(tup_esys)

                    pv_max = city.nodes[n]['entity'].roof_usabl_pv_area
                    pv_area = math.ceil(pv_max)
                    tup_esys = (n, 3, pv_area)
                    list_data.append(tup_esys)

                esysgen.gen_esys_for_city(city=city_copy, list_data=list_data,
                                          dhw_scale=True, tes_default=300)

    # Add CHP/LHN and decentralized hp aw with PV
    elif method == 'chp_lhn_50_hp_aw_50_large_pv':

        #  Select random search node for LHN
        start_id = rd.choice(list_build_ids)

        #  Get list of ids, sorted by distance to start_id
        list_ids_dist = analyse.get_ids_sorted_by_dist(id=start_id,
                                                       dict_pos=dict_pos)

        #  Generate LHN list
        list_lhn = list_ids_dist[0:int(len(list_build_ids) / 2)]
        list_lhn.append(start_id)

        dict_data_entry = {'type': 'heating', 'method': 1,
                           'nodelist': copy.copy(list_lhn)}

        dict_data = {1: dict_data_entry}

        #  Add LHN network to all buildings
        enetgen.add_energy_networks_to_city(city=city_copy,
                                            dict_data=dict_data)

        #  Dummy energy system data list
        list_data = []

        tup_esys = (start_id, 1, 4)
        #  Add fitting esys system
        list_data.append(tup_esys)

        #  Add HPs to remaining buildnigs
        for n in list_build_ids:
            if n not in list_lhn:
                tup_esys = (n, 2, 1)
                list_data.append(tup_esys)

        #  Add PV
        for n in list_build_ids:
            pv_max = city.nodes[n]['entity'].roof_usabl_pv_area
            pv_area = round(pv_max * 3 / 4, 0)
            tup_esys = (n, 3, pv_area)
            list_data.append(tup_esys)

        esysgen.gen_esys_for_city(city=city_copy, list_data=list_data,
                                  dhw_scale=True, tes_default=500)

    # Add CHP/LHN and decentralized hp ww with PV
    elif method == 'chp_lhn_50_hp_ww_50_large_pv':

        #  Select random search node for LHN
        start_id = rd.choice(list_build_ids)

        #  Get list of ids, sorted by distance to start_id
        list_ids_dist = analyse.get_ids_sorted_by_dist(id=start_id,
                                                       dict_pos=dict_pos)

        #  Generate LHN list
        list_lhn = list_ids_dist[0:int(len(list_build_ids) / 2)]
        list_lhn.append(start_id)

        dict_data_entry = {'type': 'heating', 'method': 1,
                           'nodelist': copy.copy(list_lhn)}

        dict_data = {1: dict_data_entry}

        #  Add LHN network to all buildings
        enetgen.add_energy_networks_to_city(city=city_copy,
                                            dict_data=dict_data)

        #  Dummy energy system data list
        list_data = []

        tup_esys = (start_id, 1, 4)
        #  Add fitting esys system
        list_data.append(tup_esys)

        #  Add HPs to remaining buildnigs
        for n in list_build_ids:
            if n not in list_lhn:
                tup_esys = (n, 2, 2)
                list_data.append(tup_esys)

        #  Add PV
        for n in list_build_ids:
            pv_max = city.nodes[n]['entity'].roof_usabl_pv_area
            pv_area = round(pv_max * 3 / 4, 0)
            tup_esys = (n, 3, pv_area)
            list_data.append(tup_esys)

        esysgen.gen_esys_for_city(city=city_copy, list_data=list_data,
                                  dhw_scale=True, tes_default=500)

    # Add multi CHPs with overall LHN and PV
    elif method == 'multi_chps_one_lhn_large_pv':

        #  Dummy energy system data list
        list_data = []

        #  Add PV and CHP
        for n in list_build_ids:
            tup_esys = (n, 1, 4)  # CHP
            #  Add fitting esys system
            list_data.append(tup_esys)
            pv_max = city.nodes[n]['entity'].roof_usabl_pv_area
            pv_area = round(pv_max * 3 / 4, 0)
            tup_esys = (n, 3, pv_area)
            list_data.append(tup_esys)

        esysgen.gen_esys_for_city(city=city_copy, list_data=list_data,
                                  dhw_scale=True, tes_default=1000)

        dict_data_entry = {'type': 'heating', 'method': 1,
                           'nodelist': copy.copy(list_build_ids)}

        dict_data = {1: dict_data_entry}

        #  Add LHN network to all buildings
        enetgen.add_energy_networks_to_city(city=city_copy,
                                            dict_data=dict_data)

    # Add multi CHPs with overall LHN
    elif method == 'multi_chps_one_lhn':

        #  Dummy energy system data list
        list_data = []

        #  Add CHP
        for n in list_build_ids:
            tup_esys = (n, 1, 4)  # CHP
            list_data.append(tup_esys)

        esysgen.gen_esys_for_city(city=city_copy, list_data=list_data,
                                  dhw_scale=True, tes_default=1000)

        dict_data_entry = {'type': 'heating', 'method': 1,
                           'nodelist': copy.copy(list_build_ids)}

        dict_data = {1: dict_data_entry}

        #  Add LHN network to all buildings
        enetgen.add_energy_networks_to_city(city=city_copy,
                                            dict_data=dict_data)

    # Add 50% CHPs with overall LHN and PV (CHP to buildings with largest
    #  annual el. demand)
    elif method == 'half_chps_one_lhn_large_pv':

        #  Dummy energy system data list
        list_data = []

        list_dem_ids = dimfunc. \
            sort_build_ids_by_annual_en_dem(city=city_copy,
                                            dem='el',
                                            start_highest=True)

        list_chps = list_dem_ids[0:int(len(list_dem_ids) / 2)]

        for n in list_chps:
            tup_esys = (n, 1, 4)  # CHP
            #  Add fitting esys system
            list_data.append(tup_esys)

        #  Add PV
        for n in list_build_ids:
            pv_max = city.nodes[n]['entity'].roof_usabl_pv_area
            pv_area = round(pv_max * 3 / 4, 0)
            tup_esys = (n, 3, pv_area)
            list_data.append(tup_esys)

        esysgen.gen_esys_for_city(city=city_copy, list_data=list_data,
                                  dhw_scale=True, tes_default=1000)

        dict_data_entry = {'type': 'heating', 'method': 1,
                           'nodelist': copy.copy(list_build_ids)}

        dict_data = {1: dict_data_entry}

        #  Add LHN network to all buildings
        enetgen.add_energy_networks_to_city(city=city_copy,
                                            dict_data=dict_data)

    #  ######################################################################

    # Parse city to ind dict
    dict_ind = toolbox.parse_city_to_ind(dict_ind=None, city=city_copy,
                                         list_build_ids=list_build_ids)

    if use_size_restr:
        #  Correct energy system size value with dict_restr
        cor_ind_esys_size_with_dict_restr(ind=dict_ind, dict_restr=dict_restr)

    #  ######################################################################

    if method == 'randomized':

        #  Mutate energy system size

        #  Loop over buildings
        for n in list_build_ids:
            #  80 % change that size of building is changes
            if rd.random() <= 0.8:
                mutesys. \
                    mut_esys_val_single_build(ind=dict_ind, n=n,
                                              prob_mut=0.8,
                                              dict_restr=dict_restr,
                                              pv_min=pv_min,
                                              dict_max_pv_area=dict_max_pv_area,
                                              dict_sh=dict_sh,
                                              pv_step=1,
                                              dict_heatloads=dict_heatloads)

        if do_upscale:
            #  If monte-carlo simulation is active, has the chance to upscale
            #  Peak load device power
            if rd.random() <= 0.5:
                #  Loop over buildings
                for n in list_build_ids:
                    for key in dict_ind[n].keys():
                        if key in ['boi', 'hp_aw', 'hp_ww', 'eh']:
                            if dict_ind[n][key] > 0:
                                #  Rescale given energy system size with
                                #  random factor equal to or larger than 1
                                dict_ind[n][key] *= (1 + 2 * rd.random())

    parsedictind.parse_dict_info_to_ind(dict_ind=dict_ind, ind=ind)

    print('New individuum:')
    print(ind)
    print()


def gen_diverse_pop(city, nb_ind, nb_runs, failure_tolerance, sampling_method,
                    dict_restr,
                    use_chp=True, use_lhn=True, use_hp_aw=True,
                    use_hp_ww=True, use_pv=True,
                    objective='ann_and_co2_ref_test',
                    eeg_pv_limit=False, pv_min=None, pv_step=1, add_pv_prop=0,
                    use_street=False, do_upscale=False,
                    use_kwkg_lhn_sub=False, use_size_restr=True,
                    dem_unc=True, prevent_boi_lhn=True):
    """
    Generates and returns diverse population

    Parameters
    ----------
    city : object
        City object of pyCity_calc
    nb_ind : int
        Number of desired objects
    nb_runs : int
        Number of runs per MC run per evaluation of objective function
    failure_tolerance : float, optional
        Allowed EnergyBalanceException failure tolerance (default: 0.05).
        E.g. 0.05 means, that 5% of runs are allowed to fail with
        EnergyBalanceException.
    sampling_method : str
        Defines method used for sampling.
        Options:
        - 'lhc': latin hypercube sampling
        - 'random': randomized sampling
    dict_restr : dict
        Dict holding possible energy system sizes
    use_chp : bool, optional
        Defines, if CHP systems should be used (default: True)
    use_lhn : bool, optional
        Defines, if local heating networks (LHN) should be used (default: True)
    use_hp_aw : bool, optional
        Defines, if air water heat pumps systems should be used (default: True)
    use_hp_ww : bool, optional
        Defines, if water water heat pumps systems should be used
        (default: True)
    use_pv : bool, optional
        Defines, if PV systems should be used (default: True)
    eeg_pv_limit : bool, optional
        Defines, if EEG PV feed-in limitation of 70 % of peak load is
        active (default: False). If limitation is active, maximal 70 %
        of PV peak load are fed into the grid.
        However, self-consumption is used, first.
    pv_min : float, optional
        Minimum possible PV area per building in m2 (default: None)
    pv_step : float, optional
        Defines discrete step of Pv sizing in m2 (default: 1). E.g.
        If minimum PV size is 8 m2, 9, 10, 11...up to max. rooftop area can
        be chosen as PV size.
    add_pv_prop : float, optional
        Defines additional probability of PV being changed, if only thermal
        mutation has been applied (defauft: 0). E.g. if boiler system has
        been changed to CHP, there is a change of add_pv_prob that also PV
        is mutated.
    use_street : bool, optional
        Use street networks to route LHN pipelines (default: False)
        Requires street nodes and edges on city graph, is use_street == True
    do_upscale : bool, optional
        Boolean to define, if peak load devices should have the change to
        be upscaled (only for choice 'randomized'), (default: False)
    use_kwkg_lhn_sub : bool, optional
        Defines, if KWKG LHN subsidies are used (default: False).
        If True, can get 100 Euro/m as subdidy, if share of CHP LHN fed-in
        is equal to or higher than 60 %
    use_size_restr : bool, optional
        Defines, if pre-calculate values should be strictly rounded to values
        given by dict_restr (default: True)
    dem_unc : bool, optional
        Defines, if thermal, el. and dhw demand are assumed to be uncertain
        (default: True). If True, samples demands. If False, uses reference
        demands.
    prevent_boi_lhn : bool, optional
		Prevent boi/eh LHN combinations (without CHP) (default: True).
		If True, adds CHPs to LHN systems without CHP

    Returns
    -------
    pop : list (of dicts)
        List representing population (holding individuum dicts ind)
    """

    assert nb_ind > 0

    #  Extract max. possible PV areas and add to dict
    dict_max_pv_area = pvareas.get_dict_usable_pv_areas(city=city)

    print()
    print('Maximum usable PV areas per building in m2:')
    for key in dict_max_pv_area.keys():
        print('Building id: ', key)
        print('Max. usable PV area in m2: ', dict_max_pv_area[key])

    #  Get dict with max. space heating power per building
    dict_sh = getmaxsh.get_dict_max_sh_city(city=city)

    print()
    print('Maximum space heating power per building in Watt:')
    for key in dict_sh.keys():
        print('Building id: ', key)
        print('Max. sh. power in Watt: ', dict_sh[key])
    print()

    build_standard = 'old'

    print('Estimate design heat loads for space heating AND hot water per '
          'building, assuming ' + str(build_standard) + ' building standard.')

    dict_heatloads = estdhl.calc_heat_load_per_building(
        city=city,
        build_standard=build_standard)

    for key in dict_heatloads.keys():
        print('Building id: ', key)
        print('Design heat load (space heating AND hot water) in kW: ',
              round(dict_heatloads[key]) / 1000)
    print()

    #  Add bes to all buildings, which do not have bes, yet
    #  Moreover, add initial boiler systems to overwrite existing esys combis
    addbes.add_bes_to_city(city=city, add_init_boi=True)

    #  Initialize mc runner object and hand over initial city object
    mc_run = runmc.init_base_mc_objects(city=city)

    #  Perform initial sampling
    mc_run.perform_sampling(nb_runs=nb_runs, save_samples=True,
                            dem_unc=dem_unc)
    #  Save results toself._dict_samples_const = dict_samples_const
    #         self._dict_samples_esys = dict_samples_esys

    ga_runner = optga.GARunner(mc_runner=mc_run,
                               nb_runs=nb_runs,
                               failure_tolerance=failure_tolerance)

    if (objective == 'mc_risk_av_ann_co2_to_net_energy'
            or objective == 'ann_and_co2_to_net_energy_ref_test'
            or objective == 'ann_and_co2_ref_test'
            or objective == 'mc_risk_av_ann_and_co2'
            or objective == 'mc_mean_ann_and_co2'
            or objective == 'mc_risk_friendly_ann_and_co2'
            or objective == 'mc_min_std_of_ann_and_co2'
            or objective == 'mc_dimless_eco_em_2d_mean'
            or objective == 'mc_dimless_eco_em_2d_risk_av'
            or objective == 'mc_dimless_eco_em_2d_risk_friendly'
            or objective == 'ann_and_co2_dimless_ref'
            or objective == 'mc_dimless_eco_em_2d_std'
    ):
        # Create fitness with two objectives (to be minimized)
        creator.create("Fitness", base.Fitness, weights=(-1.0, -1.0))
        creator.create("Individual", dict, fitness=creator.Fitness)

    elif (objective == 'mc_dimless_eco_em_3d_mean'
          or objective == 'mc_dimless_eco_em_3d_risk_av'
          or objective == 'mc_dimless_eco_em_3d_risk_friendly'
          or objective == 'ann_and_co2_dimless_ref_3d'
          or objective == 'mc_dimless_eco_em_3d_std'
    ):
        # Create fitness with three objectives (2 min. / 1 max.)
        creator.create("Fitness", base.Fitness, weights=(-1.0, -1.0, 1.0))
        creator.create("Individual", dict, fitness=creator.Fitness)

    else:
        msg = 'Unknown objective chosen!'
        raise AssertionError(msg)

    # Initialize toolbox
    #  ####################################################################
    toolbox = base.Toolbox()

    creator.create("Fitness", base.Fitness, weights=(-1.0, -1.0))
    creator.create("Individual", dict, fitness=creator.Fitness)

    #  Register function to parse city info to individuum
    #  Individuum is represented by dictionary, holding building ids and 'lhn'
    #  as key and energy system dictionaries as values.
    #  If dict_ind is None, uses city to extract data. Else, dict_ind is used
    toolbox.register('parse_city_to_ind', parsecity.hand_over_dict,
                     dict_ind=None,
                     city=ga_runner._city,
                     list_build_ids=ga_runner._list_build_ids)

    #  Register individual in toolbox (create individual with parse_city_to_ind
    #  by parsing city energy system attributes to individuum)
    toolbox.register('individual', tools.initIterate, creator.Individual,
                     toolbox.parse_city_to_ind)

    #  Register the population (based on repeated generation of individuals)
    toolbox.register('population', tools.initRepeat, list, toolbox.individual)

    #  Add evaluate function
    # ga_runner_copy = copy.deepcopy(ga_runner)
    toolbox.register('evaluate', eval.eval_obj,
                     ga_runner=ga_runner,
                     objective=objective,
                     eeg_pv_limit=eeg_pv_limit,
                     dict_restr=dict_restr,
                     dict_max_pv_area=dict_max_pv_area,
                     dict_sh=dict_sh,
                     pv_min=pv_min,
                     pv_step=pv_step,
                     use_pv=use_pv,
                     add_pv_prop=add_pv_prop,
                     use_street=use_street,
                     sampling_method=sampling_method,
                     use_kwkg_lhn_sub=use_kwkg_lhn_sub,
                     el_mix_for_chp=el_mix_for_chp,
                     el_mix_for_pv=el_mix_for_pv,
                     prevent_boi_lhn=prevent_boi_lhn,
                     dict_heatloads=dict_heatloads
                     )

    #  Generate initial population (to be modified)
    pop = toolbox.population(n=nb_ind)

    #  Delete existing energy systems (to prevent their usage)
    addbes.del_existing_esys(city=city)

    #  Add initial bes and energy systems to city
    addbes.add_bes_to_city(city=city)

    #  Remove heating, heating_and_deg and electricity edges from city
    delnet.del_energy_network_in_city(city=city)

    for i in range(nb_ind):

        curr_ind = pop[i]

        if i == 0:
            method = 'boi_only'
        elif i == 1:
            method = 'boi_tes_only'
        elif i == 2 and use_chp and use_lhn:
            method = 'chp_with_overall_LHN'
        elif i == 3 and use_chp:
            method = 'chp_decentral'
        elif i == 4 and use_hp_aw:
            method = 'hp_aw_decentral'
        elif i == 5 and use_hp_ww:
            method = 'hp_ww_decentral'
        elif i == 6 and use_chp and use_hp_aw and use_hp_ww:
            method = 'chp_hp_50'
        elif i == 7 and use_chp and use_lhn and use_hp_ww:
            method = 'kmeans'
        elif i == 8 and use_chp and use_lhn:
            method = 'chp_with_overall_LHN_small_PV'
        elif i == 9 and use_chp and use_lhn and use_pv:
            method = 'chp_with_overall_LHN_medium_PV'
        elif i == 10 and use_chp and use_lhn and use_pv:
            method = 'chp_with_overall_LHN_large_PV'
        elif i == 11 and use_chp and use_lhn and use_pv:
            method = 'chp_with_overall_LHN_max_PV'
        elif i == 12 and use_chp and use_lhn and use_pv and use_hp_ww:
            method = 'kmeans_large_pv'
        elif i == 13 and use_hp_aw and use_pv:
            method = 'hp_aw_decentral_large_pv'
        elif i == 14 and use_hp_ww and use_pv:
            method = 'hp_ww_decentral_large_pv'
        elif i == 14:
            method = 'boi_tes_large_pv'
        elif i == 15 and use_chp and use_lhn:
            method = 'chp_with_overall_LHN_small_PV_el_node'
        elif i == 16 and use_chp and use_lhn and use_pv:
            method = 'chp_with_overall_LHN_medium_PV_el_node'
        elif i == 17 and use_chp and use_lhn and use_pv:
            method = 'chp_with_overall_LHN_large_PV_el_node'
        elif i == 18 and use_chp and use_lhn and use_pv:
            method = 'chp_with_overall_LHN_max_PV_el_node'
        elif i == 19 and use_chp and use_lhn and use_pv and use_hp_ww:
            method = 'kmeans_large_pv_el_node'
        elif i == 20 and use_pv:
            method = 'boi_tes_max_pv'
        elif i == 21 and use_pv:
            method = 'boi_tes_medium_pv'
        elif i == 22 and use_chp and use_lhn:
            method = 'kmeans_boi'
        elif i == 23 and use_chp and use_lhn and use_pv:
            method = 'kmeans_boi_large_pv'
        elif i == 24 and use_chp and use_lhn and use_pv:
            method = 'kmeans_boi_max_pv'
        elif i == 25 and use_chp and use_lhn and use_pv and use_hp_aw:
            method = 'chp_lhn_50_hp_aw_50_large_pv'
        elif i == 26 and use_chp and use_lhn and use_pv and use_hp_ww:
            method = 'chp_lhn_50_hp_ww_50_large_pv'
        elif i == 27 and use_chp and use_lhn and use_pv:
            method = 'multi_chps_one_lhn_large_pv'
        elif i == 28 and use_chp and use_lhn and use_pv:
            method = 'multi_chps_one_lhn'
        elif i == 29 and use_chp and use_lhn and use_pv:
            method = 'half_chps_one_lhn_large_pv'
        else:
            method = 'randomized'

        #  Change population individuum
        mod_ind(city=city, method=method, ind=curr_ind,
                toolbox=toolbox,
                dict_restr=dict_restr,
                use_chp=use_chp,
                use_lhn=use_lhn,
                use_hp_aw=use_hp_aw,
                use_hp_ww=use_hp_ww,
                use_pv=use_pv,
                dict_sh=dict_sh,
                dict_max_pv_area=dict_max_pv_area,
                do_upscale=do_upscale,
                use_size_restr=use_size_restr,
                dict_heatloads=dict_heatloads)

        for ind in pop:
            # Check configuration
            #  #############################################################

            checkval.run_all_checks(ind=ind, dict_max_pv_area=dict_max_pv_area,
                                    dict_restr=dict_restr, dict_sh=dict_sh,
                                    pv_min=pv_min, pv_step=pv_step,
                                    use_pv=use_pv,
                                    add_pv_prop=add_pv_prop,
                                    prevent_boi_lhn=prevent_boi_lhn,
                                    dict_heatloads=dict_heatloads)

    return (pop, toolbox)


if __name__ == '__main__':
    #  Define pathes
    #  ####################################################################
    this_path = os.path.dirname(os.path.abspath(__file__))
    src_path = os.path.dirname(os.path.dirname(this_path))
    workspace = os.path.join(src_path, 'workspace')

    #  Number of desired individuums
    nb_ind = 200
    nb_runs = 100
    failure_tolerance = 0.05

    #  Defines, if thermal peak load devices should have the chance that their
    #  nominal thermal power can be upscaled/increased
    #  (for 'randomized' choice)
    do_upscale = True

    #  Rescale space heating peak load demand day (use resc_factor to rescale
    #  space heating peak load day power values; keeps annual space heating
    #  demand constant; comparable to procedure in pyCity_opt for robust
    #  rescaling)
    do_peak_load_resc = False
    resc_factor = 1

    #  Define, if pre-calculate values should be strictly rounded to values
    #  given by dict_restr
    use_size_restr = True

    #  Prevent specific energy system combinations
    use_chp = True  # Use combined heat and power (CHP) systems
    use_lhn = True  # Use local heating network mutations
    use_hp_aw = True  # Use air-water heat pumps
    use_hp_ww = True  # Use water-water heat pumps
    use_pv = True  # Use PV units
    prevent_boi_hp = False
    prevent_chp_eh = False

    prevent_boi_lhn = True

    pv_min = 8
    pv_step = 1
    add_pv_prop = 0.2

    use_kwkg_lhn_sub = False

    el_mix_for_chp = True  # Use el. mix for CHP fed-in electricity
    el_mix_for_pv = True  # Use el. mix for PV fed-in electricity

    #  Objective function(s)
    #  #############################################
    # objective = 'mc_dimless_eco_em_2d_mean'
    # #  Use risk neutral (mean) values of dimless cost and co2

    # objective = 'mc_dimless_eco_em_2d_risk_av'
    # #  Use risk averse values of dimless cost and co2

    # objective = 'mc_dimless_eco_em_2d_risk_friendly'
    # #  Use risk friendly values of dimless cost and co2

    objective = 'mc_dimless_eco_em_2d_std'
    #  Use minimization of standard deviation (std) with 2d function

    # objective = 'mc_dimless_eco_em_3d_mean'
    # #  Use risk neutral (mean) values of dimless cost and co2 (plus flexibility)

    # objective = 'mc_dimless_eco_em_3d_risk_av'
    # #  Use risk averse values of dimless cost and co2 plus flexibility)

    # objective = 'mc_dimless_eco_em_3d_risk_friendly'
    # #  Use risk friendly values of dimless cost and co2 plus flexibility)

    # objective = 'mc_dimless_eco_em_3d_std'
    # #  Use minimization of standard deviation (std) with 3d function

    # objective = 'mc_risk_av_ann_co2_to_net_energy'
    #  Use risk averse annuity / CO2 to net energy values

    # objective = 'mc_risk_av_ann_and_co2'
    #  Use risk averse annuity and co2 values

    # objective = 'mc_mean_ann_and_co2'
    # #  Use risk neutral (mean) values of annuity and co2

    # objective = 'mc_risk_friendly_ann_and_co2'
    # #  Use risk averse annuity and co2 values

    # objective = 'mc_min_std_of_ann_and_co2'
    # #  Minimize standard deviation (std) of annuity and co2 emissions

    # objective = 'ann_and_co2_dimless_ref'
    # # #  Perform dimensionless cost and co2 reference run

    # objective = 'ann_and_co2_dimless_ref_3d'
    # # #  Perform dimensionless cost and co2 reference run

    # objective = 'ann_and_co2_to_net_energy_ref_test'
    # #  Use annuity and co2 to net energy ratios of reference run (test case)

    # objective = 'ann_and_co2_ref_test'
    # #  Use absolute values of annuity and co2
    #  #############################################

    evaluate_pop = False
    #  Perform evaluation --> Calculate fitness of each individuum

    eeg_pv_limit = True  # Only relevant if evaluate_pop = True

    use_own_max_val = False
    #  If use_own_max_val is True, use user defines max values for boiler size
    #  if use_own_max_val is False, defines max. possible loads based on th. peak
    #  load of city

    sampling_method = 'lhc'

    dem_unc = True
    #  dem_unc : bool, optional
    # Defines, if thermal, el. and dhw demand are assumed to be uncertain
    # (default: True). If True, samples demands. If False, uses reference
    # demands.

    #  Max. possible values
    boiler_max = 1000000  # in Watt
    tes_max = 10000  # in liters
    chp_max = 100000  # in Watt (thermal)
    hp_aw_max = 100000  # in Watt (thermal)
    hp_ww_max = 100000  # in Watt (thermal)
    eh_max = 100000  # in Watt
    bat_max = 20  # in kWh

    #  Name city object
    #  ############################################
    # city_name = 'city_clust_simple_with_esys.pkl'
    # city_name = 'city_2_build_with_esys.pkl'
    # city_name = 'wm_res_east_7_w_street.pkl'
    # city_name = 'wm_res_east_7_w_street_sh_resc_wm.pkl'
    city_name = 'kronen_6_new.pkl'

    path_city = os.path.join(workspace, 'city_objects',
                             # 'with_esys',
                             'no_esys',
                             city_name)

    #  Define path to save diverse population
    if do_peak_load_resc:
        pop_name = 'pop_div_ind_' + str(nb_ind) + '_' + str(city_name[:-4]) \
                   + '_rescale_' + str(resc_factor) + '.pkl'
    else:
        pop_name = 'pop_div_ind_' + str(nb_ind) + '_' + str(city_name[:-4]) \
                   + '.pkl'
    path_save = os.path.join(workspace, 'init_populations', pop_name)

    #  Load city object instance
    city = pickle.load(open(path_city, mode='rb'))

    #  Workaround: Add additional emissions data, if necessary
    try:
        print(city.environment.co2emissions.co2_factor_pv_fed_in)
    except:
        msg = 'co2em object does not have attribute co2_factor_pv_fed_in. ' \
              'Going to manually add it.'
        warnings.warn(msg)
        city.environment.co2emissions.co2_factor_pv_fed_in = 0.651

    #  Perform space heating peak load day rescaling
    if do_peak_load_resc:

        list_build_ids = city.get_list_build_entity_node_ids()

        #  Loop over all buildings
        for n in list_build_ids:
            #  Current building
            build = city.nodes[n]['entity']

            modpeak.resc_sh_peak_load_build(building=build,
                                            resc_factor=resc_factor)

    #  Overwrite given user values, if ues_own_max_val is False
    if use_own_max_val is False:
        city_th_peak_sh_and_dhw = dimfunc.get_max_p_of_city(city_object=city,
                                                            get_thermal=True,
                                                            with_dhw=True)

        city_th_peak_only_sh = dimfunc.get_max_p_of_city(city_object=city,
                                                         get_thermal=True,
                                                         with_dhw=False)

        boiler_max = 5 * int(round(city_th_peak_only_sh / 10000, 0) * 10000)
        chp_max = int(round((city_th_peak_only_sh / 2) / 10000, 0) * 10000)
        print('Replace boiler_max with ' + str(boiler_max) + ' Watt.')
        print('Replace chp_max with ' + str(chp_max) + ' Watt thermal power.')

    dict_restr = {'boi': list(range(10000, boiler_max + 10000, 10000)),
                  'tes': list(range(100, tes_max + 100, 100)),
                  'chp': list(range(1000, 10000, 1000)) + list(
                      range(10000, chp_max + 5000, 5000)),
                  'hp_aw':  # list(range(5000, 10000, 1000)) +
                      list(range(5000, hp_aw_max + 5000, 5000)),
                  'hp_ww':  # list(range(5000, 10000, 1000)) +
                      list(range(5000, hp_ww_max + 5000, 5000)),
                  'eh':  # list(range(5000, 10000, 1000)) +
                      list(range(5000, eh_max + 5000, 5000)),
                  'bat': list(range(0, bat_max * 3600 * 1000 + 1 * 3600 * 1000,
                                    1 * 3600 * 1000))}  # bat in Joule!!

    #  ####################################################################

    #  If energy flags are False, prevent usage of specific energy system
    if use_chp is False:
        #  If no CHP can be used, set use_lhn to False
        if use_lhn:
            msg = 'use_lhn is True, but use_chp is False. Thus, going to set' \
                  ' use_lhn to False!'
            warnings.warn(msg)
            use_lhn = False
    if use_lhn is False:
        prob_lhn = 0
    if use_pv is False:
        add_pv_prop = 0

    #  List energy system mutation options with probabilities
    #  Do NOT modify names of list_options, as they are used as keywords!
    list_options = ['boi', 'boi_tes', 'chp_boi_tes', 'chp_boi_eh_tes',
                    'hp_aw_eh', 'hp_ww_eh', 'hp_aw_boi', 'hp_ww_boi',
                    'hp_aw_eh_boi', 'hp_ww_eh_boi', 'bat', 'pv']
    list_opt_prob = [0.1, 0.1, 0.2, 0.05, 0.1, 0.1, 0.05, 0.05, 0.05,
                     0.05, 0.05, 0.1]

    #  List LHN energy system mutation options with probabilities
    #  Do NOT modify names of list_options, as they are used as keywords!
    list_lhn_opt = ['chp_boi_tes', 'chp_boi_eh_tes',
                    'bat', 'pv', 'no_th_supply']
    list_lhn_prob = [0.1, 0.05, 0.05, 0.2, 0.6]

    #  Modify default probabilities, if necessary (e.g. esys boolean flags are
    #  False)

    #  Use energy system boolean flags to modify list_opt_prob, if necessary
    list_opt_prob = \
        modprob.mod_list_esys_options(list_options=list_options,
                                      list_opt_prob=list_opt_prob,
                                      use_bat=False,
                                      use_pv=use_pv,
                                      use_chp=use_chp,
                                      use_hp_aw=use_hp_aw,
                                      use_hp_ww=use_hp_ww,
                                      prevent_boi_hp=prevent_boi_hp,
                                      prevent_chp_eh=prevent_chp_eh)
    #  Modify list_lhn_opt, if necessary (not
    list_lhn_prob = modprob. \
        mod_list_lhn_options(list_lhn_opt=list_lhn_opt,
                             list_lhn_prob=list_lhn_prob,
                             use_bat=False, use_pv=use_pv)

    #  Generate list for building stand alone mutation
    list_lhn_to_stand_alone = modprob. \
        mod_list_esys_options(
        list_options=list_options,
        list_opt_prob=list_opt_prob,
        use_bat=False,
        use_pv=False,
        use_chp=use_chp,
        use_hp_aw=use_hp_aw,
        use_hp_ww=use_hp_ww,
        prevent_boi_hp=prevent_boi_hp,
        prevent_chp_eh=prevent_chp_eh)

    assert abs(sum(list_opt_prob) - 1) < 0.0000000001
    assert abs(sum(list_lhn_prob) - 1) < 0.0000000001
    assert abs(sum(list_lhn_to_stand_alone) - 1) < 0.0000000001

    #  ####################################################################

    #  Generate diverse population
    (pop_div, toolbox) = gen_diverse_pop(city=city, nb_ind=nb_ind,
                                         nb_runs=nb_runs,
                                         failure_tolerance=failure_tolerance,
                                         use_chp=use_chp,
                                         use_lhn=use_lhn,
                                         use_hp_aw=use_hp_aw,
                                         use_hp_ww=use_hp_ww,
                                         use_pv=use_pv,
                                         objective=objective,
                                         pv_min=pv_min, pv_step=pv_step,
                                         add_pv_prop=add_pv_prop,
                                         eeg_pv_limit=eeg_pv_limit,
                                         sampling_method=sampling_method,
                                         do_upscale=do_upscale,
                                         use_kwkg_lhn_sub=use_kwkg_lhn_sub,
                                         dict_restr=dict_restr,
                                         use_size_restr=use_size_restr,
                                         dem_unc=dem_unc,
                                         prevent_boi_lhn=prevent_boi_lhn
                                         )

    for ind in pop_div:
        print(ind)

    # Save diverse population
    pickle.dump(pop_div, open(path_save, mode='wb'))

    if evaluate_pop:

        #  Perform evaluation
        #  ################################################################

        list_ann = []
        list_co2 = []

        #  Perform manual energy balance and annuity calculation
        #  ################################################################
        count = 0
        for ind in pop_div:

            #  Generate city with ind object
            city_esys = parseindcit.parse_ind_dict_to_city(dict_ind=ind,
                                                           city=city)

            annuity_obj = annu.EconomicCalculation()
            energy_balance = citeb.CityEBCalculator(city=city_esys)
            city_eco_calc = citecon.CityAnnuityCalc(annuity_obj=annuity_obj,
                                                    energy_balance=energy_balance)

            (total_annuity, co2) = city_eco_calc. \
                perform_overall_energy_balance_and_economic_calc(eeg_pv_limit=
                                                                 eeg_pv_limit,
                                                                 el_mix_for_chp=
                                                                 el_mix_for_chp,
                                                                 el_mix_for_pv=
                                                                 el_mix_for_pv
                                                                 )
            list_ann.append(total_annuity)
            list_co2.append(co2)

            if count < 10:
                marker = 'o'
            elif count < 20:
                marker = '*'
            else:
                marker = '+'

            plt.plot([total_annuity], [co2], marker=marker, label=count)
            count += 1

        plt.xlabel('Total annualized cost in Euro/a')
        plt.ylabel('Total CO2 emissions in kg/a')
        plt.legend()
        plt.tight_layout()
        plt.show()
        plt.close()

        #  Evaluate initial population
        print('Evaluate initial population')
        fitnesses = toolbox.map(toolbox.evaluate, pop_div)

        list_ann_fit = []
        list_co2_fit = []

        #  Save fitness values to each individuum
        for ind, fit in zip(pop_div, fitnesses):
            ind.fitness.values = fit
            list_ann_fit.append(fit[0])
            list_co2_fit.append(fit[1])

        print('Initial Population:')
        for i in pop_div:
            print('Individuum: ', i)
            print('Fitness: ', i.fitness.values)
        print()

        plt.scatter(list_ann, list_co2, label='pyCity_calc', marker='o')
        plt.scatter(list_ann_fit, list_co2_fit, label='Fit. (GA)', marker='*')
        plt.xlabel('Total annualized cost in Euro/a')
        plt.ylabel('Total CO2 emissions in kg/a')
        plt.legend()
        plt.tight_layout()
        plt.show()
        plt.close()

    print('Saved pickle file with diverse initial population to: ')
    print(path_save)
    print()
