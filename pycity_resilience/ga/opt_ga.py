#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

"""
from __future__ import division

import os
import sys
import time
import copy
import pickle
import random
import datetime
import numpy as np
import multiprocessing
import warnings

import pycity_calc.toolbox.dimensioning.dim_functions as dimfunc
import pycity_calc.toolbox.modifiers.mod_resc_peak_load_day as modpeak

import pycity_resilience.monte_carlo.run_mc as runmc
import pycity_resilience.ga.parser.parse_city_to_ind as parsecity
import pycity_resilience.ga.preprocess.add_bes as addbes
import pycity_resilience.ga.evaluate.eval as eval
import pycity_resilience.ga.preprocess.pv_areas as pvareas
import pycity_resilience.ga.evolution.crossover as cx
import pycity_resilience.ga.evolution.mutation as muta
import pycity_resilience.ga.preprocess.get_pos as getpos
import pycity_resilience.ga.selection.select as selec
import pycity_resilience.ga.preprocess.del_energy_networks as delnet
import pycity_resilience.ga.evolution.helpers.mod_esys_prob as modprob
import pycity_resilience.ga.preprocess.get_max_sh as getmaxsh
import pycity_resilience.ga.preprocess.est_sh_dhw_design_heat_load as estdhl

from scoop import futures
from deap import base, creator, tools, algorithms


# #  Activate seed
# random.seed(1)


class GARunner(object):
    def __init__(self, mc_runner, nb_runs, failure_tolerance):
        """
        Constructor of GA Runner object instance

        Parameters
        ----------
        mc_runner : object
            MC Runner object of pyCity_calc
        nb_runs : int
            Number of runs per MC run per evaluation of objective function
        failure_tolerance : float, optional
            Allowed EnergyBalanceException failure tolerance (default: 0.05).
            E.g. 0.05 means, that 5% of runs are allowed to fail with
            EnergyBalanceException.
        """

        self.mc_runner = mc_runner
        self.nb_runs = nb_runs
        self.failure_tolerance = failure_tolerance

        #  MC results for reference system (rescaled boilers)
        #  Required for dimensionless cost and co2 fitnesses
        self._dict_mc_res_ref = None

        #  annuity anc co2 values for reference run (rescaled boilers)
        self._ann_ref = None
        self._co2_ref = None

        #  Pointers to sub-objects in mc_runner
        self._city = mc_runner._city_eco_calc.energy_balance.city
        self._list_build_ids = mc_runner._list_build_ids


# Initialize toolbox
#  ####################################################################
toolbox = base.Toolbox()

#  Define pathes
#  ####################################################################
this_path = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.dirname(os.path.dirname(this_path))
workspace = os.path.join(src_path, 'workspace')

timestamp = str('{:%Y_%m_%d_%Hh_%Mmin_%Ssec}'.
                format(datetime.datetime.now()))

#  General user inputs
#  ####################################################################
#  ####################################################################

#  ############################################

#  Multiprocessing
#  ############################################

use_scoop = True
#  True, use SCOOP for multiprocessing
#  False, use multiprocessing library

#  Enable multiprocessing (Python standard library)
nb_processes = 3
#  Only relevant as input for multiprocessing library usage
#  SCOOP automatically tries to use maximum number of available cores,
#  except the user hands over cmd window parameter

#  Project name / log folder name
log_folder = 'ga_run'
#  Defines path, where results should be logged

#  ############################################

#  Load city object
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

#  Load pickled city object (with energy systems)
city = pickle.load(open(path_city, mode='rb'))
#  ############################################

# #  Workaround: Add additional emissions data, if necessary
# try:
#     print(city.environment.co2emissions.co2_factor_pv_fed_in)
# except:
#     msg = 'co2em object does not have attribute co2_factor_pv_fed_in. ' \
#           'Going to manually add it.'
#     warnings.warn(msg)
#     city.environment.co2emissions.co2_factor_pv_fed_in = 0.651

#  Initialize diverse population or equal one?
############################################
init_diverse = True

#  #  If init_diverse is True
pop_name = 'pop_div_ind_200_kronen_6_new.pkl'
# pop_name = 'pop_div_ind_200_aachen_kronenberg_6_rescale_3.pkl'

#  #  Define folder to load pickled population
path_pop = os.path.join(workspace, 'init_populations', pop_name)
#  ############################################

add_init_boi = True  # Overwrite esys with init boilers

#  ############################################

#  GA general settings
#  ############################################

#  Sizes
nb_ind = 200  # Number of individuums in population
ngen = 500  # Nb. of generations
nb_runs = 100  # Nb. of MC runs per fitness evaluation
size_hof = 4  # Number of candidates in hall of fame

nb_min_gen = 30  # number of generations over which the standard
# deviation  should be constant to terminate run

std_break = 0.001
# Min standard deviation factor, which causes GA run to exit iterations
#  min_std = std_break * best_obj_fct_value

#  Settings for energy balance monte-carlo run
failure_tolerance = 0.05  # Share of allowed failed runs in MC analysis

#  Use street routings to construct lhn pipes or el. cables
use_street = False

sampling_method = 'lhc'
#  Options for sampling_method:
#  'lhc': Latin hypercube (lhc)
#  'random': Randomized

dem_unc = False
# dem_unc : bool, optional
# 	Defines, if thermal, el. and dhw demand are assumed to be uncertain
# 	(default: True). If True, samples demands. If False, uses reference
# 	demands.

heating_off = False
#  Defines, if heating can be switched of during summer

#  ##############################
#  Rescale space heating peak load demand day (use resc_factor to rescale
#  space heating peak load day power values; keeps annual space heating
#  demand constant; comparable to procedure in pyCity_opt for robust
#  rescaling)
do_peak_load_resc = False
resc_factor = 1
#  Perform space heating peak load day rescaling
if do_peak_load_resc:

    list_build_ids = city.get_list_build_entity_node_ids()

    #  Loop over all buildings
    for n in list_build_ids:
        #  Current building
        build = city.nodes[n]['entity']

        modpeak.resc_sh_peak_load_build(building=build,
                                        resc_factor=resc_factor)
#  ##############################

#  Defines, if pre-generated sample file should be loaded
#  ##############################

load_city_n_build_samples = False
#  Defines, if city and building sample dictionaries should be loaded
#  instead of generating new samples

#  kronen_6_resc_2_dict_city_samples are also valid for kronen_6 without
#  rescaling!
city_sample_name = 'kronen_6_resc_2_dict_city_samples.pkl'
build_sample_name = 'kronen_6_resc_2_dict_build_samples.pkl'

path_city_sample_dict = os.path.join(workspace,
                                     'mc_sample_dicts',
                                     city_sample_name)

path_build_sample_dict = os.path.join(workspace,
                                      'mc_sample_dicts',
                                      build_sample_name)

#  Defines, if space heating samples should be loaded (only relevant, if
#  space heating results of monte-carlo simulation exist and
#  load_city_n_build_samples is False (as path_build_sample_dict  already
#  include space heating samples)
load_sh_mc_res = False

#  Path to FOLDER with mc sh results (searches for corresponding building ids)
path_mc_res_folder = os.path.join(workspace,
                                  'mc_sh_results')

use_profile_pool = False

gen_use_prof_method = 1
#  Options:
#  0: Generate new profiles during runtime
#  1: Load pre-generated profile sample dictionary

#  kronen_6_resc_2_dict_profile_20_samples are also valid for kronen_6 without
#  rescaling!
el_profile_dict = 'kronen_6_resc_2_dict_profile_20_samples.pkl'
path_profile_dict = os.path.join(workspace,
                                 'mc_el_profile_pool',
                                 el_profile_dict)

#  #############################################

#  Objective function(s)
#  #############################################
# objective = 'mc_dimless_eco_em_2d_mean'
# #  Use risk neutral (mean) values of dimless cost and co2

# objective = 'mc_dimless_eco_em_2d_risk_av'
# #  Use risk averse values of dimless cost and co2

# objective = 'mc_dimless_eco_em_2d_risk_friendly'
# #  Use risk friendly values of dimless cost and co2

# objective = 'mc_dimless_eco_em_2d_std'
# #  Use minimization of standard deviation (std) with 2d function

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

objective = 'ann_and_co2_ref_test'
#  Use absolute values of annuity and co2
#  #############################################

#  Define risk factors (if risk averse or risk friendly function is used)
#  #############################################
risk_fac_av = -1
risk_fac_friendly = 1
#  #############################################

#  Add CHP penalty for too high daily switching
chp_switch_pen = True
max_switch = 6  # Max. average switching per day
# (one switch is on/off or off/on)

#  ############################################
perform_checks = True
#  Defines, if energy systems should be checked on plausibility after each
#  mutation and crossover. If False, increases speed, but only checks config.
#  before evaluation.

#  Energy system flags
#  #############################################
use_chp = True  # Use combined heat and power (CHP) systems
use_lhn = True  # Use local heating network mutations
use_hp_aw = True  # Use air-water heat pumps
use_hp_ww = True  # Use water-water heat pumps
use_pv = True  # Use PV units
use_bat = True  # Use battery mutations
prevent_boi_hp = False  # Prevent boiler / heat pump combinations
prevent_chp_eh = False  # Prevent CHP / electr. heater combinations

eeg_pv_limit = True  # Activate maximum fed-in power of 70 % of peak load of pv

use_kwkg_lhn_sub = False  # Activate KWKG LHN subsidies

el_mix_for_chp = False  # Use el. mix for CHP fed-in electricity
el_mix_for_pv = False  # Use el. mix for PV fed-in electricity

prevent_boi_lhn = True  # Prevent boi/EH-LHN combinations (CHP required)

#  Crossover settings
#  #############################################
prob_cx = 0.7  # Crossover probability
nb_part_cx = 4  # Number of participating individuums in crossover tourn.

#  Mutation settings
#  ##############################################
prob_mutation = 0.6  # Probability that mutation is applied

prob_mut = 0.3  # Probability for each attribute to be mutated
list_prob_lhn_and_esys = [0.3, 0.2, 0.5]
# List holding probabilities for LHN and esys mutation (index 0),
# LHN mutation (index 1) and single energy system mutation (index 2).
# Sum of probabilities has to be 1.
# (default: [0.4, 0.3, 0.3])

list_prob_mute_type = [0.6, 0.4]  # Prob. for change and del./gen. mutation

list_prob_lhn_gen_mut = [0.3, 0.7]
#  List holding probabilities for gen/delete LHN (index 0) and
#  probabilites to mutate LHN (index 1). Sum of probabilities has to be 1.
#  (default. [0.3, 0.7]

prob_lhn = 0.3  # Probability of (single) change of nodes in existing LHN
#  Only relevant, if select_lhn_mut == 'all_modes'

#  Min. values
pv_min = 8  # in m2 (minimum possible PV size; currently, peak to m2 ratio in
#  pyCity_calc is 0.125 kWpeak/m2 for PV --> 8 m2 equal 1 kWpeak)
#  Thus, pv_min should be int number!
pv_step = 1  # in m2 (discrete PV size step (e.g. beginning at
# pv_min + n * pv_step...until max. rooftop area is reached))

#    add_pv_prop : float, optional
#         Defines additional probability of PV being changed, if only thermal
#         mutation has been applied (defauft: 0). E.g. if boiler system has
#         been changed to CHP, there is a change of add_pv_prob that also PV
#         is mutated.
add_pv_prop = 0.2
#    add_bat_prob : float, optional
#         Defines additional probability ofBAT being changed, if only thermal
#         mutation has been applied (defauft: 0). E.g. if boiler system has
#         been changed to CHP, there is a change of add_pv_prob that also BAT
#         is mutated.
add_bat_prob = 0

#  Maximum allowed distance in m between LHN nodes
max_dist = None  # in m (if None, no limitation)

use_own_max_val = False
#  If use_own_max_val is True, use user defines max values for boiler size
#  if use_own_max_val is False, defines max. possible loads based on th. peak
#  load of city

#  Max. possible values
boiler_max = 1000000  # in Watt
tes_max = 10000  # in liters
chp_max = 50000  # in Watt (thermal)
hp_aw_max = 50000  # in Watt (thermal)
hp_ww_max = 50000  # in Watt (thermal)
eh_max = 50000  # in Watt
bat_max = 20  # in kWh

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
if use_bat is False:
    add_bat_prob = 0

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
                                  use_bat=use_bat,
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
                         use_bat=use_bat, use_pv=use_pv)

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

# Logging
#  ############################################
log_name = 'log_' + timestamp + '.txt'
folder_path = os.path.join(workspace, 'output', 'ga_opt', log_folder)
log_path = os.path.join(folder_path, log_name)

path_logbook = os.path.join(folder_path, 'logbook.pkl')

save_pop = True  # Save intermediate populations as pickle file

#  End of user inputs
#  ####################################################################
#  ####################################################################

if not isinstance(pv_min, int):
    msg = 'pv_min ' + str() + ' is no integer value! Thus, you might not ' \
                              'account for PV areas, which are at subidy ' \
                              'limits (such as 80 m2 for 10 kWpeak).'
    warnings.warn(msg)

# #  Generate folder_path, if not existent
# if not os.path.exists(folder_path):
#     os.makedirs(folder_path)

#  Generate folder_path without race condition (#166), based on:
#  https://stackoverflow.com/questions/12468022/python-fileexists-error-when-making-directory
while not os.path.exists(folder_path):
    try:
        os.makedirs(folder_path)
        #  Leave while loop, when folder is generated
        break
    except OSError as e:
        #  If OSError, which is not FileExist error
        if e.errno != os.errno.EEXIST:
            raise  # Raise error
        #  Pause for 0.1 second
        time.sleep(0.1)

# Open log file in writing mode
log_file = open(log_path, 'w')

#  Write system print statements to log file
sys.stdout = log_file

#  Write basic settings
print('GA Opt. log file (pyCity_resilience)')
print('##############################################################')
print()
print('Timestamp: ', timestamp)
print('City file name: ', city_name)
print()
print('use_scoop: ', use_scoop)
print('log_folder: ', log_folder)
print('path_city: ', path_city)
print()
print('objective: ', objective)
print('Risk. av. factor: ', risk_fac_av)
print('Risk. friendly factor: ', risk_fac_friendly)
print()
print('init_diverse: ', init_diverse)
if init_diverse:
    print('pop_name: ', pop_name)
print()
print('nb_ind: ', nb_ind)
print('ngen: ', ngen)
print('nb_runs: ', nb_runs)
print('size_hof: ', size_hof)
print('nb_min_gen: ', nb_min_gen)
print('std_break: ', std_break)
print('failure_tolerance: ', failure_tolerance)
print()
print('use_street: ', use_street)
print()
print('sampling_method: ', sampling_method)
print('load_city_n_build_samples: ', load_city_n_build_samples)
if load_city_n_build_samples:
    print('city_sample_name: ', city_sample_name)
    print('build_sample_name: ', build_sample_name)
    print('path_city_sample_dict: ', path_city_sample_dict)
    print('path_build_sample_dict: ', path_build_sample_dict)
print('load_sh_mc_res: ', load_sh_mc_res)
if load_sh_mc_res:
    print('path_mc_res_folder: ', path_mc_res_folder)
print('use_profile_pool: ', use_profile_pool)
if use_profile_pool:
    print('gen_use_prof_method: ', gen_use_prof_method)
    print('el_profile_dict: ', el_profile_dict)
    print('path_profile_dict: ', path_profile_dict)
print()
print('perform_checks: ', perform_checks)
print()
print('use_chp: ', use_chp)
print('use_lhn: ', use_lhn)
print('use_hp_aw: ', use_hp_aw)
print('use_hp_ww: ', use_hp_ww)
print('use_pv: ', use_pv)
print('use_bat: ', use_bat)
print('prevent_boi_hp: ', prevent_boi_hp)
print('prevent_chp_eh: ', prevent_chp_eh)
print('eeg_pv_limit: ', eeg_pv_limit)
print('use_kwkg_lhn_sub: ', use_kwkg_lhn_sub)
print('el_mix_for_chp: ', el_mix_for_chp)
print('el_mix_for_pv: ', el_mix_for_pv)
print('prevent_boi_lhn: ', prevent_boi_lhn)
print()
print('prob_cx: ', prob_cx)
print('nb_part_cx: ', nb_part_cx)
print('prob_mutation: ', prob_mutation)
print('prob_mut: ', prob_mut)
print('list_prob_lhn_and_esys: ', list_prob_lhn_and_esys)
print('list_prob_mute_type: ', list_prob_mute_type)
print('list_prob_lhn_gen_mut: ', list_prob_lhn_gen_mut)
print('prob_lhn: ', prob_lhn)
print()
print('pv_min: ', pv_min)
print('pv_step: ', pv_step)
print('add_pv_prop: ', add_pv_prop)
print('add_bat_prob: ', add_bat_prob)
print()
print('max_dist: ', max_dist)
print()
print('use_own_max_val: ', use_own_max_val)
print('boiler_max: ', boiler_max)
print('tes_max: ', tes_max)
print('chp_max: ', chp_max)
print('hp_aw_max: ', hp_aw_max)
print('hp_ww_max: ', hp_ww_max)
print('eh_max: ', eh_max)
print('bat_max: ', bat_max)
print()
for key in dict_restr.keys():
    print('key: ', key)
    print('Values: ', dict_restr[key])
    print()
print('list_options: ', list_options)
print('list_opt_prob: ', list_opt_prob)
print('list_lhn_opt: ', list_lhn_opt)
print('list_lhn_prob: ', list_lhn_prob)
print('list_lhn_to_stand_alone: ', list_lhn_to_stand_alone)

print('##############################################################')

#  Deactivate plotting to logfile
sys.stdout = sys.__stdout__

#  Initialize basic city object and mc runner
#  ####################################################################

#  Extract max. possible PV areas and add to dict
dict_max_pv_area = pvareas.get_dict_usable_pv_areas(city=city)

print()
print('Maximum usable PV areas per building in m2:')
for key in dict_max_pv_area.keys():
    print('Building id: ', key)
    print('Max. usable PV area in m2: ', dict_max_pv_area[key])

    if dict_max_pv_area[key] is None:
        msg = 'Max. PV area of building ' \
              + str(key) + ' is None. Thus, going to set it to zero!'
        dict_max_pv_area[key] = 0
    elif dict_max_pv_area[key] < 0:
        msg = 'Rooftop area of building ' \
              + str(key) + ' is negative! ' + str(dict_max_pv_area[key])
        raise AssertionError(msg)

#  Get dict with building positions
dict_pos = getpos.get_build_pos(city=city)

#  #######################################################################
#  Get dict with max. space heating power per building
dict_sh = getmaxsh.get_dict_max_sh_city(city=city)

print()
print('Maximum space heating power per building in Watt:')
for key in dict_sh.keys():
    print('Building id: ', key)
    print('Max. sh. power in kW: ', round(dict_sh[key])/1000)
print()

#  #######################################################################
#  Estimate design heat load for space heating AND hot water

build_standard = 'old'

print('Estimate design heat loads for space heating AND hot water per '
      'building, assuming ' + str(build_standard) + ' building standard.')

dict_heatloads = estdhl.calc_heat_load_per_building(
    city=city,
    build_standard=build_standard)

for key in dict_heatloads.keys():
    print('Building id: ', key)
    print('Design heat load (space heating AND hot water) in kW: ',
          round(dict_heatloads[key])/1000)
print()

#  #######################################################################
#  Add bes to all buildings, which do not have bes, yet
#  BES are necessary to run GA (enable/disable esys by setting them to True/
#  False on BES, even if object is constantly existent.
#  Boilers can be added, if city has no energy system, boilers are added to
#  prevent EnergySupplyException
addbes.add_bes_to_city(city=city, add_init_boi=add_init_boi)

del_existing_networks = True  # Delete existing LHN/DEGs
#  Necessary to prevent "blocking" of new LHNs by existing LHNs on city object
if del_existing_networks:
    #  Delete all existing energy networks (if some exist)
    delnet.del_energy_network_in_city(city=city)

# Initialize mc runner object and hand over initial city object
mc_run = runmc.init_base_mc_objects(city=city)

#  Perform initial sampling
if sampling_method == 'random':
    mc_run.perform_sampling(nb_runs=nb_runs, save_samples=True,
                            dem_unc=dem_unc)
    #  Save results toself._dict_samples_const = dict_samples_const
    #         self._dict_samples_esys = dict_samples_esys
elif sampling_method == 'lhc':
    mc_run.perform_lhc_sampling(nb_runs=nb_runs, save_res=True,
                                load_sh_mc_res=load_sh_mc_res,
                                path_mc_res_folder=path_mc_res_folder,
                                use_profile_pool=use_profile_pool,
                                gen_use_prof_method=gen_use_prof_method,
                                path_profile_dict=path_profile_dict,
                                load_city_n_build_samples=
                                load_city_n_build_samples,
                                path_city_sample_dict=path_city_sample_dict,
                                path_build_sample_dict=path_build_sample_dict,
                                dem_unc=dem_unc)

#  Initialize GA runner object
#  ####################################################################
ga_runner = GARunner(mc_runner=mc_run,
                     nb_runs=nb_runs,
                     failure_tolerance=failure_tolerance)

#  Perform reference mc run for rescaled boiler system (necessary to
#  use dimensionless quantifiers for fitnesses)
#  ###################################################################
if (objective == 'mc_dimless_eco_em_2d_mean'
        or objective == 'mc_dimless_eco_em_2d_risk_av'
        or objective == 'mc_dimless_eco_em_2d_risk_friendly'
        or objective == 'mc_dimless_eco_em_3d_mean'
        or objective == 'mc_dimless_eco_em_3d_risk_av'
        or objective == 'mc_dimless_eco_em_3d_risk_friendly'
        or objective == 'mc_dimless_eco_em_2d_std'
        or objective == 'mc_dimless_eco_em_3d_std'
):
    #  Perform reference system mc run (4x rescaled boiler)

    #  Copy city, only use boilers
    city_copy = copy.deepcopy(city)

    #  Add to copy of mc_runner --> Perform mc run
    addbes.gen_boiler_ref_scenario(city=city_copy)

    #  Copy mc_runner obj. of ga_runner
    mc_run_ref = copy.deepcopy(ga_runner.mc_runner)

    #  Replace city object with city_copy
    mc_run_ref._city_eco_calc.energy_balance.city = city_copy

    nb_runs = ga_runner.nb_runs

    #  Run MC analysis
    (dict_mc_res, dict_mc_setup, dict_mc_cov) = \
        mc_run_ref.perform_mc_runs(nb_runs=nb_runs,
                                   sampling_method=sampling_method,
                                   eeg_pv_limit=eeg_pv_limit,
                                   use_kwkg_lhn_sub=use_kwkg_lhn_sub,
                                   el_mix_for_chp=el_mix_for_chp,
                                   el_mix_for_pv=el_mix_for_pv,
                                   heating_off=heating_off
                                   )

    #  Save results to dict
    ga_runner._dict_mc_res_ref = dict_mc_res

    if len(dict_mc_setup['idx_failed_runs']) > 0:
        msg = 'Reference run (rescaled boilers) failed!'
        raise AssertionError(msg)

if (objective == 'ann_and_co2_dimless_ref'
        or objective == 'ann_and_co2_dimless_ref_3d'):
    #  Reference run for dimensionless annuity and co2

    #  Copy city, only use boilers
    city_copy = copy.deepcopy(city)

    #  Add to copy of mc_runner --> Perform mc run
    addbes.gen_boiler_ref_scenario(city=city_copy)

    #  Copy mc_runner obj. of ga_runner
    mc_run_ref = copy.deepcopy(ga_runner.mc_runner)

    #  Replace city object with city_copy
    mc_run_ref._city_eco_calc.energy_balance.city = city_copy

    #  Perform ref. run with ref. system (boiler rescaled)
    (ann_ref, co2_ref, sh_dem, el_dem, dhw_dem) =\
        mc_run_ref.perform_ref_run(eeg_pv_limit=eeg_pv_limit,
                                   use_kwkg_lhn_sub=use_kwkg_lhn_sub,
                                   chp_switch_pen=chp_switch_pen,
                                   max_switch=max_switch, obj='max',
                                   el_mix_for_chp=el_mix_for_chp,
                                   el_mix_for_pv=el_mix_for_pv
                                   )

    #  Save results to ga_runner
    if ann_ref != 0:
        ga_runner._ann_ref = ann_ref
    else:
        msg = 'Ref. annuity is zero!'
        raise AssertionError(msg)

    if co2_ref != 0:
        ga_runner._co2_ref = co2_ref
    else:
        msg = 'Ref. emissions are zero!'
        raise AssertionError(msg)

    print('Reference run annuity in Euro/a: ')
    print(round(ann_ref, 2))
    print('Reference emissions in kg/a: ')
    print(round(co2_ref, 2))

#  Create types
#  ####################################################################
#  Create fitness and individuum types
# if (objective == 'net_energy_related_to_ann_and_co2'
#     or objective == 'net_exergy_related_to_ann_and_co2'
#     or objective == 'net_energy_to_ann_and_co2_mean'
#     or objective == 'net_energy_to_ann_ref_run_test'):
#     #  Create fitness with two objectives (to be maximized)
#     creator.create("Fitness", base.Fitness, weights=(1.0, 1.0))
#     creator.create("Individual", dict, fitness=creator.Fitness)
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
        or objective == 'mc_dimless_eco_em_2d_std'):
    # Create fitness with two objectives (to be minimized)
    creator.create("Fitness", base.Fitness, weights=(-1.0, -1.0))
    creator.create("Individual", dict, fitness=creator.Fitness)

elif (objective == 'mc_dimless_eco_em_3d_mean'
      or objective == 'mc_dimless_eco_em_3d_risk_av'
      or objective == 'mc_dimless_eco_em_3d_risk_friendly'
      or objective == 'ann_and_co2_dimless_ref_3d'
      or objective == 'mc_dimless_eco_em_3d_std'):
    # Create fitness with three objectives (2 min. / 1 max.)
    creator.create("Fitness", base.Fitness, weights=(-1.0, -1.0, 1.0))
    creator.create("Individual", dict, fitness=creator.Fitness)

else:
    msg = 'Unknown objective chosen!'
    raise AssertionError(msg)

# Enable stats
#  ####################################################################
stats = tools.Statistics(key=lambda ind: ind.fitness.values)
stats.register("avg", np.mean, axis=0)
stats.register("std", np.std, axis=0)
stats.register("min", np.min, axis=0)
stats.register("max", np.max, axis=0)
logbook = tools.Logbook()

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
#  ####################################################################
# ga_runner_copy = copy.deepcopy(ga_runner)
toolbox.register('evaluate', eval.eval_obj,
                 ga_runner=ga_runner,
                 dict_restr=dict_restr,
                 objective=objective,
                 use_street=use_street,
                 eeg_pv_limit=eeg_pv_limit,
                 dict_max_pv_area=dict_max_pv_area,
                 dict_sh=dict_sh, pv_min=pv_min,
                 pv_step=pv_step, use_pv=use_pv,
                 add_pv_prop=add_pv_prop,
                 sampling_method=sampling_method,
                 use_kwkg_lhn_sub=use_kwkg_lhn_sub,
                 chp_switch_pen=chp_switch_pen,
                 max_switch=max_switch,
                 risk_fac_av=risk_fac_av,
                 risk_fac_friendly=risk_fac_friendly,
                 el_mix_for_chp=el_mix_for_chp,
                 el_mix_for_pv=el_mix_for_pv,
                 heating_off=heating_off,
                 prevent_boi_lhn=prevent_boi_lhn,
                 dict_heatloads=dict_heatloads
                 )

# # Test section
# bit = toolbox.parse_city_to_ind()
# ind = toolbox.individual()
# pop = toolbox.population(n=nb_ind)
#
# print("bit is of type %s and has value\n%s" % (type(bit), bit))
# print(
#     "ind is of type %s and contains %d bits\n%s" % (
#         type(ind), len(ind), ind))
# print("pop is of type %s and contains %d individuals\n%s" % (
#     type(pop), len(pop), pop))
# print()
# ind.fitness.values = toolbox.evaluate(individuum=ind,
#                                       ga_runner=ga_runner,
#                                       objective=objective)
# print(ind.fitness.valid)  # True
# print(ind.fitness)

# #  Add crossover function
# #  ####################################################################
# #  Register crossover function as mate
# toolbox.register("mate", cx.do_crossover,
#                  dict_max_pv_area=dict_max_pv_area)

toolbox.register('crossover', cx.cx_tournament, prob_cx=prob_cx,
                 nb_part=nb_part_cx, perform_checks=perform_checks,
                 dict_max_pv_area=dict_max_pv_area,
                 dict_restr=dict_restr, dict_sh=dict_sh,
                 pv_min=pv_min, pv_step=pv_step, use_pv=use_pv,
                 add_pv_prop=add_pv_prop,
                 prevent_boi_lhn=prevent_boi_lhn,
                 dict_heatloads=dict_heatloads
                 )

#  Add mutation function
#  ####################################################################
#  Register mutation function as mutate
toolbox.register('mutate', muta.do_mutate,
                 prob_mut=prob_mut,
                 prob_lhn=prob_lhn,
                 dict_restr=dict_restr,
                 dict_max_pv_area=dict_max_pv_area,
                 pv_min=pv_min,
                 dict_pos=dict_pos,
                 list_prob_lhn_and_esys=list_prob_lhn_and_esys,
                 list_prob_mute_type=list_prob_mute_type,
                 list_prob_lhn_gen_mut=list_prob_lhn_gen_mut,
                 max_dist=max_dist, perform_checks=perform_checks,
                 use_bat=use_bat, use_pv=use_pv,
                 use_lhn=use_lhn,
                 list_options=list_options,
                 list_opt_prob=list_opt_prob,
                 list_lhn_opt=list_lhn_opt,
                 list_lhn_prob=list_lhn_prob,
                 list_lhn_to_stand_alone=list_lhn_to_stand_alone,
                 dict_sh=dict_sh,
                 pv_step=pv_step,
                 add_pv_prop=add_pv_prop,
                 add_bat_prob=add_bat_prob,
                 prevent_boi_lhn=prevent_boi_lhn,
                 dict_heatloads=dict_heatloads)

#  Add selection function
#  ####################################################################
#  Register selection function function as select
toolbox.register("select", selec.do_selection, objective=objective)

if __name__ == '__main__':

    if use_scoop:
        toolbox.register("map", futures.map)

        print('Start multiprocessing using SCOOP')

    else:
        #  Use multiprocessing
        pool = multiprocessing.Pool(processes=nb_processes)

        #  Enable multiprocessing usage
        toolbox.register("map", pool.map)

        print('Start GA run with Python multiprocessing package and '
              + str(nb_processes) + ' number of processes.')
        print('#############################################################')
        print()

    # ####################################################################

    time_start = time.time()

    #  initialize halloffame to store best individuums
    halloffame = tools.HallOfFame(size_hof)

    print('Initialze population')
    print('#######################################################')

    #  Generate population
    #  # Generate diverse initial population
    if init_diverse:
        pop = pickle.load(open(path_pop, mode='rb'))

        if len(pop) != nb_ind:
            msg = 'Population length ' \
                  + str(len(pop)) + ' is different from number of desired ' \
                                    'individuals ' + str(nb_ind) + '!'
            raise AssertionError(msg)
    else:
        #  # Generate population with same individuals
        pop = toolbox.population(n=nb_ind)

    # Evaluate fitnesses of start population
    print('Evaluate initial population')
    fitnesses = toolbox.map(toolbox.evaluate, pop)

    #  Save fitness values to each individuum
    for ind, fit in zip(pop, fitnesses):
        ind.fitness.values = fit

    # Write system print statements to log file
    sys.stdout = log_file

    print('Evaluated %i individuals' % len(pop))

    print('Initial Population:')
    for i in pop:
        print('Individuum: ', i)
        print('Fitness: ', i.fitness.values)
    print()

    # Initial offspring is created by cloning
    selected = list(map(toolbox.clone, pop))

    #  Dummy value
    parents = None
    list_ind = None

    for g in range(ngen):
        print('Generation ', g)
        print('#######################################################')

        # Select the next generations individuals from parents + offspring
        if g != 0:
            selected = toolbox.select(parents=parents, invalid_ind=list_ind,
                                      nb_ind=nb_ind,
                                      objective=objective)

        # Clone selected individuals
        parents = list(map(toolbox.clone, selected))
        newoffspring = list(map(toolbox.clone, selected))

        #  Replace population with new offspring
        pop[:] = parents

        #  Store population to stats
        record = stats.compile(pop)

        print('Population of generation ', g, ':')
        for i in pop:
            print(i, 'fitness: ', i.fitness.values)

        # Deactivate plotting to logfile
        sys.stdout = sys.__stdout__

        #  Perform evolution (crossover)
        offspring = toolbox. \
            crossover(newoffspring,
                      prob_cx=prob_cx,
                      dict_max_pv_area=dict_max_pv_area,
                      nb_part=nb_part_cx)

        #  Perform evolution (mutation)
        new_offspring = []
        for ind_mut in offspring:
            if random.random() < prob_mutation:
                ind_mut = toolbox.mutate(ind_mut)
                del ind_mut.fitness.values
            new_offspring.append(ind_mut)
        # Overwrite offspring
        offspring = new_offspring

        #  Write system print statements to log file
        sys.stdout = log_file

        print('Offspring after crossover and mutation call:')
        for ind_off in offspring:
            print(str(ind_off))
            print('Fitness: ' + str(ind_off.fitness.values))
        print()

        # Deactivate plotting to logfile
        sys.stdout = sys.__stdout__

        #  Evaluate all mutated individuals to add new fitness value
        #  ###############################################################
        list_ind_temp = [ind for ind in offspring if not ind.fitness.valid]

        #  Check if individuum is already in parent generation
        list_ind = [ind for ind in list_ind_temp if ind not in parents]

        #  Evaluate fitness values for list of
        fitnesses = toolbox.map(toolbox.evaluate, list_ind)

        #  Write system print statements to log file
        sys.stdout = log_file

        #  Save new fitness values to individuums
        for ind, fit in zip(list_ind, fitnesses):
            print('Mutated/crossovered individuum: ', ind)
            print('Fitness values: ', fit)
            print()
            ind.fitness.values = fit

        # Deactivate plotting to logfile
        sys.stdout = sys.__stdout__

        # Update the hall of fame by the best individuals from offspring
        halloffame.update(pop)

        #  Store the record to the logbook
        logbook.record(gen=0, evals=30, **record)

        #  Save population as pickle file
        if save_pop:
            name_pop = 'population_' + str(g) + '.pkl'
            path_pop = os.path.join(workspace, 'output', 'ga_opt', log_folder,
                                    name_pop)
            pickle.dump(pop, open(path_pop, mode='wb'))

        #  Check if minimum number of generations has been processed to 
        #  check if GA execution can terminate
        if g > nb_min_gen:

            obj_0 = np.zeros(nb_min_gen)
            obj_1 = np.zeros(nb_min_gen)

            count = 0
            #  Get lat nb_min_gen number of results out of logbook
            for n in range(len(logbook) - 1 - nb_min_gen,
                           len(logbook) - 1):
                obj_0[count] = logbook[n]["max"][0]
                obj_1[count] = logbook[n]["max"][1]
                count += 1

            # Calculate standard deviations
            std_dev0 = np.std(obj_0)
            std_dev1 = np.std(obj_1)

            ref_obj_0 = obj_0[0]
            ref_obj_1 = obj_1[0]

            #  If both std are below std_break, exit iteration
            if (std_dev0 < std_break * ref_obj_0
                    and std_dev1 < std_break * ref_obj_1):
                #  Write system print statements to log file
                sys.stdout = log_file
                print('Stop iteration, as standard deviation over the last'
                      + str(nb_min_gen) + ' generations is smaller than  '
                      + str(std_break) + ' % of fitness values '
                      + str(ref_obj_0) + ' and '
                      + str(ref_obj_1))
                break

    # Write system print statements to log file
    sys.stdout = log_file

    # print the hall of fame
    print('Hall of fame: ')
    for i in range(len(halloffame)):
        print(halloffame[i], 'fitness:', halloffame[i].fitness.values)
    print()

    # print the final population
    print('Final Population: ', pop)
    print()

    #  Get pareto frontier results (first/best pareto frontier)
    list_pareto_frontier = tools.sortNondominated(pop, len(pop),
                                                  first_front_only=True)

    #  Add pareto frontier results to logfile
    print('Best/last pareto frontier results:')
    for ind_par in list_pareto_frontier[0]:
        print(ind_par)
        print('Fitness: ', ind_par.fitness.values)
    print()

    # print the logbook
    print('Logbook: ')
    for i in logbook:
        print(i)
    print()

    #  Pickle and save logbook
    pickle.dump(logbook, open(path_logbook, mode='wb'))
    print()

    time_stop = time.time()

    print('Required runtime for execution in hours: ')
    print(round((time_stop - time_start) / 3600), 2)

    # Deactivate plotting to logfile
    sys.stdout = sys.__stdout__

    print('Finished GA optimization')
    print()

    print('Required runtime for execution in hours: ')
    print(round((time_stop - time_start) / 3600), 2)
