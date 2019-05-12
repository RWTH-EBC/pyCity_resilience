#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to perform Monte Carlo analysis
"""
from __future__ import division

import os
import pickle

import pycity_calc.economic.city_economic_calc as citecon
import pycity_calc.environments.germanmarket as gmarket
import pycity_calc.simulation.energy_balance.city_eb_calc as citeb
import pycity_calc.economic.annuity_calculation as annu
import pycity_calc.toolbox.modifiers.mod_city_esys_size as modesys
import pycity_calc.toolbox.mc_helpers.mc_runner as mcrun


def init_base_mc_objects(city):
    """
    Initialize all objects requires as input for mc runner object

    Parameters
    ----------
    city : object
        City object of pyCity_calc (should hold energy supply systems and
        demands

    Returns
    -------
    mc_run : object
        MC runner object of pyCity_calc
    """

    #  Generate german market instance (if not already included in environment)
    ger_market = gmarket.GermanMarket()

    #  Add GermanMarket object instance to city
    city.environment.prices = ger_market

    #  Generate annuity object instance
    annuity_obj = annu.EconomicCalculation()

    #  Generate energy balance object for city
    energy_balance = citeb.CityEBCalculator(city=city)

    city_eco_calc = citecon.CityAnnuityCalc(annuity_obj=annuity_obj,
                                            energy_balance=energy_balance)

    #  Hand over initial city object to mc_runner
    mc_run = mcrun.McRunner(city_eco_calc=city_eco_calc)

    return mc_run


def run_monte_carlo_analysis(city, nb_runs,
                             sampling_method='lhc',
                             do_sampling=True,
                             failure_tolerance=0.05,
                             prevent_printing=False,
                             load_sh_mc_res=False,
                             path_mc_res_folder=None,
                             use_profile_pool=False,
                             random_profile=False,
                             load_city_n_build_samples=False,
                             path_city_sample_dict=None,
                             path_build_sample_dict=None,
                             eeg_pv_limit=False,
                             use_kwkg_lhn_sub=False,
                             calc_th_el_cov=False,
                             dem_unc=True,
                             el_mix_for_chp=True,
                             el_mix_for_pv=True
                             ):
    """
    Run economic Monte-Carlo analysis with city object

    Parameters
    ----------
    city : object
        City object of pyCity_calc
    nb_runs : int
        Number of Monte-Carlo loops
    sampling_method : str, optional
        Defines method used for sampling (default: 'lhc')
        Options:
        - 'lhc': latin hypercube sampling
        - 'random': randomized sampling
    do_sampling : bool, optional
        Defines, if sampling should be performed/samples should be loaded
        from path (default: True). Else: Use existing sample data on
        mc_runner.py object
    failure_tolerance : float, optional
        Allowed EnergyBalanceException failure tolerance (default: 0.05).
        E.g. 0.05 means, that 5% of runs are allowed to fail with
        EnergyBalanceException.
    prevent_printing : bool, optional
        Defines, if printing statements should be suppressed
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
    random_profile : bool, optional
        Defines, if random samples should be kused from profile pool
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
        Defines, if KWKG LHN subsidies are used (default: False).
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
        Tuple with result dicts
        (dict_samples_const, dict_samples_esys, dict_res, dict_mc_setup,
        list_failed_idx)
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
            dict_res : dict
                Dict, holding dicts and arrays with result data
            dict_mc_setup : dict
                Dict, holding mc run settings
            list_failed_idx : list (of ints)
                List with indexes of failed runs (with EnergyBalanceException)
            dict_mc_cov : dict
                Dictionary holding thermal/electrical coverage factors
                dict_mc_cov['th_cov_boi'] = array_th_cov_boi
                dict_mc_cov['th_cov_chp'] = array_th_cov_chp
                dict_mc_cov['th_cov_hp_aw'] = array_th_cov_hp_aw
                dict_mc_cov['th_cov_hp_ww'] = array_th_cov_hp_ww
                dict_mc_cov['th_cov_eh'] = array_th_cov_eh
                dict_mc_cov['el_cov_chp'] = array_el_cov_chp
                dict_mc_cov['el_cov_pv'] = array_el_cov_pv
    """

    #  Hand over initial city object to mc_runner
    mc_run = init_base_mc_objects(city=city)

    #  Perform Monte-Carlo uncertainty analysis
    (dict_samples_const, dict_samples_esys, dict_res, dict_mc_setup,
     dict_profiles, dict_mc_cov) = \
        mc_run.run_mc_analysis(nb_runs=nb_runs,
                               failure_tolerance=failure_tolerance,
                               do_sampling=do_sampling,
                               prevent_printing=prevent_printing,
                               sampling_method=sampling_method,
                               load_sh_mc_res=load_sh_mc_res,
                               path_mc_res_folder=path_mc_res_folder,
                               use_profile_pool=use_profile_pool,
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

    list_failed_idx = mc_run._list_failed_runs

    print('Nb. of failed runs: ', str(len(list_failed_idx)))

    return (dict_samples_const, dict_samples_esys, dict_res, dict_mc_setup,
            list_failed_idx, dict_mc_cov)


if __name__ == '__main__':

    #  Get workspace path
    #  #############################################################
    this_path = os.path.dirname(os.path.abspath(__file__))
    src_path = os.path.dirname(os.path.dirname(this_path))
    path_workspace = os.path.join(src_path, 'workspace')
    #  #############################################################

    city_name = 'city_2_build_with_esys.pkl'

    city_path = os.path.join(path_workspace, 'city_objects', 'with_esys',
                             city_name)

    city = pickle.load(open(city_path, mode='rb'))

    nb_runs = 10  # Number of MC runs
    do_sampling = True  # Perform initial sampling or use existing samples

    dem_unc = True
    #  dem_unc : bool, optional
    # Defines, if thermal, el. and dhw demand are assumed to be uncertain
    # (default: True). If True, samples demands. If False, uses reference
    # demands.

    failure_tolerance = 0.1
    #  Allowed share of runs, which fail with EnergyBalanceException.
    #  If failure_tolerance is exceeded, mc runner exception is raised.

    #  Suppress print and warnings statements during MC-run
    prevent_printing = False

    eeg_pv_limit = True
    use_kwkg_lhn_sub = False

    calc_th_el_cov = True

    el_mix_for_chp = True  # Use el. mix for CHP fed-in electricity
    el_mix_for_pv = True  # Use el. mix for PV fed-in electricity

    #  Path to save results dict
    res_name = 'mc_run_results_dict.pkl'
    path_res = os.path.join(path_workspace, 'output', 'monte_carlo', res_name)

    #  Path to sampling dict const
    sample_name_const = 'mc_run_sample_dict_const.pkl'
    path_sample_const = os.path.join(path_workspace, 'output', 'monte_carlo',
                                     sample_name_const)

    #  Path to sampling dict esys
    sample_name_esys = 'mc_run_sample_dict_esys.pkl'
    path_sample_esys = os.path.join(path_workspace, 'output', 'monte_carlo',
                                    sample_name_esys)

    #  Path to save mc settings to
    setup_name = 'mc_run_setup_dict.pkl'
    path_setup = os.path.join(path_workspace, 'output', 'monte_carlo',
                              setup_name)

    cov_dict_name = 'mc_cov_dict.pkl'
    path_mc_cov = os.path.join(path_workspace, 'output', 'monte_carlo',
                               cov_dict_name)

    #  #############################################################

    #  If necessary, increase esys size
    modesys.incr_esys_size_city(city=city, base_factor=3, tes_factor=2)

    (dict_samples_const, dict_samples_esys, dict_res, dict_mc_setup,
     list_failed_idx, dict_mc_cov) = \
        run_monte_carlo_analysis(city=city,
                                 nb_runs=nb_runs,
                                 failure_tolerance=failure_tolerance,
                                 do_sampling=do_sampling,
                                 prevent_printing=prevent_printing,
                                 eeg_pv_limit=eeg_pv_limit,
                                 use_kwkg_lhn_sub=use_kwkg_lhn_sub,
                                 calc_th_el_cov=calc_th_el_cov,
                                 dem_unc=dem_unc,
                                 el_mix_for_chp=el_mix_for_chp,
                                 el_mix_for_pv=el_mix_for_pv
                                 )

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

    if calc_th_el_cov and dict_mc_cov is not None:
        pickle.dump(dict_mc_cov, open(path_mc_cov, mode='wb'))
        print('Saved dict_mc_cov to: ', path_mc_cov)
        print()
