#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

"""
from __future__ import division

import os
import pickle
import copy
import warnings
import numpy as np
import matplotlib.pyplot as plt

import pycity_calc.simulation.energy_balance.city_eb_calc as citeb
import pycity_calc.economic.annuity_calculation as annu
import pycity_calc.economic.city_economic_calc as citecon
import pycity_calc.toolbox.mc_helpers.mc_runner as mcrun
import pycity_calc.toolbox.mc_helpers.postprocessing.analyse_eco_mc_run \
    as analyzemc
import pycity_calc.toolbox.flex_quantification.flexibility_quant as flexquant

import pycity_resilience.ga.preprocess.add_bes as addbes
import pycity_resilience.ga.postprocess.analyze_generation_dev as andev
import pycity_resilience.ga.parser.parse_ind_to_city as parseindcit


def reeval_par_sol(path_city,
                   path_save_par,
                   path_results,
                   size_used,
                   nb_ind_used,
                   sampling_method,
                   nb_runs,
                   dem_unc,
                   load_sh_mc_res,
                   path_mc_res_folder,
                   use_profile_pool,
                   gen_use_prof_method,
                   path_profile_dict,
                   load_city_n_build_samples,
                   path_city_sample_dict,
                   path_build_sample_dict,
                   eeg_pv_limit,
                   use_kwkg_lhn_sub,
                   el_mix_for_chp,
                   el_mix_for_pv,
                   heating_off,
                   red_size,
                   failure_tolerance,
                   path_save_dict=None,
                   plot_res=False,
                   save_res=False):
    """
    Reevaluate pareto solutions by reruning economic monte carlo analysis.
    Necessary, if more than default/saved results of opt_ga.py should be
    used/extracted.

    Parameters
    ----------
    path_city : str
    path_save_par
    path_results
    size_used
    nb_ind_used
    sampling_method
    nb_runs
    dem_unc
    load_sh_mc_res
    path_mc_res_folder
    use_profile_pool
    gen_use_prof_method
    path_profile_dict
    load_city_n_build_samples
    path_city_sample_dict
    path_build_sample_dict
    eeg_pv_limit
    use_kwkg_lhn_sub
    el_mix_for_chp
    el_mix_for_pv
    heating_off
    red_size
    failure_tolerance
    path_save_dict : str, optional
    plot_res=False : bool, optional
    save_res : bool, optional

    Returns
    -------
    dict_res
    """

    #  Load city object and add pv_fed_in factor, if not existent
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

    #  Extract pareto results
    #  ####################################################################

    try:
        #  Try to load pickled pareto frontier result, if existent
        dict_pareto_sol = pickle.load(open(path_save_par, mode='rb'))
    except:
        print('Could not load pickled dictionary with pareto-frontier '
              'results  from'
              + str(path_save_par)
              + '. Thus, going to extract pareto solutions from'
              + str(path_results))

        #  Load results dicts from path
        dict_gen = andev.load_res(dir=path_results)

        #  Extract list of pareto-optimal results from overall populations
        list_inds_pareto = \
            andev.get_pareto_front(dict_gen=dict_gen,
                                   size_used=size_used,  # Nb. Gen.
                                   nb_ind_used=nb_ind_used)  # Nb. ind.

        #  Parse list of pareto solutions to dict (nb. as keys to re-identify
        #  each solution
        dict_pareto_sol = {}
        for i in range(len(list_inds_pareto)):
            dict_pareto_sol[int(i + 1)] = list_inds_pareto[i]

        #  Save pareto dict to path
        pickle.dump(dict_pareto_sol, open(path_save_par, mode='wb'))

    #  #####################################################################

    #  Generate mc_runner object

    annuity_obj = annu.EconomicCalculation()
    energy_balance = citeb.CityEBCalculator(city=city)
    city_eco_calc = citecon.CityAnnuityCalc(annuity_obj=annuity_obj,
                                            energy_balance=energy_balance)

    #  Hand over initial city object to mc_runner
    mc_run = mcrun.McRunner(city_eco_calc=city_eco_calc)

    #  Perform initial sampling
    if sampling_method == 'random':
        mc_run.perform_sampling(nb_runs=nb_runs, save_samples=True,
                                dem_unc=dem_unc)
        #  Save results toself._dict_samples_const = dict_samples_const
        #         self._dict_samples_esys = dict_samples_esys
    elif sampling_method == 'lhc':
        mc_run.perform_lhc_sampling(nb_runs=nb_runs,
                                    load_sh_mc_res=load_sh_mc_res,
                                    path_mc_res_folder=path_mc_res_folder,
                                    use_profile_pool=use_profile_pool,
                                    gen_use_prof_method=gen_use_prof_method,
                                    path_profile_dict=path_profile_dict,
                                    save_res=True,
                                    load_city_n_build_samples=load_city_n_build_samples,
                                    path_city_sample_dict=path_city_sample_dict,
                                    path_build_sample_dict=path_build_sample_dict,
                                    dem_unc=dem_unc)

    #  Generate reference system (boilers 4x rescaled) and perform ref. run
    #  ###################################################################

    #  Copy city, only use boilers
    city_copy = copy.deepcopy(city)

    #  Add to copy of mc_runner --> Perform mc run
    addbes.gen_boiler_ref_scenario(city=city_copy)

    #  Copy mc_runner obj. of ga_runner
    mc_run_ref = copy.deepcopy(mc_run)

    #  Replace city object with city_copy
    mc_run_ref._city_eco_calc.energy_balance.city = city_copy

    #  Run MC analysis
    (dict_mc_res_ref, dict_mc_setup_ref, dict_mc_cov_ref) = \
        mc_run_ref.perform_mc_runs(nb_runs=nb_runs,
                                   sampling_method=sampling_method,
                                   eeg_pv_limit=eeg_pv_limit,
                                   use_kwkg_lhn_sub=use_kwkg_lhn_sub,
                                   el_mix_for_chp=el_mix_for_chp,
                                   el_mix_for_pv=el_mix_for_pv,
                                   heating_off=heating_off
                                   )

    if len(dict_mc_setup_ref['idx_failed_runs']) > 0:
        msg = 'Reference run (rescaled boilers) failed!'
        raise AssertionError(msg)

    #  ####################################################################

    print('Start reevaluation of pareto results')
    print('#################################################################')
    print()

    list_keys = list(dict_pareto_sol.keys())
    list_keys.sort()

    #  Dummy result dict
    dict_res = {}

    if red_size is not None:
        list_allowed = list(range(1, nb_ind_used, red_size))
        print('List allowed solution numbers: ', list_allowed)
    else:
        list_allowed = list_keys

    #  Loop over results
    for i in list_keys:
        if i in list_allowed:
            print('Solution key: ', i)

            ind_sel = dict_pareto_sol[i]

            #  Copy mc_runner
            mc_run_copy = copy.deepcopy(mc_run)

            #  Use parser
            #  Generate city with ind object (copy of city)
            parseindcit. \
                parse_ind_dict_to_city(dict_ind=ind_sel,
                                       city=mc_run_copy._city_eco_calc.energy_balance.city,
                                       copy_city=False)

            # #  Add city_eco_calc
            # mc_run_copy._city_eco_calc = city_eco_calc

            #  Reinitialize mc_runner
            mc_run_copy._city_eco_calc.energy_balance.reinit()

            #  Perform MC analysis
            (dict_mc_res, dict_mc_setup, dict_mc_cov) = \
                mc_run_copy.perform_mc_runs(nb_runs=nb_runs,
                                            sampling_method=sampling_method,
                                            eeg_pv_limit=eeg_pv_limit,
                                            failure_tolerance=
                                            failure_tolerance,
                                            use_kwkg_lhn_sub=use_kwkg_lhn_sub,
                                            el_mix_for_chp=el_mix_for_chp,
                                            el_mix_for_pv=el_mix_for_pv,
                                            heating_off=heating_off
                                            )

            #  Initialize mc analyze object
            mc_analyze = analyzemc.EcoMCRunAnalyze()

            #  Hand over results and setup dict
            mc_analyze.dict_results = dict_mc_res
            mc_analyze.dict_setup = dict_mc_setup

            #  Extract basic results
            mc_analyze.extract_basic_results()
            mc_analyze.calc_annuity_to_net_energy_ratio()
            mc_analyze.calc_co2_to_net_energy_ratio()
            mc_analyze.calc_dimless_cost_co2(dict_ref_run=dict_mc_res_ref)

            #  Perform flexibility calculation
            city_flex_copy = copy.deepcopy(
                mc_run_copy._city_eco_calc.energy_balance.city)

            (beta_el_pos, beta_el_neg) = \
                flexquant.calc_beta_el_city(city=city_flex_copy)

            #  Save results
            dict_res_ind = {}

            dict_res_ind['array_dimless_cost'] = mc_analyze._array_dimless_cost
            dict_res_ind['array_dimless_co2'] = mc_analyze._array_dimless_co2
            dict_res_ind['array_ann'] = mc_analyze._array_ann_mod
            dict_res_ind['array_co2'] = mc_analyze._array_co2_mod

            dict_res_ind['array_sh'] = mc_analyze._array_sh_dem_mod
            dict_res_ind['array_el'] = mc_analyze._array_el_dem_mod
            dict_res_ind['array_dhw'] = mc_analyze._array_dhw_dem_mod

            # dict_res_ind['beta_el_pos'] = beta_el_pos
            # dict_res_ind['beta_el_neg'] = beta_el_neg

            dict_res_ind[
                'list_idx_failed_runs'] = mc_analyze._list_idx_failed_runs

            #  Save to overall results dict
            dict_res[i] = dict_res_ind

    if save_res:
        #  Save dict_res
        pickle.dump(dict_res, open(path_save_dict, mode='wb'))

    if plot_res:
        #  Plot mean dimless function values
        fig = plt.figure()

        for i in list_keys:
            if i in list_allowed:
                print('Solution key: ', i)

                dimless_cost_mean = np.mean(dict_res[i]['array_dimless_cost'])
                dimless_co2_mean = np.mean(dict_res[i]['array_dimless_co2'])

                print(dimless_cost_mean)
                print(dimless_co2_mean)

                plt.plot([dimless_cost_mean],
                         [dimless_co2_mean],
                         marker='o',
                         linestyle='',
                         markersize=3,
                         )

        plt.xlabel('Dimensionless cost')
        plt.ylabel('Dimensionless emissions')
        plt.show()
        plt.close()

    return dict_res


def main():
    #  Define pathes
    #  ####################################################################
    this_path = os.path.dirname(os.path.abspath(__file__))
    src_path = os.path.dirname(os.path.dirname(os.path.dirname(this_path)))
    workspace = os.path.join(src_path, 'workspace')

    name_res_folder = 'ga_run_job_8_dimless_mean_co2_dyn'
    path_results = os.path.join(workspace,
                                'output',
                                'ga_opt',
                                name_res_folder)

    out_name = name_res_folder + '_dict_par_front_sol.pkl'
    path_save_par = os.path.join(workspace, 'output', 'ga_opt', out_name)

    save_res = True
    plot_res = True

    # nb_ind_used : int, optional
    #     Number of pareto-optimal solutions, which should be extracted
    #     (default: None). If None, nb_ind_used is equal to size of population
    #     respectively number of individuals per population
    nb_ind_used = 400

    # size_used : int, optional
    #     Defines size of last number of generations, which should be used
    #     in NSGA-2 sorting (default: None). If None, uses all generations.
    size_used = None

    #  Reduce number of analysed pareto solutions?
    red_size = 50
    #  If red_size is None, use original size (nb_ind_used)
    #  Else; only process solution numbers 1, 1+res_size, 1 + 2 x red_size ...

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

    #  Name city object
    #  ############################################
    city_name = 'aachen_kronenberg_6.pkl'

    #  Pathes
    #  ################################################################
    path_city = os.path.join(workspace, 'city_objects',
                             # 'with_esys',
                             'no_esys',
                             city_name)

    #  Savings path
    path_save = os.path.join(workspace, 'output',
                             'reevaluate_par',
                             str(city_name[:-4]))

    if not os.path.exists(path_save):
        os.makedirs(path_save)

    save_name = 'dict_res.pkl'
    path_save_dict = os.path.join(path_save, save_name)

    dict_res = reeval_par_sol(path_city=path_city,
                              path_save_par=path_save_par,
                              path_results=path_results,
                              size_used=size_used,
                              nb_ind_used=nb_ind_used,
                              sampling_method=sampling_method,
                              nb_runs=nb_runs,
                              dem_unc=dem_unc,
                              load_sh_mc_res=load_sh_mc_res,
                              path_mc_res_folder=path_mc_res_folder,
                              use_profile_pool=use_profile_pool,
                              gen_use_prof_method=gen_use_prof_method,
                              path_profile_dict=path_profile_dict,
                              load_city_n_build_samples=load_city_n_build_samples,
                              path_city_sample_dict=path_city_sample_dict,
                              path_build_sample_dict=path_build_sample_dict,
                              eeg_pv_limit=eeg_pv_limit,
                              use_kwkg_lhn_sub=use_kwkg_lhn_sub,
                              el_mix_for_chp=el_mix_for_chp,
                              el_mix_for_pv=el_mix_for_pv,
                              heating_off=heating_off,
                              red_size=red_size,
                              failure_tolerance=failure_tolerance,
                              path_save_dict=path_save_dict,
                              save_res=save_res,
                              plot_res=plot_res)

if __name__ == '__main__':
    main()
