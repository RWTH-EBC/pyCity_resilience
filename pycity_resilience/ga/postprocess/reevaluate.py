#!/usr/bin/env python
# coding=utf-8
"""
Perform reevaluation of fitness of specific populuation and individuum or
city object with energy system
"""
from __future__ import division

import os
import pickle
import warnings
import numpy as np
import matplotlib.pyplot as plt

try:
    from matplotlib2tikz import save as tikz_save
except:
    msg = 'Could not import matplotlib2tikz'
    warnings.warn(msg)

import pycity_calc.toolbox.dimensioning.dim_functions as dimfunc
import pycity_calc.simulation.energy_balance.city_eb_calc as citeb
import pycity_calc.economic.annuity_calculation as annu
import pycity_calc.economic.city_economic_calc as citecon
import pycity_calc.toolbox.mc_helpers.mc_runner as mcrun
import pycity_calc.visualization.city_visual as citvis

import pycity_resilience.ga.parser.parse_ind_to_city as parseindcit
import pycity_resilience.ga.preprocess.add_bes as addbes
import pycity_resilience.monte_carlo.run_mc as runmc
import pycity_resilience.ga.opt_ga as optga
import pycity_resilience.ga.evolution.helpers.mod_esys_prob as modprob
import pycity_resilience.ga.postprocess.analyze_generation_dev as andev

import pycity_resilience.ga.opt_ga  # Necessary to load pickle files!
from deap import base, creator, tools, algorithms


