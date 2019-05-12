#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Scripts to change energy system configuration on single node of individuum
dict
"""
from __future__ import division

import random
import numpy as np
import math
import warnings

import pycity_resilience.ga.evolution.helpers.mod_list_esys_sizes as modlist


def gen_boiler_only(ind, n, dict_restr, dict_heatloads=None):
    """
    Generate boiler, only, scenario (no tes)

    Parameters
    ----------
    ind : dict
        Individuum dict
    n : int
        Id of building node in ind dict
    dict_restr : dict
        Dict holding possible energy system sizes
    dict_heatloads : dict, optional
        Dict holding building ids as keys and design heat loads in Watt
        as values (default: None)
    """

    if n not in ind.keys():
        msg = str(n) + ' is not in keys of individuum dict ind!'
        raise AssertionError(msg)

    if dict_heatloads is not None:
        #  Boiler
        list_boi_choice = \
            modlist.get_list_values_larger_than_ref(
                list_val=dict_restr['boi'],
                ref_val=dict_heatloads[n])
    else:
        list_boi_choice = dict_restr['boi']

    ind[n]['boi'] = random.choice(list_boi_choice)
    ind[n]['chp'] = 0
    ind[n]['hp_aw'] = 0
    ind[n]['hp_ww'] = 0
    ind[n]['eh'] = 0
    ind[n]['tes'] = 0
    if ind[n]['pv'] == 0:
        #  Delete battery
        ind[n]['bat'] = 0


def gen_boi_tes(ind, n, dict_restr, dict_heatloads=None):
    """
    Generate boiler, tes system

    Parameters
    ----------
    ind : dict
        Individuum dict
    n : int
        Id of building node in ind dict
    dict_restr : dict
        Dict holding possible energy system sizes
    dict_heatloads : dict, optional
        Dict holding building ids as keys and design heat loads in Watt
        as values (default: None)
    """

    if n not in ind.keys():
        msg = str(n) + ' is not in keys of individuum dict ind!'
        raise AssertionError(msg)

    if dict_heatloads is not None:
        #  Boiler
        list_boi_choice = \
            modlist.get_list_values_larger_than_ref(
                list_val=dict_restr['boi'],
                ref_val=dict_heatloads[n])
    else:
        list_boi_choice = dict_restr['boi']

    ind[n]['boi'] = random.choice(list_boi_choice)
    ind[n]['chp'] = 0
    ind[n]['hp_aw'] = 0
    ind[n]['hp_ww'] = 0
    ind[n]['eh'] = 0
    ind[n]['tes'] = random.choice(dict_restr['tes'])
    if ind[n]['pv'] == 0:
        #  Delete battery
        ind[n]['bat'] = 0


def gen_chp_boi_tes(ind, n, dict_restr, dict_sh=None, to_lhn=False,
                    sh_power_min=None, dict_heatloads=None):
    """
    Generate CHP, boiler, tes solution

    Parameters
    ----------
    ind : dict
        Individuum dict
    n : int
        Id of building node in ind dict
    dict_restr : dict
        Dict holding possible energy system sizes
    dict_sh : dict, optional
        Dictionary holding building node ids as keys and maximum space heating
        power values in Watt as dict values (default: None). If not None,
        used for size limitation. If None, dict_restr is used for sizing.
    to_lhn : bool, optional
        Defines, if energy system is added as feeder node in LHN
        (default: False)
    sh_power_min : float, optional
        Minimum required space heating power at feeder node (for LHN).
        (default: None). If None is chosen, sh_power_min is not used.
        If value is set, this value is used as lower bound for boiler/chp
        sizing.
    dict_heatloads : dict, optional
        Dict holding building ids as keys and design heat loads in Watt
        as values (default: None)
    """

    if n not in ind.keys():
        msg = str(n) + ' is not in keys of individuum dict ind!'
        raise AssertionError(msg)

    if dict_sh is not None and to_lhn is False and dict_heatloads is not None:
        #  Boiler
        list_boi_choice = \
            modlist.get_list_values_larger_than_ref(list_val=dict_restr['boi'],
                                            ref_val=dict_heatloads[n])
        #  CHP
        list_chp_choice = modlist. \
            get_list_values_smaller_than_ref(list_val=dict_restr['chp'],
                                             ref_val=dict_sh[n])
        #  TES
        list_tes_choice = modlist.\
            get_list_values_larger_than_ref(list_val=dict_restr['tes'],
                                            ref_val=500)
    else:
        list_boi_choice = dict_restr['boi']
        list_chp_choice = dict_restr['chp']
        list_tes_choice = dict_restr['tes']

    ind[n]['boi'] = random.choice(list_boi_choice)
    ind[n]['chp'] = random.choice(list_chp_choice)
    ind[n]['hp_aw'] = 0
    ind[n]['hp_ww'] = 0
    ind[n]['eh'] = 0
    ind[n]['tes'] = random.choice(list_tes_choice)

    #  If sh_power_min is set, check if boiler power and tes
    if sh_power_min is not None:
        count = 0
        while ind[n]['boi'] < sh_power_min:
            ind[n]['boi'] = random.choice(list_boi_choice)
            count += 1
            if count == 100:
                msg = 'Could not identify boiler which is large enough to ' \
                      'cover minimal space heating requirements for given LHN!'
                warnings.warn(msg)
                break
        count = 0
        while ind[n]['tes'] < 1000:
            ind[n]['tes'] = random.choice(list_tes_choice)
            count += 1
            if count == 100:
                msg = 'Could not identify tes which is large enough to cover' \
                      ' minimal space heating requirements for given LHN!'
                warnings.warn(msg)
                break
        count = 0
        while ind[n]['chp'] > sh_power_min:
            ind[n]['chp'] = random.choice(list_chp_choice)
            count += 1
            if count == 100:
                msg = 'Could not identify CHP which is smaller than ' \
                      'reference space heating power for LHN!'
                warnings.warn(msg)
                break


def gen_chp_boi_eh_tes(ind, n, dict_restr, dict_sh=None, sh_power_min=None,
                       dict_heatloads=None):
    """
    Generate CHP, boiler, electr. heater, tes solution

    Parameters
    ----------
    ind : dict
        Individuum dict
    n : int
        Id of building node in ind dict
    dict_restr : dict
        Dict holding possible energy system sizes
    dict_sh : dict, optional
        Dictionary holding building node ids as keys and maximum space heating
        power values in Watt as dict values (default: None). If not None,
        used for size limitation. If None, dict_restr is used for sizing.
    sh_power_min : float, optional
        Minimum required space heating power at feeder node (for LHN).
        (default: None). If None is chosen, sh_power_min is not used.
        If value is set, this value is used as lower bound for boiler/chp
        sizing.
    dict_heatloads : dict, optional
        Dict holding building ids as keys and design heat loads in Watt
        as values (default: None)
    """

    if n not in ind.keys():
        msg = str(n) + ' is not in keys of individuum dict ind!'
        raise AssertionError(msg)

    if dict_sh is not None and dict_heatloads is not None:
        #  Boiler
        list_boi_choice = \
            modlist.get_list_values_larger_than_ref(list_val=dict_restr['boi'],
                                            ref_val=dict_heatloads[n])
        #  CHP
        list_chp_choice = modlist. \
            get_list_values_smaller_than_ref(list_val=dict_restr['chp'],
                                             ref_val=dict_sh[n])
        #  TES
        list_tes_choice = modlist.\
            get_list_values_larger_than_ref(list_val=dict_restr['tes'],
                                            ref_val=500)
    else:
        list_boi_choice = dict_restr['boi']
        list_chp_choice = dict_restr['chp']
        list_tes_choice = dict_restr['tes']

    ind[n]['boi'] = random.choice(list_boi_choice)
    ind[n]['chp'] = random.choice(list_chp_choice)
    ind[n]['hp_aw'] = 0
    ind[n]['hp_ww'] = 0
    ind[n]['eh'] = random.choice(dict_restr['eh'])
    ind[n]['tes'] = random.choice(list_tes_choice)

    #  If sh_power_min is set, check if boiler power and tes
    if sh_power_min is not None:
        count = 0
        while ind[n]['boi'] < sh_power_min:
            ind[n]['boi'] = random.choice(list_boi_choice)
            count += 1
            if count == 100:
                msg = 'Could not identify boiler which is large enough to ' \
                      'cover minimal space heating requirements for given LHN!'
                warnings.warn(msg)
                break
        count = 0
        while ind[n]['tes'] < 1000:
            ind[n]['tes'] = random.choice(list_tes_choice)
            count += 1
            if count == 100:
                msg = 'Could not identify tes which is large enough to cover' \
                      ' minimal space heating requirements for given LHN!'
                warnings.warn(msg)
                break
        count = 0
        while ind[n]['chp'] > sh_power_min:
            ind[n]['chp'] = random.choice(list_chp_choice)
            count += 1
            if count == 100:
                msg = 'Could not identify CHP which is smaller than ' \
                      'reference space heating power for LHN!'
                warnings.warn(msg)
                break


def gen_hp_aw_eh(ind, n, dict_restr, dict_sh=None):
    """
    Generate air water heat pump, electr. heater, storage solution

    Parameters
    ----------
    ind : dict
        Individuum dict
    n : int
        Id of building node in ind dict
    dict_restr : dict
        Dict holding possible energy system sizes
    dict_sh : dict, optional
        Dictionary holding building node ids as keys and maximum space heating
        power values in Watt as dict values (default: None). If not None,
        used for size limitation. If None, dict_restr is used for sizing.
    """

    if n not in ind.keys():
        msg = str(n) + ' is not in keys of individuum dict ind!'
        raise AssertionError(msg)

    if dict_sh is not None:
        #  Air/water heat pump
        list_hp_aw_choice = modlist. \
            get_list_values_larger_than_ref(list_val=dict_restr['hp_aw'],
                                            ref_val=dict_sh[n])
        #  TES
        list_tes_choice = modlist. \
            get_list_values_larger_than_ref(list_val=dict_restr['tes'],
                                            ref_val=300)
    else:
        list_hp_aw_choice = dict_restr['hp_aw']
        list_tes_choice = dict_restr['tes']

    ind[n]['boi'] = 0
    ind[n]['chp'] = 0
    ind[n]['hp_aw'] = random.choice(list_hp_aw_choice)
    ind[n]['hp_ww'] = 0
    ind[n]['eh'] = random.choice(dict_restr['eh'])
    ind[n]['tes'] = random.choice(list_tes_choice)
    if ind[n]['pv'] == 0:
        #  Delete battery
        ind[n]['bat'] = 0


def gen_hp_ww_eh(ind, n, dict_restr, dict_sh=None):
    """
    Generate water/water heat pump, electr. heater, storage solution

    Parameters
    ----------
    ind : dict
        Individuum dict
    n : int
        Id of building node in ind dict
    dict_restr : dict
        Dict holding possible energy system sizes
    dict_sh : dict, optional
        Dictionary holding building node ids as keys and maximum space heating
        power values in Watt as dict values (default: None). If not None,
        used for size limitation. If None, dict_restr is used for sizing.
    """

    if n not in ind.keys():
        msg = str(n) + ' is not in keys of individuum dict ind!'
        raise AssertionError(msg)

    if dict_sh is not None:
        #  water/water heat pump
        list_hp_ww_choice = modlist. \
            get_list_values_larger_than_ref(list_val=dict_restr['hp_ww'],
                                            ref_val=dict_sh[n])
        #  TES
        list_tes_choice = modlist. \
            get_list_values_larger_than_ref(list_val=dict_restr['tes'],
                                            ref_val=300)
    else:
        list_hp_ww_choice = dict_restr['hp_ww']
        list_tes_choice = dict_restr['tes']

    ind[n]['boi'] = 0
    ind[n]['chp'] = 0
    ind[n]['hp_aw'] = 0
    ind[n]['hp_ww'] = random.choice(list_hp_ww_choice)
    ind[n]['eh'] = random.choice(dict_restr['eh'])
    ind[n]['tes'] = random.choice(list_tes_choice)
    if ind[n]['pv'] == 0:
        #  Delete battery
        ind[n]['bat'] = 0


def gen_hp_aw_boi(ind, n, dict_restr, dict_sh=None):
    """
    Generate air water heat pump, boiler, storage solution

    Parameters
    ----------
    ind : dict
        Individuum dict
    n : int
        Id of building node in ind dict
    dict_restr : dict
        Dict holding possible energy system sizes
    dict_sh : dict, optional
        Dictionary holding building node ids as keys and maximum space heating
        power values in Watt as dict values (default: None). If not None,
        used for size limitation. If None, dict_restr is used for sizing.
    """

    if n not in ind.keys():
        msg = str(n) + ' is not in keys of individuum dict ind!'
        raise AssertionError(msg)

    ind[n]['boi'] = random.choice(dict_restr['boi'])
    ind[n]['chp'] = 0
    ind[n]['hp_aw'] = random.choice(dict_restr['hp_aw'])
    ind[n]['hp_ww'] = 0
    ind[n]['eh'] = 0
    ind[n]['tes'] = random.choice(dict_restr['tes'])
    if ind[n]['pv'] == 0:
        #  Delete battery
        ind[n]['bat'] = 0


def gen_hp_ww_boi(ind, n, dict_restr, dict_sh=None):
    """
    Generate water/water heat pump, boiler, storage solution

    Parameters
    ----------
    ind : dict
        Individuum dict
    n : int
        Id of building node in ind dict
    dict_restr : dict
        Dict holding possible energy system sizes
    dict_sh : dict, optional
        Dictionary holding building node ids as keys and maximum space heating
        power values in Watt as dict values (default: None). If not None,
        used for size limitation. If None, dict_restr is used for sizing.
    """

    if n not in ind.keys():
        msg = str(n) + ' is not in keys of individuum dict ind!'
        raise AssertionError(msg)

    ind[n]['boi'] = random.choice(dict_restr['boi'])
    ind[n]['chp'] = 0
    ind[n]['hp_aw'] = 0
    ind[n]['hp_ww'] = random.choice(dict_restr['hp_ww'])
    ind[n]['eh'] = 0
    ind[n]['tes'] = random.choice(dict_restr['tes'])
    if ind[n]['pv'] == 0:
        #  Delete battery
        ind[n]['bat'] = 0


def gen_hp_aw_boi_eh(ind, n, dict_restr, dict_sh=None):
    """
    Generate air water heat pump, boiler, electr. heater, storage solution

    Parameters
    ----------
    ind : dict
        Individuum dict
    n : int
        Id of building node in ind dict
    dict_restr : dict
        Dict holding possible energy system sizes
    dict_sh : dict, optional
        Dictionary holding building node ids as keys and maximum space heating
        power values in Watt as dict values (default: None). If not None,
        used for size limitation. If None, dict_restr is used for sizing.
    """

    if n not in ind.keys():
        msg = str(n) + ' is not in keys of individuum dict ind!'
        raise AssertionError(msg)

    ind[n]['boi'] = random.choice(dict_restr['boi'])
    ind[n]['chp'] = 0
    ind[n]['hp_aw'] = random.choice(dict_restr['hp_aw'])
    ind[n]['hp_ww'] = 0
    ind[n]['eh'] = random.choice(dict_restr['eh'])
    ind[n]['tes'] = random.choice(dict_restr['tes'])
    if ind[n]['pv'] == 0:
        #  Delete battery
        ind[n]['bat'] = 0


def gen_hp_ww_boi_eh(ind, n, dict_restr, dict_sh=None):
    """
    Generate water/water heat pump, boiler, electr. heater, storage solution

    Parameters
    ----------
    ind : dict
        Individuum dict
    n : int
        Id of building node in ind dict
    dict_restr : dict
        Dict holding possible energy system sizes
    dict_sh : dict, optional
        Dictionary holding building node ids as keys and maximum space heating
        power values in Watt as dict values (default: None). If not None,
        used for size limitation. If None, dict_restr is used for sizing.
    """

    if n not in ind.keys():
        msg = str(n) + ' is not in keys of individuum dict ind!'
        raise AssertionError(msg)

    ind[n]['boi'] = random.choice(dict_restr['boi'])
    ind[n]['chp'] = 0
    ind[n]['hp_aw'] = 0
    ind[n]['hp_ww'] = random.choice(dict_restr['hp_ww'])
    ind[n]['eh'] = random.choice(dict_restr['eh'])
    ind[n]['tes'] = random.choice(dict_restr['tes'])
    if ind[n]['pv'] == 0:
        #  Delete battery
        ind[n]['bat'] = 0


def gen_or_del_bat(ind, n, dict_restr):
    """
    Generate or delete battery. If existent, delete it. If not existent,
    generate battery.

    Parameters
    ----------
    ind : dict
        Individuum dict
    n : int
        Id of building node in ind dict
    dict_restr : dict
        Dict holding possible energy system sizes
    """

    if n not in ind.keys():
        msg = str(n) + ' is not in keys of individuum dict ind!'
        raise AssertionError(msg)

    if ind[n]['bat'] == 0:
        if ind[n]['chp'] > 0 or ind[n]['pv'] > 0:
            ind[n]['bat'] = random.choice(dict_restr['bat'])
    else:
        #  Erase battery
        ind[n]['bat'] = 0


def gen_or_del_pv(ind, n, pv_min, pv_max, pv_step=1):
    """
    Generate or delete photovoltaic. If existent, delete it. If not existent,
    generate photovoltaic module.

    Parameters
    ----------
    ind : dict
        Individuum dict
    n : int
        Id of building node in ind dict
    pv_min : float
        Minimum possible PV area in m2
    pv_max : float
        Maximum possible PV area in m2
    pv_step : float, optional
        Defines discrete step of Pv sizing in m2 (default: 1). E.g.
        If minimum PV size is 8 m2, 9, 10, 11...up to max. rooftop area can
        be chosen as PV size.
    """

    if pv_max < pv_min:
        msg = 'pv_max is smaller than minimal required pv size pv_min. ' \
              'Thus, going to exit gen_or_del_pv().'
        warnings.warn(msg)

    assert pv_min >= 0
    assert pv_step > 0

    if n not in ind.keys():
        msg = str(n) + ' is not in keys of individuum dict ind!'
        raise AssertionError(msg)

    if ind[n]['pv'] == 0:

        min_ref = round(pv_min, 0)
        max_ref = math.ceil(pv_max)

        if max_ref > min_ref:

            array_choices = np.arange(start=min_ref, stop=max_ref, step=pv_step)

            pv_area = np.random.choice(array_choices)

        elif max_ref == min_ref:

            pv_area = min_ref + 0.0

        else:

            pv_area = 0

        ind[n]['pv'] = pv_area
    else:
        #  Erase PV
        ind[n]['pv'] = 0


def set_th_supply_off(ind, n):
    """
    Set all thermal devices to zero (necessary for LHN supply, only)

    Parameters
    ----------
    ind : dict
        Individuum dict
    n : int
        Id of building node in ind dict
    """

    if n not in ind.keys():
        msg = str(n) + ' is not in keys of individuum dict ind!'
        raise AssertionError(msg)

    ind[n]['boi'] = 0
    ind[n]['chp'] = 0
    ind[n]['hp_aw'] = 0
    ind[n]['hp_ww'] = 0
    ind[n]['eh'] = 0
    ind[n]['tes'] = 0
    if ind[n]['pv'] == 0:
        #  Delete battery
        ind[n]['bat'] = 0
