#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to evaluate objectives of GA
"""
from __future__ import division

import copy
import warnings
import numpy as np

import pycity_calc.toolbox.mc_helpers.mc_runner as mcrun
import pycity_calc.toolbox.mc_helpers.postprocessing.analyse_eco_mc_run \
    as analyzemc
import pycity_calc.simulation.energy_balance.check_eb_requ as checkeb
import pycity_calc.simulation.energy_balance.building_eb_calc as buildeb
import pycity_calc.toolbox.flex_quantification.flexibility_quant as flexquant

import pycity_resilience.ga.parser.parse_ind_to_city as parseind
import pycity_resilience.ga.verify.check_validity as checkval


def eval_obj(individuum,
             ga_runner,
             dict_restr,
             sampling_method,
             objective,
             use_street=False, eeg_pv_limit=False,
             dict_max_pv_area=None, dict_sh=None,
             pv_min=None, pv_step=1, use_pv=False, add_pv_prop=0,
             use_kwkg_lhn_sub=False,
             chp_switch_pen=False,
             max_switch=None,
             risk_fac_av=-1,
             risk_fac_friendly=1,
             el_mix_for_chp=True, el_mix_for_pv=True,
             heating_off=True,
             prevent_boi_lhn=True,
             dict_heatloads=None):
    """
    Evaluation function

    Parameters
    ----------
    individuum : dict
        Dict holding parameters of GA individuum
    ga_runner : object
        GA runner object of pyCity_resilience
    dict_restr : dict
        Dict holding possible energy system sizes
    sampling_method : str
        Defines method used for sampling.
        Options:
        - 'lhc': latin hypercube sampling
        - 'random': randomized sampling
    objective : str
        Objective function
         Options:
         'mc_risk_av_ann_co2_to_net_energy':
         'ann_and_co2_to_net_energy_ref_test'
         'ann_and_co2_ref_test'
         'mc_risk_av_ann_and_co2'
         'mc_mean_ann_and_co2'
         'mc_risk_friendly_ann_and_co2'
         'mc_min_std_of_ann_and_co2'
         'mc_dimless_eco_em_2d_mean'
         'mc_dimless_eco_em_2d_risk_av'
         'mc_dimless_eco_em_2d_risk_friendly'
         'mc_dimless_eco_em_2d_std'
         'ann_and_co2_dimless_ref'
         'mc_dimless_eco_em_3d_mean'
         'mc_dimless_eco_em_3d_risk_av'
         'mc_dimless_eco_em_3d_risk_friendly'
         'mc_dimless_eco_em_3d_std'
         'ann_and_co2_dimless_ref_3d'
    use_street : bool, optional
        Use street networks to route LHN pipelines (default: False)
        Requires street nodes and edges on city graph, is use_street == True
    eeg_pv_limit : bool, optional
        Defines, if EEG PV feed-in limitation of 70 % of peak load is
        active (default: False). If limitation is active, maximal 70 %
        of PV peak load are fed into the grid.
        However, self-consumption is used, first.
    dict_max_pv_area : dict, optional
        Dict holding maximum usable PV area values in m2 per building
        (default: None)
    dict_sh : dict, optional
        Dictionary holding building node ids as keys and maximum space heating
        power values in Watt as dict values (default: None). If not None,
        used for size limitation. If None, dict_restr is used for sizing.
        (default: None)
    pv_min : float, optional
        Minimum possible PV area per building in m2 (default: None)
    pv_step : float, optional
        Defines discrete step of Pv sizing in m2 (default: 1). E.g.
        If minimum PV size is 8 m2, 9, 10, 11...up to max. rooftop area can
        be chosen as PV size.
    use_pv : bool, optional
        Defines, if PV can be used (default: False)
    add_pv_prop : float, optional
        Defines additional probability of PV being changed, if only thermal
        mutation has been applied (defauft: 0). E.g. if boiler system has
        been changed to CHP, there is a change of add_pv_prob that also PV
        is mutated.
    use_kwkg_lhn_sub : bool, optional
        Defines, if KWKG LHN subsidies are used (default: False).
        If True, can get 100 Euro/m as subdidy, if share of CHP LHN fed-in
        is equal to or higher than 60 %
    chp_switch_pen : bool, optional
        Defines, if too many switchings per day (CHP) should be penalized
        (default: False).
    max_switch : int, optional
        Defines maximum number of allowed average switching commands per CHP
        for a single day (default: None), e.g. 8 means that a maximum of 8
        on/off or off/on switching commands is allowed as average per day.
        Only relevant, if chp_switch_pen is True
    risk_fac_av : float, optional
        Preference/risk value for mu-sigma-evaluation for risk averse
        preference (default: -1)
    risk_fac_friendly : float, optional
        Preference/risk value for mu-sigma-evaluation for risk
        friendly preference (default: 1)
    el_mix_for_chp : bool, optional
        Defines, if el. mix should be used for CHP fed-in electricity
        (default: True). If False, uses specific fed-in CHP factor,
        defined in co2emissions object (co2_factor_el_feed_in)
    el_mix_for_pv : bool, optional
        Defines, if el. mix should be used for PV fed-in electricity
        (default: True). If False, uses specific fed-in PV factor,
        defined in co2emissions object (co2_factor_pv_fed_in)
    heating_off : bool, optional
        Defines, if sampling to deactivate heating during summer should
        be used (default: True)
    prevent_boi_lhn : bool, optional
		Prevent boi/eh LHN combinations (without CHP) (default: True).
		If True, adds CHPs to LHN systems without CHP
	dict_heatloads : dict, optional
        Dict holding building ids as keys and design heat loads in Watt
        as values (default: None)

    Returns
    -------
    tuple_obj_fkt : tuple
        Tuple holding objective function fitness values, e.g.
        (win_en_to_an, win_en_to_co2) for objective
        'net_energy_related_to_ann_and_co2'
    """

    if (objective not in ['mc_risk_av_ann_co2_to_net_energy',
                          'ann_and_co2_to_net_energy_ref_test',
                          'ann_and_co2_ref_test',
                          'mc_risk_av_ann_and_co2',
                          'mc_mean_ann_and_co2',
                          'mc_risk_friendly_ann_and_co2',
                          'mc_min_std_of_ann_and_co2',
                          'mc_dimless_eco_em_2d_mean',
                          'mc_dimless_eco_em_2d_risk_av',
                          'mc_dimless_eco_em_2d_risk_friendly',
                          'ann_and_co2_dimless_ref',
                          'mc_dimless_eco_em_3d_mean',
                          'mc_dimless_eco_em_3d_risk_av',
                          'mc_dimless_eco_em_3d_risk_friendly',
                          'ann_and_co2_dimless_ref_3d',
                          'mc_dimless_eco_em_2d_std',
                          'mc_dimless_eco_em_3d_std'
                          ]):
        msg = 'Unknown objective. Check your input for eval_obj().'
        raise AssertionError(msg)

    if chp_switch_pen:
        if max_switch is None:
            msg = 'max_switch cannot be None, if chp_switch_pen is True.' \
                  ' Please set a maximum number of allowed switching CHP ' \
                  'commands per day (e.g. max_switch = 8).'
            raise AssertionError(msg)

    # Check validity of ind
    checkval.run_all_checks(ind=individuum, dict_max_pv_area=dict_max_pv_area,
                            dict_restr=dict_restr, dict_sh=dict_sh,
                            pv_min=pv_min, pv_step=pv_step, use_pv=use_pv,
                            add_pv_prop=add_pv_prop,
                            prevent_boi_lhn=prevent_boi_lhn,
                            dict_heatloads=dict_heatloads)

    # Copy ga runner
    ga_runner_copy = copy.deepcopy(ga_runner)

    #  Pointers to nb. of runs and failure tolerance
    nb_runs = ga_runner_copy.nb_runs
    failure_tolerance = ga_runner_copy.failure_tolerance

    #  Add new individuum parameters to city object instance
    #  on CityEBCalculator (use original city object (city_copy is False)
    #  on copied ga_runner object (thus, original city on original ga_runner
    #  is not going to be modified)
    parseind.parse_ind_dict_to_city(dict_ind=individuum,
                                    city=ga_runner_copy._city,
                                    list_build_ids=
                                    ga_runner_copy._list_build_ids,
                                    use_street=use_street,
                                    copy_city=False)

    #  Reinitialize CityEBCalculator with new city object instance
    ga_runner_copy.mc_runner._city_eco_calc.energy_balance.reinit()

    #  Evaluate reference values instead of MC runs (for testing purpose)
    #  ##############################################################
    if objective == 'ann_and_co2_to_net_energy_ref_test':
        try:
            #  Perform reference run
            (ann, co2, sh_dem, el_dem, dhw_dem) = ga_runner_copy. \
                mc_runner.perform_ref_run(eeg_pv_limit=eeg_pv_limit,
                                          use_kwkg_lhn_sub=use_kwkg_lhn_sub,
                                          chp_switch_pen=chp_switch_pen,
                                          max_switch=max_switch,
                                          obj='min',
                                          el_mix_for_chp=el_mix_for_chp,
                                          el_mix_for_pv=el_mix_for_pv
                                          )

            ann_to_en = ann / (sh_dem + el_dem + dhw_dem)

            co2_to_en = co2 / (sh_dem + el_dem + dhw_dem)

        except buildeb.EnergyBalanceException or checkeb.EnergySupplyException:
            msg = 'Ran into EnergyBalanceException ' \
                  'or EnergySupplyException, which means ' \
                  'that system is not able to cover demands for reference' \
                  ' run. Thus, solution is going to be penalized!'
            warnings.warn(msg)

            ann_to_en = 10 ** 100
            co2_to_en = 10 ** 100

        return (ann_to_en, co2_to_en)
    # ################################

    elif objective == 'ann_and_co2_ref_test':
        try:
            #  Perform reference run
            (ann, co2, sh_dem, el_dem, dhw_dem) = ga_runner_copy. \
                mc_runner.perform_ref_run(eeg_pv_limit=eeg_pv_limit,
                                          use_kwkg_lhn_sub=use_kwkg_lhn_sub,
                                          chp_switch_pen=chp_switch_pen,
                                          max_switch=max_switch, obj='min',
                                          el_mix_for_chp=el_mix_for_chp,
                                          el_mix_for_pv=el_mix_for_pv
                                          )

        except buildeb.EnergyBalanceException or checkeb.EnergySupplyException:
            msg = 'Ran into EnergyBalanceException ' \
                  'or EnergySupplyException, which means ' \
                  'that system is not able to cover demands for reference' \
                  ' run. Thus, solution is going to be penalized!'
            warnings.warn(msg)

            ann = 10 ** 100
            co2 = 10 ** 100

        return (ann, co2)
    # ################################

    elif objective == 'ann_and_co2_dimless_ref':
        try:
            #  Perform reference run
            (ann, co2, sh_dem, el_dem, dhw_dem) = ga_runner_copy. \
                mc_runner.perform_ref_run(eeg_pv_limit=eeg_pv_limit,
                                          use_kwkg_lhn_sub=use_kwkg_lhn_sub,
                                          chp_switch_pen=chp_switch_pen,
                                          max_switch=max_switch, obj='min',
                                          el_mix_for_chp=el_mix_for_chp,
                                          el_mix_for_pv=el_mix_for_pv
                                          )

            #  Calculate dimensionless parameters
            ann = ann / ga_runner._ann_ref
            co2 = co2 / ga_runner._co2_ref

        except buildeb.EnergyBalanceException or checkeb.EnergySupplyException:
            msg = 'Ran into EnergyBalanceException ' \
                  'or EnergySupplyException, which means ' \
                  'that system is not able to cover demands for reference' \
                  ' run. Thus, solution is going to be penalized!'
            warnings.warn(msg)

            ann = 10 ** 100
            co2 = 10 ** 100

        return (ann, co2)

    # ################################

    elif objective == 'ann_and_co2_dimless_ref_3d':
        try:
            #  Perform reference run
            (ann, co2, sh_dem, el_dem, dhw_dem) = ga_runner_copy. \
                mc_runner.perform_ref_run(eeg_pv_limit=eeg_pv_limit,
                                          use_kwkg_lhn_sub=use_kwkg_lhn_sub,
                                          chp_switch_pen=chp_switch_pen,
                                          max_switch=max_switch, obj='min',
                                          el_mix_for_chp=el_mix_for_chp,
                                          el_mix_for_pv=el_mix_for_pv
                                          )

            #  Calculate dimensionless parameters
            ann = ann / ga_runner._ann_ref
            co2 = co2 / ga_runner._co2_ref

            #  Calc. flexibility
            city_flex_copy = copy.deepcopy(ga_runner_copy._city)

            (beta_el_pos, beta_el_neg) = \
                flexquant.calc_beta_el_city(city=city_flex_copy)

            beta_el = abs(beta_el_pos) + abs(beta_el_neg)

            print('Dimensionless el. energy flexibility beta_el: ', beta_el)
            print()

        except buildeb.EnergyBalanceException or checkeb.EnergySupplyException:
            msg = 'Ran into EnergyBalanceException ' \
                  'or EnergySupplyException, which means ' \
                  'that system is not able to cover demands for reference' \
                  ' run. Thus, solution is going to be penalized!'
            warnings.warn(msg)

            ann = 10 ** 100
            co2 = 10 ** 100
            beta_el = -10 ** 100

        return (ann, co2, beta_el)

    # ##############################################################
    # ##############################################################

    #  If MC run should be performed and sampling method is 'random',
    #  energy system samples are chosen for new energy system config.
    if sampling_method == 'random':
        #  Re-sample energy system parameters, as esys config might have
        #  changed
        ga_runner_copy.mc_runner.perform_esys_resampling(nb_runs=nb_runs)

    try:
        #  Perform Monte-Carlo runs (dict_mc_cov is currently None/unused)
        (dict_mc_res, dict_mc_setup, dict_mc_cov) = \
            ga_runner_copy.mc_runner.perform_mc_runs(nb_runs=nb_runs,
                                                     sampling_method=
                                                     sampling_method,
                                                     failure_tolerance=
                                                     failure_tolerance,
                                                     eeg_pv_limit=eeg_pv_limit,
                                                     use_kwkg_lhn_sub=
                                                     use_kwkg_lhn_sub,
                                                     el_mix_for_chp=
                                                     el_mix_for_chp,
                                                     el_mix_for_pv=
                                                     el_mix_for_pv,
                                                     heating_off=heating_off
                                                     )

        #  Initialize mc analyze object
        mc_analyze = analyzemc.EcoMCRunAnalyze()

        #  Hand over results and setup dict
        mc_analyze.dict_results = dict_mc_res
        mc_analyze.dict_setup = dict_mc_setup

        #  Extract basic results
        #  ####################################################################
        mc_analyze.extract_basic_results()
        # mc_analyze.calc_net_energy_to_annuity_ratio()
        # mc_analyze.calc_net_energy_to_co2_ratio()
        # mc_analyze.calc_net_exergy_to_annuity_ratio()
        # mc_analyze.calc_net_exergy_to_co2_ratio()
        mc_analyze.calc_annuity_to_net_energy_ratio()
        mc_analyze.calc_co2_to_net_energy_ratio()

        #  Pre-calculate dimensionless cost and co2 parameters:
        if (objective == 'mc_dimless_eco_em_2d_mean'
                or objective == 'mc_dimless_eco_em_2d_risk_av'
                or objective == 'mc_dimless_eco_em_2d_risk_friendly'
                or objective == 'mc_dimless_eco_em_3d_mean'
                or objective == 'mc_dimless_eco_em_3d_risk_av'
                or objective == 'mc_dimless_eco_em_3d_risk_friendly'
                or objective == 'mc_dimless_eco_em_2d_std'
                or objective == 'mc_dimless_eco_em_3d_std'):
            #  Calculate dimensionless cost and co2 parameters
            mc_analyze.calc_dimless_cost_co2(dict_ref_run=
                                             ga_runner._dict_mc_res_ref)

        #  Pre-calculate energy flexibility
        if (objective == 'mc_dimless_eco_em_3d_mean'
                or objective == 'mc_dimless_eco_em_3d_risk_av'
                or objective == 'mc_dimless_eco_em_3d_risk_friendly'
                or objective == 'mc_dimless_eco_em_3d_std'):
            #  Calc. flexibility
            city_flex_copy = copy.deepcopy(ga_runner_copy._city)

            (beta_el_pos, beta_el_neg) = \
                flexquant.calc_beta_el_city(city=city_flex_copy)

            beta_el = abs(beta_el_pos) + abs(beta_el_neg)

            print('Dimensionless el. energy flexibility beta_el: ', beta_el)
            print()

        if objective == 'mc_risk_av_ann_co2_to_net_energy':
            #  Evaluate risk aversion with annuity / CO2 values to net energy
            ann_risk_factor = mc_analyze.calc_risk_averse_parameters(
                type='ann_to_en')
            co2_risk_factor = mc_analyze.calc_risk_averse_parameters(
                type='co2_to_en')

            print('Risk aversion evaluation factor of annuity to net '
                  'energy ratios:')
            print(round(ann_risk_factor, 2))

            print('Risk aversion evaluation factor of co2 to net '
                  'energy ratios:')
            print(round(co2_risk_factor, 2))
            print()

        elif objective == 'mc_risk_av_ann_and_co2':
            #  Evaluate risk aversion with annuity / CO2 values
            ann_risk_factor = mc_analyze.calc_risk_averse_parameters(
                type='annuity')
            co2_risk_factor = mc_analyze.calc_risk_averse_parameters(
                type='co2')

            print('Risk aversion evaluation factor of annuity:')
            print(round(ann_risk_factor, 2))

            print('Risk aversion evaluation factor of co2:')
            print(round(co2_risk_factor, 2))
            print()

        elif objective == 'mc_mean_ann_and_co2':

            #  Extract annuity values and calculate mean
            ann_risk_factor = np.mean(mc_analyze._array_ann_mod)

            #  Extract CO2 values and calculate mean
            co2_risk_factor = np.mean(mc_analyze._array_co2_mod)

            print('Mean value of annuity:')
            print(round(ann_risk_factor, 2))

            print('Mean value of CO2:')
            print(round(co2_risk_factor, 2))
            print()

        elif objective == 'mc_risk_friendly_ann_and_co2':
            # #  Evaluate risk friendly (mean) with annuity / CO2 values

            ann_risk_factor = mc_analyze.calc_risk_friendly_parameters(
                type='annuity')
            co2_risk_factor = mc_analyze.calc_risk_friendly_parameters(
                type='co2')

            print('Risk friendly evaluation factor of annuity:')
            print(round(ann_risk_factor, 2))

            print('Risk friendly evaluation factor of co2:')
            print(round(co2_risk_factor, 2))
            print()

        elif objective == 'mc_min_std_of_ann_and_co2':
            # #  Minimize std of annuity / CO2 values

            #  Extract annuity values and calculate mean
            ann_risk_factor = np.std(mc_analyze._array_ann_mod)

            #  Extract CO2 values and calculate mean
            co2_risk_factor = np.std(mc_analyze._array_co2_mod)

            print('Std. value of annuity:')
            print(round(ann_risk_factor, 2))

            print('Std. value of CO2:')
            print(round(co2_risk_factor, 2))
            print()

        elif (objective == 'mc_dimless_eco_em_2d_mean' or
              objective == 'mc_dimless_eco_em_3d_mean'):
            #  Minimize mean of dimless cost and co2

            #  Extract dimless annuity values and calculate mean
            ann_risk_factor = np.mean(mc_analyze._array_dimless_cost)

            #  Extract dimless CO2 values and calculate mean
            co2_risk_factor = np.mean(mc_analyze._array_dimless_co2)

            print('Mean value of dimensionless annuity:')
            print(round(ann_risk_factor, 2))

            print('Mean value of dimensionless CO2:')
            print(round(co2_risk_factor, 2))
            print()

        elif (objective == 'mc_dimless_eco_em_2d_risk_av' or
              objective == 'mc_dimless_eco_em_3d_risk_av'):
            #  Minimize risk averse dimensionless cost and emissions

            #  Evaluate risk aversion with dimless annuity / CO2 values
            ann_risk_factor = mc_analyze.calc_risk_averse_parameters(
                type='dimless_an', risk_factor=risk_fac_av)
            co2_risk_factor = mc_analyze.calc_risk_averse_parameters(
                type='dimless_co2', risk_factor=risk_fac_av)

            print('Risk aversion evaluation factor of dimensionless annuity:')
            print(round(ann_risk_factor, 2))

            print('Risk aversion evaluation factor of dimensionless co2:')
            print(round(co2_risk_factor, 2))
            print()

        elif (objective == 'mc_dimless_eco_em_2d_risk_friendly' or
              objective == 'mc_dimless_eco_em_3d_risk_friendly'):
            #  Minimize risk friendly dimensionless cost and emissions

            ann_risk_factor = mc_analyze.calc_risk_friendly_parameters(
                type='dimless_an', risk_factor=risk_fac_friendly)
            co2_risk_factor = mc_analyze.calc_risk_friendly_parameters(
                type='dimless_co2', risk_factor=risk_fac_friendly)

            print('Risk friendly evaluation factor of dimensionless annuity:')
            print(round(ann_risk_factor, 2))

            print('Risk friendly evaluation factor of dimensionless co2:')
            print(round(co2_risk_factor, 2))
            print()

        elif (objective == 'mc_dimless_eco_em_2d_std' or
              objective == 'mc_dimless_eco_em_3d_std'):
            #  Minimize std of dimless cost and co2

            #  Extract dimless annuity values and calculate mean
            ann_risk_factor = np.std(mc_analyze._array_dimless_cost)

            #  Extract dimless CO2 values and calculate mean
            co2_risk_factor = np.std(mc_analyze._array_dimless_co2)

            print('Std. value of dimensionless annuity:')
            print(round(ann_risk_factor, 2))

            print('Std. value of dimensionless CO2:')
            print(round(co2_risk_factor, 2))
            print()

    except mcrun.McToleranceException:
        msg = 'Ran into McToleranceException, which means that more than' \
              ' allowed share of runs failed. This solution is going to ' \
              'be penalized!'
        warnings.warn(msg)

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
                or objective == 'mc_dimless_eco_em_2d_std'):
            ann_risk_factor = 10 ** 100
            co2_risk_factor = 10 ** 100

        elif (objective == 'mc_dimless_eco_em_3d_mean'
              or objective == 'mc_dimless_eco_em_3d_risk_av'
              or objective == 'mc_dimless_eco_em_3d_risk_friendly'
              or objective == 'mc_dimless_eco_em_3d_std'):
            ann_risk_factor = 10 ** 100
            co2_risk_factor = 10 ** 100
            beta_el = -10 ** 100

    except checkeb.EnergySupplyException:
        msg = 'Ran into EnergySupplyException, which means that illogical ' \
              'energy system configuration has been chosen (such as ' \
              'building without thermal supply unit and without LHN ' \
              'connection). This solution is going to be penalized!'
        warnings.warn(msg)

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
                or objective == 'mc_dimless_eco_em_2d_std'):
            ann_risk_factor = 10 ** 100
            co2_risk_factor = 10 ** 100

        elif (objective == 'mc_dimless_eco_em_3d_mean'
              or objective == 'mc_dimless_eco_em_3d_risk_av'
              or objective == 'mc_dimless_eco_em_3d_risk_friendly'
              or objective == 'mc_dimless_eco_em_3d_std'):
            ann_risk_factor = 10 ** 100
            co2_risk_factor = 10 ** 100
            beta_el = -10 ** 100

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
            or objective == 'mc_dimless_eco_em_2d_std'):
        return (ann_risk_factor, co2_risk_factor)
    elif (objective == 'mc_dimless_eco_em_3d_mean'
          or objective == 'mc_dimless_eco_em_3d_risk_av'
          or objective == 'mc_dimless_eco_em_3d_risk_friendly'
          or objective == 'mc_dimless_eco_em_3d_std'):
        return (ann_risk_factor, co2_risk_factor, beta_el)