def reevaluate_ind(city_esys, nb_runs,
                   sampling_method,
                   do_sampling=True,
                   failure_tolerance=0.05,
                   prevent_printing=False,
                   heating_off=True,
                   load_sh_mc_res=False,
                   path_mc_res_folder=None,
                   use_profile_pool=False,
                   gen_use_prof_method=0,
                   path_profile_dict=None,
                   random_profile=False,
                   load_city_n_build_samples=False,
                   path_city_sample_dict=None,
                   path_build_sample_dict=None,
                   eeg_pv_limit=False,
                   use_kwkg_lhn_sub=False,
                   calc_th_el_cov=False,
                   dem_unc=True,
                   el_mix_for_chp=True,
                   el_mix_for_pv=True):
    """
    Reevaluate solution by running economic and ecologic Monte Carlo
    uncertainty analysis

    Parameters
    ----------
    ind : object
        Individual of GA run (holding energy system solution)
    city_esys : object
        City object of pyCity_calc (should have energy system!)
    nb_runs : int
        Number of Monte-Carlo loops
    sampling_method : str
        Defines method used for sampling.
        Options:
        - 'lhc': latin hypercube sampling
        - 'random': randomized sampling
    do_sampling : bool, optional
        Defines, if sampling should be performed/samples should be loaded from
         path (default: True). Else: Use existing sample data on mc_runner.py
         object
    failure_tolerance : float, optional
        Allowed EnergyBalanceException failure tolerance (default: 0.05).
        E.g. 0.05 means, that 5% of runs are allowed to fail with
        EnergyBalanceException.
    prevent_printing : bool, optional
        Defines, if printing statements should be suppressed
    heating_off : bool, optional
        Defines, if sampling to deactivate heating during summer should
        be used (default: True)
    load_sh_mc_res : bool, optional
        If True, tries to load space heating monte-carlo uncertainty run
        results for each building and uses result to sample space heating
        values. If False, uses default distribution to sample space heating
        values (default: False)
    path_mc_res_folder : str, optional
        Path to folder, where sh mc run results are stored (default: None).
        Only necessary if load_sh_mc_res is True
    use_profile_pool : bool, optional
        Defines, if user/el. load/dhw profile pool should be generated
        (default: False). If True, generates profile pool.
    gen_use_prof_method : int, optional
        Defines method for el. profile pool usage (default: 0).
        Options:
        - 0: Generate new el. profile pool
        - 1: Load profile pool from path_profile_dict
    path_profile_dict : str, optional
        Path to dict with el. profile pool (default: None).
    random_profile : bool, optional
        Defines, if random samples should be used from profile pool
        (default: False). Only relevant, if profile pool has been given,
        sampling_method == 'lhc' and nb. of profiles is equal to nb.
        of samples
    load_city_n_build_samples : bool, optional
        Defines, if existing city and building sample dicts should be
        loaded (default: False). If False, generates new sample dicts.
    path_city_sample_dict : str, optional
        Defines path to city sample dict (default: None). Only relevant,
        if load_city_n_build_samples is True
    path_build_sample_dict : str, optional
        Defines path to building sample dict (default: None). Only relevant,
        if load_city_n_build_samples is True
    eeg_pv_limit : bool, optional
        Defines, if EEG PV feed-in limitation of 70 % of peak load is
        active (default: False). If limitation is active, maximal 70 %
        of PV peak load are fed into the grid.
        However, self-consumption is used, first.
    use_kwkg_lhn_sub : bool, optional
        Defines, if KWKG LHN subsidies are used (default: True).
        If True, can get 100 Euro/m as subdidy, if share of CHP LHN fed-in
        is equal to or higher than 60 %
    calc_th_el_cov : bool, optional
        Defines, if thermal and electric coverage of different types of
        devices should be calculated (default: False)
    dem_unc : bool, optional
        Defines, if thermal, el. and dhw demand are assumed to be uncertain
        (default: True). If True, samples demands. If False, uses reference
        demands.
    el_mix_for_chp : bool, optional
        Defines, if el. mix should be used for CHP fed-in electricity
        (default: True). If False, uses specific fed-in CHP factor,
        defined in co2emissions object (co2_factor_el_feed_in)
    el_mix_for_pv : bool, optional
        Defines, if el. mix should be used for PV fed-in electricity
        (default: True). If False, uses specific fed-in PV factor,
        defined in co2emissions object (co2_factor_pv_fed_in)

    Returns
    -------
    tuple_res : tuple (of dicts)
        Tuple holding five dictionaries
        For sampling_method == 'random':
        (dict_samples_const, dict_samples_esys, dict_mc_res, dict_mc_setup,
        None)
        dict_samples_const : dict (of dicts)
            Dictionary holding dictionaries with constant
            sample data for MC run
            dict_samples_const['city'] = dict_city_samples
            dict_samples_const['<building_id>'] = dict_build_dem
            (of building with id <building_id>)
        dict_samples_esys : dict (of dicts)
            Dictionary holding dictionaries with energy system sampling
            data for MC run
            dict_samples_esys['<building_id>'] = dict_esys
            (of building with id <building_id>)
        dict_mc_res : dict
            Dictionary with result arrays for each run
            dict_mc_res['annuity'] = array_annuity
            dict_mc_res['co2'] = array_co2
            dict_mc_res['sh_dem'] = array_net_sh
            dict_mc_res['el_dem'] = array_net_el
            dict_mc_res['dhw_dem'] = array_net_dhw
            dict_mc_res['gas_boiler'] = array_gas_boiler
            dict_mc_res['gas_chp'] = array_gas_chp
            dict_mc_res['grid_imp_dem'] = array_grid_imp_dem
            dict_mc_res['grid_imp_hp'] = array_grid_imp_hp
            dict_mc_res['grid_imp_eh'] = array_grid_imp_eh
            dict_mc_res['lhn_pump'] = array_lhn_pump
            dict_mc_res['grid_exp_chp'] = array_grid_exp_chp
            dict_mc_res['grid_exp_pv'] = array_grid_exp_pv
        dict_mc_setup : dict
            Dictionary holding mc run settings
            dict_mc_setup['nb_runs'] = nb_runs
            dict_mc_setup['failure_tolerance'] = failure_tolerance
            dict_mc_setup['heating_off'] = heating_off
            dict_mc_setup['idx_failed_runs'] = self._list_failed_runs
        dict_mc_cov : dict
            Dictionary holding thermal/electrical coverage factors
            dict_mc_cov['th_cov_boi'] = array_th_cov_boi
            dict_mc_cov['th_cov_chp'] = array_th_cov_chp
            dict_mc_cov['th_cov_hp_aw'] = array_th_cov_hp_aw
            dict_mc_cov['th_cov_hp_ww'] = array_th_cov_hp_ww
            dict_mc_cov['th_cov_eh'] = array_th_cov_eh
            dict_mc_cov['el_cov_chp'] = array_el_cov_chp
            dict_mc_cov['el_cov_pv'] = array_el_cov_pv
            dict_mc_cov['el_cov_grid']

        For sampling_method == 'lhc':
        (dict_city_sample_lhc, dict_build_samples_lhc, dict_mc_res,
                dict_mc_setup, dict_profiles_lhc)
        dict_city_sample_lhc : dict
            Dict holding city parameter names as keys and numpy arrays with
            samples as dict values
        dict_build_samples_lhc : dict
            Dict. holding building ids as keys and dict of samples as
            values.
            These dicts hold paramter names as keys and numpy arrays with
            samples as dict values
        dict_mc_res : dict
            Dictionary with result arrays for each run
            dict_mc_res['annuity'] = array_annuity
            dict_mc_res['co2'] = array_co2
            dict_mc_res['sh_dem'] = array_net_sh
            dict_mc_res['el_dem'] = array_net_el
            dict_mc_res['dhw_dem'] = array_net_dhw
            dict_mc_res['gas_boiler'] = array_gas_boiler
            dict_mc_res['gas_chp'] = array_gas_chp
            dict_mc_res['grid_imp_dem'] = array_grid_imp_dem
            dict_mc_res['grid_imp_hp'] = array_grid_imp_hp
            dict_mc_res['grid_imp_eh'] = array_grid_imp_eh
            dict_mc_res['lhn_pump'] = array_lhn_pump
            dict_mc_res['grid_exp_chp'] = array_grid_exp_chp
            dict_mc_res['grid_exp_pv'] = array_grid_exp_pv
        dict_mc_setup : dict
            Dictionary holding mc run settings
            dict_mc_setup['nb_runs'] = nb_runs
            dict_mc_setup['failure_tolerance'] = failure_tolerance
            dict_mc_setup['heating_off'] = heating_off
            dict_mc_setup['idx_failed_runs'] = self._list_failed_runs
        dict_profiles_lhc : dict
            Dict. holding building ids as keys and dict with numpy arrays
            with different el. and dhw profiles for each building as value
            fict_profiles_build['el_profiles'] = el_profiles
            dict_profiles_build['dhw_profiles'] = dhw_profiles
            When use_profile_pool is False, dict_profiles is None
        dict_mc_cov : dict
            Dictionary holding thermal/electrical coverage factors
            dict_mc_cov['th_cov_boi'] = array_th_cov_boi
            dict_mc_cov['th_cov_chp'] = array_th_cov_chp
            dict_mc_cov['th_cov_hp_aw'] = array_th_cov_hp_aw
            dict_mc_cov['th_cov_hp_ww'] = array_th_cov_hp_ww
            dict_mc_cov['th_cov_eh'] = array_th_cov_eh
            dict_mc_cov['el_cov_chp'] = array_el_cov_chp
            dict_mc_cov['el_cov_pv'] = array_el_cov_pv
            dict_mc_cov['el_cov_grid']
    """

    #  Reevaluate fitness
    annuity_obj = annu.EconomicCalculation()
    energy_balance = citeb.CityEBCalculator(city=city_esys)
    city_eco_calc = citecon.CityAnnuityCalc(annuity_obj=annuity_obj,
                                            energy_balance=energy_balance)

    if nb_runs == 1:
        (total_annuity, co2) = city_eco_calc. \
            perform_overall_energy_balance_and_economic_calc(eeg_pv_limit=
                                                             eeg_pv_limit,
                                                             el_mix_for_chp=el_mix_for_chp,
                                                             el_mix_for_pv=el_mix_for_pv
                                                             )

        print('Total annuity in Euro/a: ')
        print(total_annuity)
        print()
        print('Total emissions in kg/a: ')
        print(co2)
        print()
        return (total_annuity, co2)

    #  Hand over initial city object to mc_runner
    mc_run = mcrun.McRunner(city_eco_calc=city_eco_calc)

    #  Perform Monte-Carlo uncertainty analysis
    #  #####################################################################
    (dict_samples_const, dict_samples_esys, dict_res, dict_mc_setup,
     dict_profiles_lhc, dict_mc_cov) = \
        mc_run.run_mc_analysis(nb_runs=nb_runs,
                               failure_tolerance=failure_tolerance,
                               do_sampling=do_sampling,
                               prevent_printing=prevent_printing,
                               heating_off=heating_off,
                               sampling_method=sampling_method,
                               load_sh_mc_res=load_sh_mc_res,
                               path_mc_res_folder=path_mc_res_folder,
                               use_profile_pool=use_profile_pool,
                               gen_use_prof_method=gen_use_prof_method,
                               path_profile_dict=path_profile_dict,
                               random_profile=random_profile,
                               load_city_n_build_samples=
                               load_city_n_build_samples,
                               path_city_sample_dict=path_city_sample_dict,
                               path_build_sample_dict=path_build_sample_dict,
                               eeg_pv_limit=eeg_pv_limit,
                               use_kwkg_lhn_sub=use_kwkg_lhn_sub,
                               calc_th_el_cov=calc_th_el_cov,
                               dem_unc=dem_unc,
                               el_mix_for_chp=el_mix_for_chp,
                               el_mix_for_pv=el_mix_for_pv
                               )

    return (dict_samples_const, dict_samples_esys, dict_res, dict_mc_setup,
            dict_profiles_lhc, dict_mc_cov)


