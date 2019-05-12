#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

"""
from __future__ import division

import random
import math
import numpy as np

import pycity_resilience.ga.evolution.esys_changes as esyschanges
import pycity_resilience.ga.analyse.find_lhn as findlhn
import pycity_resilience.ga.evolution.helpers.mod_list_esys_sizes as modlist


def mut_esys_val_single_build(ind, n, prob_mut, dict_restr, pv_min,
                              dict_max_pv_area, dict_sh=None, pv_step=1,
                              dict_heatloads=None):
    """
    Randomly change energy system values in ranges given by dict_restr

    Parameters
    ----------
    ind : dict
        Individuum dictionary holding node ids with energy system dicts
        and 'lhn' with list of LHN subnetworks
    n : int
        Chosen building id in individuum dict
    prob_mut : float
        Probability of mutation (e.g. 0.2 --> 20 % chance of mutation of
        single attribute)
    dict_restr : dict
        Dict holding possible energy system sizes
    pv_min : float
        Minimum possible PV area per building in m2
    dict_max_pv_area : dict
        Dict holding maximum usable PV area values in m2 per building
    dict_sh : dict, optional
        Dictionary holding building node ids as keys and maximum space heating
        power values in Watt as dict values (default: None). If not None,
        used for size limitation. If None, dict_restr is used for sizing.
    pv_step : float, optional
        Defines discrete step of Pv sizing in m2 (default: 1). E.g.
        If minimum PV size is 8 m2, 9, 10, 11...up to max. rooftop area can
        be chosen as PV size.
    dict_heatloads : dict, optional
        Dict holding building ids as keys and design heat loads in Watt
        as values (default: None)
    """

    assert prob_mut >= 0
    assert prob_mut <= 1
    assert pv_min >= 0
    assert pv_step > 0

    #  Define list with allowed sizes
    #  #######################################################################
    if dict_sh is not None:
        #  Boiler
        list_boi_choice = \
            modlist.get_list_values_larger_than_ref(
                list_val=dict_restr['boi'],
                ref_val=dict_heatloads[n])
        #  Air/water heat pump
        list_hp_aw_choice = modlist. \
            get_list_values_larger_than_ref(list_val=dict_restr['hp_aw'],
                                            ref_val=dict_sh[n])
        #  Water/water heat pump
        list_hp_ww_choice = modlist. \
            get_list_values_larger_than_ref(list_val=dict_restr['hp_ww'],
                                            ref_val=dict_sh[n])

        #  CHP
        list_chp_choice = modlist. \
            get_list_values_smaller_than_ref(list_val=dict_restr['chp'],
                                             ref_val=dict_sh[n])

        assert len(list_boi_choice) > 0
        assert len(list_hp_aw_choice) > 0
        assert len(list_hp_ww_choice) > 0
        assert len(list_chp_choice) > 0
    else:
        list_boi_choice = dict_restr['boi']
        list_hp_aw_choice = dict_restr['hp_aw']
        list_hp_ww_choice = dict_restr['hp_ww']
        list_chp_choice = dict_restr['chp']
    # #######################################################################

    # Mutate boiler
    if random.random() < prob_mut and ind[n]['boi'] > 0:
        ind[n]['boi'] = random.choice(list_boi_choice)

    # Mutate CHP
    if (random.random() < prob_mut and ind[n]['chp'] > 0
            and ind[n]['hp_aw'] == 0 and ind[n]['hp_ww'] == 0):
        ind[n]['chp'] = random.choice(list_chp_choice)

    # Mutate AW heat pump
    if (random.random() < prob_mut and ind[n]['hp_aw'] > 0
            and ind[n]['hp_ww'] == 0 and ind[n]['chp'] == 0):
        ind[n]['hp_aw'] = random.choice(list_hp_aw_choice)

    # Mutate WW heat pump
    if (random.random() < prob_mut and ind[n]['hp_ww'] > 0 and
            ind[n]['hp_aw'] == 0 and ind[n]['chp'] == 0):
        ind[n]['hp_ww'] = random.choice(list_hp_ww_choice)

    # Mutate EH
    if (random.random() < prob_mut and ind[n]['eh'] > 0):
        ind[n]['eh'] = random.choice(dict_restr['eh'])

    # Mutate thermal storage
    if random.random() < prob_mut and ind[n]['tes'] > 0 \
            and (ind[n]['boi'] > 0
                 or ind[n]['chp'] > 0
                 or ind[n]['hp_aw'] > 0
                 or ind[n]['hp_ww'] > 0):
        ind[n]['tes'] = random.choice(dict_restr['tes'])

    # Mutate PV
    if random.random() < prob_mut and ind[n]['pv'] > 0:
        pv_max = dict_max_pv_area[n]

        min_ref = round(pv_min, 0)
        max_ref = math.ceil(pv_max)

        if max_ref > min_ref:
            array_choices = np.arange(start=min_ref, stop=max_ref,
                                      step=pv_step)

            pv_area = np.random.choice(array_choices)

        elif max_ref == min_ref:

            pv_area = min_ref + 0.0

        else:

            pv_area = 0

        ind[n]['pv'] = pv_area

    # Mutate battery
    if random.random() < prob_mut and ind[n]['bat'] > 0:
        ind[n]['bat'] = random.choice(dict_restr['bat'])


def mut_esys_config_single_build(ind, n, dict_restr, pv_min,
                                 dict_max_pv_area,
                                 list_options=None,
                                 list_opt_prob=None,
                                 list_lhn_opt=None,
                                 list_lhn_prob=None,
                                 use_bat=True,
                                 use_pv=True,
                                 dict_sh=None,
                                 sh_power_min=None,
                                 pv_step=1,
                                 add_pv_prop=0,
                                 add_bat_prob=0,
                                 dict_heatloads=None):
    """
    Change energy system configurations (e.g. from HP/EH to boiler/CHP).

    Differentiate between nodes n with and without LHN connection.
    LHN connected buildings have other mutation options (e.g. 'no_th_supply')

    Parameters
    ----------
    ind : dict
        Individuum dictionary holding node ids with energy system dicts
        and 'lhn' with list of LHN subnetworks
    n : int
        Chosen building id in individuum dict
    dict_restr : dict
        Dict holding possible energy system sizes
    pv_min : float
        Minimum possible PV area per building in m2
    dict_max_pv_area : dict
        Dict holding maximum usable PV area values in m2 per building
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
    use_bat : bool, optional
        Defines, if battery can be used (default: True)
    use_pv : bool, optional
        Defines, if PV can be used (default: True)
    dict_sh : dict, optional
        Dictionary holding building node ids as keys and maximum space heating
        power values in Watt as dict values (default: None). If not None,
        used for size limitation. If None, dict_restr is used for sizing.
    sh_power_min : float, optional
        Minimum required space heating power at feeder node (for LHN).
        (default: None). If None is chosen, sh_power_min is not used.
        If value is set, this value is used as lower bound for boiler/chp
        sizing.
    pv_step : float, optional
        Defines discrete step of Pv sizing in m2 (default: 1). E.g.
        If minimum PV size is 8 m2, 9, 10, 11...up to max. rooftop area can
        be chosen as PV size.
    add_pv_prop : float, optional
        Defines additional probability of PV being changed, if only thermal
        mutation has been applied (defauft: 0). E.g. if boiler system has
        been changed to CHP, there is a change of add_pv_prob that also PV
        is mutated.
    add_bat_prob : float, optional
        Defines additional probability of BAT being changed, if only thermal
        mutation has been applied (defauft: 0). E.g. if boiler system has
        been changed to CHP, there is a change of add_pv_prob that also BAT
        is mutated.
    dict_heatloads : dict, optional
        Dict holding building ids as keys and design heat loads in Watt
        as values (default: None)
    """

    assert pv_min >= 0
    if sh_power_min is not None:
        assert sh_power_min > 0
    assert pv_step > 0
    assert add_pv_prop >= 0
    assert add_pv_prop <= 1
    assert add_bat_prob >= 0
    assert add_bat_prob <= 1

    if use_pv is False:
        #  Set add_pv_prop to zero
        add_pv_prop = 0
    if use_bat is False:
        #  Set add_bat_prob to zero
        add_bat_prob = 0

    #  Define default values
    #  #################################################################
    if list_options is None:
        list_options = ['boi', 'boi_tes', 'chp_boi_tes', 'chp_boi_eh_tes',
                        'hp_aw_eh', 'hp_ww_eh', 'hp_aw_boi', 'hp_ww_boi',
                        'hp_aw_eh_boi', 'hp_ww_eh_boi', 'bat', 'pv']

    if list_opt_prob is None:
        list_opt_prob = [0.1, 0.1, 0.2, 0.05, 0.1, 0.1, 0.05, 0.05, 0.05,
                         0.05, 0.05, 0.1]

    if list_lhn_opt is None:
        list_lhn_opt = ['chp_boi_tes', 'chp_boi_eh_tes',
                        'bat', 'pv', 'no_th_supply']

    if list_lhn_prob is None:
        list_lhn_prob = [0.1, 0.05, 0.05, 0.2, 0.6]

    # Assert checks
    #  #################################################################
    if list_opt_prob is not None and list_options is not None:
        assert len(list_options) == len(list_opt_prob)

    if list_lhn_opt is not None and list_lhn_prob is not None:
        assert len(list_lhn_opt) == len(list_lhn_prob)

    if abs(sum(list_opt_prob) - 1) > 0.0000001:
        msg = 'Sum of single probabilities of list_opt_prob is ' \
              + str(sum(list_opt_prob)) + ' and not 1!'
        raise AssertionError(msg)

    if abs(sum(list_lhn_prob) - 1) > 0.0000001:
        msg = 'Sum of single probabilities is of list_lhn_prob is ' \
              + str(sum(list_opt_prob)) + ' and not 1!'
        raise AssertionError(msg)

    # Search for LHN connection of n (if True, has LHN)
    has_lhn = findlhn.has_lhn_connection(ind=ind, id=n)

    #  Perform mutation
    #  #################################################################
    if has_lhn:
        #  Make random choice out of options (for LHN)
        select = np.random.choice(a=list_lhn_opt, p=list_lhn_prob)
    else:
        #  Make random choice out of options (for stand alone esys)
        select = np.random.choice(a=list_options, p=list_opt_prob)

    if select == 'boi':
        #  Generate boiler, only
        esyschanges.gen_boiler_only(ind=ind, n=n, dict_restr=dict_restr,
                                    dict_heatloads=dict_heatloads)

    elif select == 'boi_tes':
        #  Generate boiler and tes
        esyschanges.gen_boi_tes(ind=ind, n=n, dict_restr=dict_restr,
                                dict_heatloads=dict_heatloads)

    elif select == 'chp_boi_tes':
        #  Generate chp, boiler and tes
        esyschanges.gen_chp_boi_tes(ind=ind, n=n, dict_restr=dict_restr,
                                    dict_sh=dict_sh, sh_power_min=sh_power_min,
                                    dict_heatloads=dict_heatloads)

    elif select == 'chp_boi_eh_tes':
        #  Generate chp, boiler, eh and tes
        esyschanges.gen_chp_boi_eh_tes(ind=ind, n=n, dict_restr=dict_restr,
                                       dict_sh=dict_sh,
                                       sh_power_min=sh_power_min,
                                       dict_heatloads=dict_heatloads)

    elif select == 'hp_aw_eh':
        #  Generate aw hp, eh and tes
        esyschanges.gen_hp_aw_eh(ind=ind, n=n, dict_restr=dict_restr,
                                 dict_sh=dict_sh)

    elif select == 'hp_ww_eh':
        #  Generate bw hp, eh and tes
        esyschanges.gen_hp_ww_eh(ind=ind, n=n, dict_restr=dict_restr,
                                 dict_sh=dict_sh)

    elif select == 'hp_aw_boi':
        #  Generate aw hp, boi and tes
        esyschanges.gen_hp_aw_boi(ind=ind, n=n, dict_restr=dict_restr,
                                  dict_sh=dict_sh)

    elif select == 'hp_ww_boi':
        #  Generate ww hp, boi and tes
        esyschanges.gen_hp_ww_boi(ind=ind, n=n, dict_restr=dict_restr,
                                  dict_sh=dict_sh)

    elif select == 'hp_aw_eh_boi':
        #  Generate aw hp, boi, eh and tes
        esyschanges.gen_hp_aw_boi_eh(ind=ind, n=n, dict_restr=dict_restr,
                                     dict_sh=dict_sh)

    elif select == 'hp_ww_eh_boi':
        #  Generate ww hp, boi, eh and tes
        esyschanges.gen_hp_ww_boi_eh(ind=ind, n=n, dict_restr=dict_restr,
                                     dict_sh=dict_sh)

    elif select == 'bat' and use_bat:
        #  Generate battery, if not existent
        esyschanges.gen_or_del_bat(ind=ind, n=n, dict_restr=dict_restr)

    elif select == 'pv' and use_pv:

        pv_max = dict_max_pv_area[n]
        #  Generate PV
        esyschanges.gen_or_del_pv(ind=ind, n=n, pv_min=pv_min, pv_max=pv_max,
                                  pv_step=pv_step)
        #  As PV has already been changed, set add_pv_prob to zero
        add_pv_prop = 0

    elif select == 'no_th_supply':
        #  Eliminiate thermal supply (only valid for LHN connected buildings)
        esyschanges.set_th_supply_off(ind=ind, n=n)

    #  Add additional chance to add PV, if only thermal mutation has been
    #  applied
    if random.random() < add_pv_prop and use_pv:
        #  Mutate PV system
        pv_max = dict_max_pv_area[n]
        #  Generate PV
        esyschanges.gen_or_del_pv(ind=ind, n=n, pv_min=pv_min, pv_max=pv_max,
                                  pv_step=pv_step)

    if (ind[n]['chp'] > 0 or ind[n]['pv'] > 0) and use_bat:
        #  Add additional chance to add BAT, if only thermal mutation has been
        #  applied
        if random.random() < add_bat_prob:
            #  Generate battery, if not existent
            esyschanges.gen_or_del_bat(ind=ind, n=n, dict_restr=dict_restr)
