#!/usr/bin/env python
# coding=utf-8
"""
Generate city object with energy systems by using solution of final pareto
frontiers solutions
"""
from __future__ import division

import os
import pickle
import copy

import pycity_resilience.ga.parser.parse_ind_to_city as parseind2city
import pycity_resilience.ga.preprocess.add_bes as addbes

import pycity_resilience.ga.opt_ga  # Necessary to load pickle files!
from deap import base, creator, tools, algorithms


def gen_cities_with_pareto_solutions(city, dict_par_sol, list_sol_nb):
    """
    Generate city objects with energy systems based on indivduals in
    of final pareto frontier

    Parameters
    ----------
    city : object
        City object without energy system
    dict_par_sol : dict
        Dict holding individuals of GA run with solution number as key
        and individual object as value
    list_sol_nb : list (of ints)
        List holding all solution numbers, which should be returned as cities

    Returns
    -------
    dict_cities : dict
        Dict holding solution numbers as key and city object as value
    """

    assert len(list_sol_nb) > 0

    dict_cities = {}

    #  Copy city to prevent unwanted modification by add_bes_to_city
    city = copy.deepcopy(city)

    #  Get list of building ids
    list_build_ids = city.get_list_build_entity_node_ids()

    #  Add all subsystems, necessary to work with GA parser
    addbes.add_bes_to_city(city=city, add_init_boi=False)

    for n in list_sol_nb:
        #  Extract individual
        ind = dict_par_sol[n]

        #  Parse ind to city
        city_new = parseind2city.parse_ind_dict_to_city(dict_ind=ind,
                                                        city=city,
                                                        use_street=False,
                                                        copy_city=True)

        #  Erase all energy system objects, if esys is False
        for id in list_build_ids:
            build = city_new.nodes[id]['entity']
            if build.hasBes:
                if build.bes.hasBattery is False:
                    build.bes.battery = []
                if build.bes.hasBoiler is False:
                    build.bes.boiler = []
                if build.bes.hasChp is False:
                    build.bes.chp = []
                if build.bes.hasElectricalHeater is False:
                    build.bes.electricalHeater = []
                if build.bes.hasHeatpump is False:
                    build.bes.heatpump = []
                if build.bes.hasPv is False:
                    build.bes.pv = []
                if build.bes.hasTes is False:
                    build.bes.tes = []

        #  Add to dict_cities
        dict_cities[n] = city_new

    return dict_cities


if __name__ == '__main__':
    #  Define pathes
    #  ####################################################################
    this_path = os.path.dirname(os.path.abspath(__file__))
    src_path = os.path.dirname(os.path.dirname(os.path.dirname(this_path)))
    workspace = os.path.join(src_path, 'workspace')

    #  Solution number to be extracted
    list_sol_nb = [1, 22, 33, 56]

    #  Path to city pickle file
    city_name = 'aachen_kronenberg_6.pkl'
    path_city = os.path.join(workspace, 'city_objects', 'no_esys', city_name)

    #  Path to dict with final pareto frontier solutions of GA run
    name_dict_par_sol = 'ga_run_aachen_kronenberg_6_peak_resc_2_chp_pen_dict_par_front_sol.pkl'
    path_results = os.path.join(workspace, 'output', 'ga_opt',
                                name_dict_par_sol)

    #  Path to output folder
    path_output = os.path.join(workspace, 'output', 'city_sol')

    #  Generate path_output, if not existent
    if not os.path.exists(path_output):
        os.makedirs(path_output)

    #  Load city object without energy systems
    city = pickle.load(open(path_city, mode='rb'))

    #  Load results file
    dict_par_sol = pickle.load(open(path_results, mode='rb'))

    #  Return dict with city object (with energy systems)
    dict_cities = \
        gen_cities_with_pareto_solutions(city=city,
                                         dict_par_sol=dict_par_sol,
                                         list_sol_nb=list_sol_nb)

    #  Save all city objects to path_output folder
    for key in dict_cities.keys():
        city_new = dict_cities[key]
        city_name = 'city_par_sol_' + str(key) + '.pkl'
        path_city_out = os.path.join(path_output, city_name)
        pickle.dump(city_new, open(path_city_out, mode='wb'))