def main():
    #  Define pathes
    #  ####################################################################
    this_path = os.path.dirname(os.path.abspath(__file__))
    src_path = os.path.dirname(os.path.dirname(os.path.dirname(this_path)))
    workspace = os.path.join(src_path, 'workspace')

    #  Define path to results folder (holding pickled population files)
    name_res_folder = 'ga_run_dyn_co2_ref_2'
    path_results_folder = os.path.join(workspace,
                                       'output',
                                       'ga_opt',
                                       name_res_folder)

    plot_configs = True
    # plot_configs : bool, optional
    #     Defines, if configurations should be plotted (default: False)

    plot_pareto = True
    #  Defines, if pareto frontier with solution numbers should be plotted

    #  Select individuum number of final population (to be evaluated)
    ind_nb = 1
    #  Select individual by index (ind_nb - 1)

    #  Number of desired individuums
    nb_runs = 100
    failure_tolerance = 1

    do_sampling = True  # Perform initial sampling/load existing sample dicts
    #  If False, use existing sample data on mc_runner object
    sampling_method = 'lhc'

    dem_unc = True
    # dem_unc : bool, optional
    # 	Defines, if thermal, el. and dhw demand are assumed to be uncertain
    # 	(default: True). If True, samples demands. If False, uses reference
    # 	demands.

    heating_off = True
    #  Defines, if heating can be switched of during summer

    #  Suppress print and warnings statements during MC-run
    prevent_printing = False

    #  #############################################

    eeg_pv_limit = True  # Only relevant if evaluate_pop = True

    use_kwkg_lhn_sub = False  # Use KWKG subsidies for LHN

    calc_th_el_cov = True  # Calculate thermal and electric coverage factors

    el_mix_for_chp = False  # Use el. mix for CHP fed-in electricity
    el_mix_for_pv = False  # Use el. mix for PV fed-in electricity

    #  Defines, if pre-generated sample file should be loaded
    #  ##############################

    load_city_n_build_samples = True
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
    load_sh_mc_res = True

    #  Path to FOLDER with mc sh results (searches for corresponding building ids)
    path_mc_res_folder = os.path.join(workspace,
                                      'mc_sh_results')

    #  Generate el. and dhw profile pool to sample from (time consuming)
    use_profile_pool = True
    #  Only relevant, if sampling_method == 'lhc'
    random_profile = False
    #  Defines, if random samples should be used from profiles. If False,
    #  loops over given profiles (if enough profiles exist).

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

    #  Special options
    #  ################
    resc_boilers = False
    #  If resc_boilers is True, rescale boiler sizes with resc_factor
    resc_factor = 1

    #  Name city object
    #  ############################################
    city_name = 'aachen_kronenberg_6.pkl'

    #  Pathes
    #  ################################################################
    path_city = os.path.join(workspace, 'city_objects',
                             # 'with_esys',
                             'no_esys',
                             city_name)

    outfolder = city_name[:-4] + '_reeval_ind_' + str(ind_nb)
    # outfolder = city_name[:-4] + '_ref_boi_2_resc'
    if resc_boilers:
        outfolder = city_name[:-4] + '_reeval_ind_' + str(ind_nb) + '_resc'

    path_city_out = os.path.join(workspace, 'output', 'reevaluate',
                            str(city_name[:-4])
                                 )
    path_out = os.path.join(path_city_out,
                            outfolder)

    if not os.path.exists(path_out):
        os.makedirs(path_out)

    #  Path to save results dict
    res_name = 'mc_run_results_dict.pkl'
    path_res = os.path.join(path_out, res_name)

    #  Path to sampling dict const
    sample_name_const = 'mc_run_sample_dict_const.pkl'
    path_sample_const = os.path.join(path_out, sample_name_const)

    #  Path to sampling dict esys
    sample_name_esys = 'mc_run_sample_dict_esys.pkl'
    path_sample_esys = os.path.join(path_out, sample_name_esys)

    #  Path to save mc settings to
    setup_name = 'mc_run_setup_dict.pkl'
    path_setup = os.path.join(path_out, setup_name)

    profiles_name = 'mc_run_profile_pool_dict.pkl'
    path_profiles = os.path.join(path_out, profiles_name)

    cov_dict_name = 'mc_cov_dict.pkl'
    path_mc_cov = os.path.join(path_out, cov_dict_name)

    #  Path to save figures to. Only relevant, if plot_configs is True
    path_save_fig = os.path.join(path_out, 'figure')

    path_log_file = os.path.join(path_out, 'log_failed_runs.txt')

    file_par_front = str(city_name[:-4]) + '_pareto_front.pkl'
    path_par_front = os.path.join(path_city_out, file_par_front)

    city_out_name = 'city_with_esys_ind_' + str(ind_nb) + '.pkl'
    if resc_boilers:
        city_out_name = 'city_with_esys_ind_ref_boi_2_resc.pkl'
    path_city_obj_out = os.path.join(path_out, city_out_name)


    #  ####################################################################

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

    #  ####################################################################

    #  Add bes to all buildings, which do not have bes, yet
    #  Moreover, add initial boiler systems to overwrite existing esys combis
    addbes.add_bes_to_city(city=city, add_init_boi=True)

    #  TODO: Erase, as part has no effect
    # #  Initialize mc runner object and hand over initial city object
    # mc_run = runmc.init_base_mc_objects(city=city)
    #
    # #  Perform initial sampling
    # if sampling_method == 'random':
    #     mc_run.perform_sampling(nb_runs=nb_runs, save_samples=True,
    #                             dem_unc=dem_unc)
    #     #  Save results toself._dict_samples_const = dict_samples_const
    #     #         self._dict_samples_esys = dict_samples_esys
    #
    # elif sampling_method == 'lhc':
    #     mc_run.perform_lhc_sampling(nb_runs=nb_runs, save_res=True,
    #                                 load_sh_mc_res=load_sh_mc_res,
    #                                 path_mc_res_folder=path_mc_res_folder,
    #                                 use_profile_pool=use_profile_pool,
    #                                 gen_use_prof_method=gen_use_prof_method,
    #                                 path_profile_dict=path_profile_dict,
    #                                 load_city_n_build_samples=
    #                                 load_city_n_build_samples,
    #                                 path_city_sample_dict=path_city_sample_dict,
    #                                 path_build_sample_dict=path_build_sample_dict,
    #                                 dem_unc=dem_unc
    #                                 )

    #  Get pickled population result files
    #  ##################################################################
    #  Load results (all pickled population objects into dict)
    dict_gen = andev.load_res(dir=path_results_folder)

    # #  Extract final population
    # (final_pop, list_ann, list_co2) = andev.get_final_pop(dict_gen=dict_gen)
    #
    # #  Extract list of pareto optimal results
    # list_inds_pareto = andev.get_par_front_list_of_final_pop(final_pop)

    try:
        dict_pareto_sol = pickle.load(open(path_par_front, mode='rb'))
    except:
        msg = 'Could not load file from ' + str(path_par_front)
        warnings.warn(msg)
        #  Extract list of pareto optimal results
        list_inds_pareto = andev.get_pareto_front(dict_gen=dict_gen,
                                                  size_used=None,  # Nb. Gen.
                                                  nb_ind_used=400)  # Nb. ind.
        #  Parse list of pareto solutions to dict (nb. as keys to re-identify
        #  each solution
        dict_pareto_sol = {}
        for i in range(len(list_inds_pareto)):
            dict_pareto_sol[int(i + 1)] = list_inds_pareto[i]

        #  Save pareto-frontier solution
        pickle.dump(dict_pareto_sol, open(path_par_front, mode='wb'))

    #  Extract list of pareto solutions
    list_inds_pareto = []
    for key in dict_pareto_sol.keys():
        list_inds_pareto.append(dict_pareto_sol[key])

    if plot_pareto:
        #  Print pareto front and energy system configurations
        andev.get_esys_pareto_info(list_pareto_sol=list_inds_pareto)

    #  Extract selected individuum with ind_nb info
    ind_sel = list_inds_pareto[ind_nb - 1]

    # #  ###################################
    # #  Erase pv to generate ref. scenario
    # for id in ind_sel.keys():
    #     if id != 'lhn':
    #         for esys in ind_sel[id].keys():
    #             if esys == 'pv':
    #                 ind_sel[id][esys] = 0
    #
    # for id in ind_sel.keys():
    #     if id != 'lhn':
    #         curr_build = city.nodes[id]['entity']
    #
    #         q_dot_th_max = \
    #             dimfunc.get_max_power_of_building(building=curr_build,
    #                                               get_therm=True,
    #                                               with_dhw=True)
    #
    #         ind_sel[id]['boi'] = 2 * q_dot_th_max
    # #  ###################################

    #  ############################################
    #  Rescale boilers
    if resc_boilers:

        print('Rescale boiler sizes.')
        print('resc_factor boiler: ')
        print(resc_factor)

        for id in ind_sel.keys():
            if id != 'lhn':
                for esys in ind_sel[id].keys():
                    if esys == 'boi':
                        print('Boiler size of building ' + str(id) + ' in kW:')
                        print(ind_sel[id][esys])
                        ind_sel[id][esys] *= resc_factor
                        print('New size (rescaled):')
                        print(ind_sel[id][esys])
                        print()
    #  ############################################

    print('#################################################################')
    print('Selected individual by user: ', ind_nb)
    print(ind_sel)
    print('#################################################################')
    print()

    #  Use parser
    #  Generate city with ind object
    city_esys = parseindcit.parse_ind_dict_to_city(dict_ind=ind_sel,
                                                   city=city)

    if nb_runs == 1:  #  Return single objective values
        (total_annuity, co2) = \
            reevaluate_ind(city_esys=city_esys,
                           nb_runs=nb_runs,
                           sampling_method=sampling_method,
                           do_sampling=do_sampling,
                           failure_tolerance=failure_tolerance,
                           prevent_printing=prevent_printing,
                           heating_off=heating_off,
                           load_sh_mc_res=load_sh_mc_res,
                           path_mc_res_folder=path_mc_res_folder,
                           use_profile_pool=use_profile_pool,
                           gen_use_prof_method=gen_use_prof_method,
                           path_profile_dict=path_profile_dict,
                           random_profile=random_profile,
                           load_city_n_build_samples=load_city_n_build_samples,
                           path_city_sample_dict=path_city_sample_dict,
                           path_build_sample_dict=path_build_sample_dict,
                           eeg_pv_limit=eeg_pv_limit,
                           use_kwkg_lhn_sub=use_kwkg_lhn_sub,
                           calc_th_el_cov=calc_th_el_cov,
                           dem_unc=dem_unc,
                           el_mix_for_chp=el_mix_for_chp,
                           el_mix_for_pv=el_mix_for_pv
                           )
        print('Annuity in Euro/a: ', total_annuity)
        print('Emissions in kg/a: ', co2)
        print()

    else:  # Perform Monte-Carlo economic and ecologic uncertainty analysis
        #  Run reevaluation
        (dict_samples_const, dict_samples_esys, dict_res, dict_mc_setup,
         dict_profiles_lhc, dict_mc_cov) = \
            reevaluate_ind(city_esys=city_esys,
                           nb_runs=nb_runs,
                           sampling_method=sampling_method,
                           do_sampling=do_sampling,
                           failure_tolerance=failure_tolerance,
                           prevent_printing=prevent_printing,
                           heating_off=heating_off,
                           load_sh_mc_res=load_sh_mc_res,
                           path_mc_res_folder=path_mc_res_folder,
                           use_profile_pool=use_profile_pool,
                           gen_use_prof_method=gen_use_prof_method,
                           path_profile_dict=path_profile_dict,
                           random_profile=random_profile,
                           load_city_n_build_samples=load_city_n_build_samples,
                           path_city_sample_dict=path_city_sample_dict,
                           path_build_sample_dict=path_build_sample_dict,
                           eeg_pv_limit=eeg_pv_limit,
                           use_kwkg_lhn_sub=use_kwkg_lhn_sub,
                           calc_th_el_cov=calc_th_el_cov,
                           dem_unc=dem_unc,
                           el_mix_for_chp=el_mix_for_chp,
                           el_mix_for_pv=el_mix_for_pv
                           )

        #  ###################################################################
        pickle.dump(dict_res, open(path_res, mode='wb'))
        print('Saved results dict to: ', path_res)
        print()

        pickle.dump(dict_samples_const, open(path_sample_const, mode='wb'))
        print('Saved sample dict to: ', path_sample_const)
        print()

        pickle.dump(dict_samples_esys, open(path_sample_esys, mode='wb'))
        print('Saved sample dict to: ', path_sample_esys)
        print()

        pickle.dump(dict_mc_setup, open(path_setup, mode='wb'))
        print('Saved mc settings dict to: ', path_setup)
        print()

        if dict_profiles_lhc is not None:
            pickle.dump(dict_profiles_lhc, open(path_profiles, mode='wb'))
            print('Saved profiles dict to: ', path_profiles)
            print()

        if calc_th_el_cov and dict_mc_cov is not None:
            pickle.dump(dict_mc_cov, open(path_mc_cov, mode='wb'))
            print('Saved dict_mc_cov to: ', path_mc_cov)
            print()

        nb_failed_runs = len(dict_mc_setup['idx_failed_runs'])
        print('Nb. failed runs: ', str(nb_failed_runs))
        print()

        list_idx_failed = dict_mc_setup['idx_failed_runs']
        print('Indexes of failed runs: ', str(list_idx_failed))
        print()

        with open(path_log_file, mode='w') as logfile:
            logfile.write('Nb. failed runs: ' + str(nb_failed_runs))
            logfile.write('\nIndexes of failed runs: ' + str(list_idx_failed))

            print('Nb. failed runs: ' + str(nb_failed_runs))
            print('Indexes of failed runs: ' + str(list_idx_failed))

    #  Save city object with esys config
    pickle.dump(city_esys, open(path_city_obj_out, mode='wb'))

    if plot_configs:
        #  Generate figure path
        if not os.path.isdir(path_save_fig):
            os.makedirs(path_save_fig)

        #  Plot and save energy system configuration
        #  You might need to manually adjust input settings, depending
        #  on your city object (such as plot_str_dist or offset)
        citvis.plot_city_district(city=city_esys,
                                  plot_lhn=True,
                                  plot_deg=True,
                                  plot_esys=True,
                                  font_size=11,
                                  save_plot=True,
                                  save_path=path_save_fig,
                                  plot_str_dist=60,
                                  offset=10)

        #  Add to city_visual.py as workaround to rescale figure size
        #  to prevent overlapping of large esys labels with axes
        #  plt.plot([335], [220], color='white')

if __name__ == '__main__':
    main()
