#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

"""
from __future__ import division

import copy
import warnings
import random
import math

import pycity_resilience.ga.analyse.find_lhn as findlhn
import pycity_resilience.ga.analyse.analyse as analyse
import pycity_resilience.ga.evolution.esys_changes as esyschanges
import pycity_resilience.ga.evolution.helpers.mod_list_esys_sizes as modlist


def check_ind_is_valid(ind):
    """
    Check if generated individuum dict ind is valid (e.g. all nodes in 'lhn'
    are also keys. 'lhn' tag is present.

    Parameters
    ----------
    ind

    Returns
    -------
    is_valid : bool
        True, if ind is valid object. False, if ind is incorrect
    """

    is_valid = True

    if 'lhn' not in ind:
        msg = 'lhn tag is not on individuum dict!'
        warnings.warn(msg)
        return False

    if not isinstance(ind['lhn'], list):
        msg = 'lhn tag is not of instance list!'
        warnings.warn(msg)
        return False

    if len(ind['lhn']) > 0:  # Has LHN networks
        for sublhn in ind['lhn']:
            for n in sublhn:
                if n not in ind.keys():
                    msg = 'Key ' + str(n) + ' is not in ind.keys()!'
                    warnings.warn(msg)
                    return False
    else:
        # Check that 'lhn' = []
        if ind['lhn'] != []:  # pragma: no cover
            msg = 'lhn tag has value ' + str(
                ind['lhn']) + ', which is invalid'
            warnings.warn(msg)
            return False

    return is_valid


def check_no_hp_in_lhn(ind, do_correction=True):
    """
    Checks if individuum dict holds HP within LHN. If yes and do_correction is
    True, erases HP from LHN.

    Parameters
    ----------
    ind : dict
        Individuum dict for GA run
    do_correction : bool, optional
        Defines, if ind dict should be modified, if necessary (default: True).
        If True, can erase HP form LHN network building nodes.

    Returns
    -------
    is_correct : bool
        Boolean to define, if no heat pump is found within ind dict.
        If True, no heat pump has been found. If False, HP exists in LHN
        network
    """

    is_correct = True

    # check if heatpump is connected to LHN at ind1
    if len(ind['lhn']) > 0:
        for subcity in ind['lhn']:
            for node in subcity:
                if ind[node]['hp_aw'] > 0 or ind[node]['hp_ww'] > 0:
                    is_correct = False
                    if do_correction:
                        # if node has lhn and hp delete lhn connection
                        subcity.remove(node)
                    else:  # pragma: no cover
                        break

    return is_correct


def check_lhn_has_min_two_build(ind, do_correction=True):
    """
    Checks if individuum dict has, at least, two buildings. If not, erases
    LHN system.

    Parameters
    ----------
    ind : dict
        Individuum dict for GA run
    do_correction : bool, optional
        Defines, if ind dict should be modified, if necessary (default: True).
        If True, erased LHN lists with only one or zero buildings.

    Returns
    -------
    is_correct : bool
        Boolean to define, if all LHN hold, at least, two buildings
        (respectively one LHN edge)
    """

    is_correct = True

    list_del_idx = []

    if len(ind['lhn']) > 0:
        for i in range(len(ind['lhn'])):
            list_sub_lhn = ind['lhn'][i]  # Get LHN sublist
            if len(list_sub_lhn) <= 1:  # If max. holds one element
                is_correct = False
                list_del_idx.append(i)  # Add index to delete list
                if do_correction is False:  # pragma: no cover
                    break

        if do_correction:
            for i in list_del_idx:
                del ind['lhn'][i]

        if 'lhn' not in ind:
            ind['lhn'] = []

    return is_correct


def check_lhn_th_supply(ind, do_correction=True, do_random=True,
                        dict_restr=None, dict_max_pv_area=None,
                        dict_heatloads=None, dict_sh=None, pv_min=None,
                        pv_step=1,
                        use_pv=False, add_pv_prop=0):
    """
    Check if each sub-LHN in ind dict has, at least, one thermal feeder

    Parameters
    ----------
    ind : dict
        Individuum dict for GA run
    do_correction : bool, optional
        Defines, if ind dict should be modified, if necessary (default: True).
        If True, adds large scale boiler, CHP and tes to single feeder node
        of LHN.
    do_random : bool, optional
        If True, uses random values to generate feeder node (default: True).
        If False, uses default values
        ind[build_id]['boi'] = 500000  # in Watt
        ind[build_id]['chp'] = 10000  # in Watt th. power
        ind[build_id]['tes'] = 5000  # in liters
    dict_restr : dict, optional
        Dict holding possible energy system sizes (default: None)
    dict_max_pv_area : dict, optional
        Dict holding maximum usable PV area values in m2 per building
        (default: None)
    dict_heatloads : dict, optional
        Dict holding building ids as keys and design heat loads in Watt
        as values (default: None)
    dict_sh : dict, optional
        Dictionary holding building node ids as keys and maximum space heating
        power values in Watt as dict values (default: None). If not None,
        used for size limitation. If None, dict_restr is used for sizing.
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

    Returns
    -------
    is_correct : bool
        Boolean to define, if all sub-LHNs in ind dict have, at least, one
        thermal feeder
    """

    if do_correction and do_random:
        if dict_restr is None:
            msg = 'dict_restr cannot be None for random mode correction!'
            raise AssertionError(msg)
        if dict_heatloads is None:
            msg = 'dict_heatloads cannot be None for random mode correction!'
            raise AssertionError(msg)
        if dict_max_pv_area is None and use_pv:
            msg = 'dict_max_pv_area cannot be None for random mode ' \
                  'correction with PV!'
            raise AssertionError(msg)
        if pv_min is None and use_pv:
            msg = 'pv_min cannot be None for random mode correction with PV!'
            raise AssertionError(msg)

    list_failed_sublhn_idx = []

    if len(ind['lhn']) > 0:
        for i in range(len(ind['lhn'])):  # Loop over lists of LHN networks
            is_correct = False
            list_lhn_ids = ind['lhn'][i]
            for n in list_lhn_ids:  # Loop over nodes in LHN network
                if ind[n]['boi'] > 0 or ind[n]['chp'] > 0 or ind[n]['eh']:
                    is_correct = True  # pragma: no cover
                    break  # pragma: no cover
            if is_correct is False:
                list_failed_sublhn_idx.append(i)

        if do_correction and len(list_failed_sublhn_idx) > 0:
            if do_random:
                for idx in list_failed_sublhn_idx:
                    #  Randomly select feeder node of LHN subnetwork
                    build_id = random.choice(ind['lhn'][idx])

                    #  Calculate sh_power_min
                    sh_power_min = 0
                    #  Sum up design heat load values
                    for n in ind['lhn'][idx]:
                        sh_power_min += dict_heatloads[n]

                    #  Use buffer factor for downscaling
                    if len(ind['lhn'][idx]) >= 50:
                        sh_power_min *= 0.8
                    elif len(ind['lhn'][idx]) >= 15:
                        sh_power_min *= 0.9

                    #  Generate chp, boiler and tes
                    esyschanges.gen_chp_boi_tes(ind=ind, n=build_id,
                                                dict_restr=dict_restr,
                                                dict_sh=dict_sh,
                                                sh_power_min=sh_power_min,
                                                to_lhn=True,
                                                dict_heatloads=dict_heatloads)

                    #  Perform PV feeder mutation
                    if random.random() < add_pv_prop and use_pv:
                        #  Mutate PV system
                        pv_max = dict_max_pv_area[build_id]
                        #  Generate PV
                        esyschanges.gen_or_del_pv(ind=ind, n=build_id,
                                                  pv_min=pv_min,
                                                  pv_max=pv_max,
                                                  pv_step=pv_step)

            else:
                for idx in list_failed_sublhn_idx:
                    #  Randomly select feeder node of LHN subnetwork
                    build_id = random.choice(ind['lhn'][idx])

                    #  Add boiler
                    ind[build_id]['boi'] = 500000  # in Watt
                    ind[build_id]['chp'] = 10000  # in Watt th. power
                    ind[build_id]['tes'] = 5000  # in liters

                    #  Perform PV feeder mutation
                    if random.random() < add_pv_prop and use_pv:
                        #  Mutate PV system
                        pv_max = dict_max_pv_area[build_id]
                        #  Generate PV
                        esyschanges.gen_or_del_pv(ind=ind, n=build_id,
                                                  pv_min=pv_min,
                                                  pv_max=pv_max,
                                                  pv_step=pv_step)

    else:  # pragma: no cover
        # msg = 'No LHN found in ' + str(ind)
        # warnings.warn(msg)
        is_correct = True

    return is_correct


def check_pv_max_areas(ind, dict_max_pv_area, do_correction=True):
    """
    Checks if used PV area is smaller or equal to maximum usable PV rooftop
    area. If not defines maximum usable PV rooftop area as new PV area.

    Parameters
    ----------
    ind : dict
        Individuum dict for GA run
    dict_max_pv_area : dict (of floats)
        Dictionary holding building nodes as keys and max. usable pv areas
        in m2 as values
    do_correction : bool, optional
        Defines, if ind dict should be modified, if necessary (default: True).

    Returns
    -------
    is_correct : bool
        Boolean to define, if used PV area is within limitations of maximum
        usable PV area
    """

    is_correct = True

    list_ids = analyse.get_build_ids_ind(ind=ind)

    for n in list_ids:
        if ind[n]['pv'] > dict_max_pv_area[n]:
            is_correct = False

            if do_correction:
                ind[n]['pv'] = math.ceil(dict_max_pv_area[n])
            else:  # pragma: no cover
                break

    return is_correct


def check_bat_only_with_pv_or_chp(ind, do_correction=True):
    """
    Check if battery is only installed when CHP or PV system exist

    Parameters
    ----------
    ind : dict
        Individuum dict for GA run
    do_correction : bool, optional
        Defines, if ind dict should be modified, if necessary (default: True).
        If True, erases all batteries in buildings without CHP or PV

    Returns
    -------
    is_correct : bool
        Boolean to define, if all batteries are installed in buildings
        with CHP or PV system
    """

    is_correct = True

    list_del = []

    list_ids = analyse.get_build_ids_ind(ind=ind)

    for n in list_ids:
        if ind[n]['bat'] > 0:
            if ind[n]['chp'] == 0 and ind[n]['pv'] == 0:
                is_correct = False
                if do_correction is False:  # pragma: no cover
                    break
                else:
                    list_del.append(n)

    if do_correction:
        for n in list_del:
            ind[n]['bat'] = 0

    return is_correct


def check_stand_alone_build_th(ind, do_correction=True, do_random=True,
                               dict_sh=None, dict_restr=None,
                               pv_min=None, pv_step=1, use_pv=False,
                               add_pv_prop=0, dict_max_pv_area=None,
                               dict_heatloads=None):
    """
    Check if stand alone buildings (no LHN) have thermal energy supply.

    Parameters
    ----------
    ind : dict
        Individuum dict for GA run
    do_correction : bool, optional
        Defines, if ind dict should be modified, if necessary (default: True).
        If True, randomly adds heating device to stand-alone building without
        thermal supply and without LHN connection
    do_random : bool, optional
        If True, uses random values to generate th. supply (default: True).
        If False, uses default values
    dict_restr : dict
        Dict holding possible energy system sizes
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
    dict_max_pv_area : dict, optional
        Dict holding maximum usable PV area values in m2 per building
        (default: None)
    dict_heatloads : dict, optional
        Dict holding building ids as keys and design heat loads in Watt
        as values (default: None)

    Returns
    -------
    is_correct : bool
        Boolean to define, if all stand-alone buildings (no LHN connection)
        have a thermal energy supply unit
    """

    if do_random:
        if dict_sh is None:
            msg = 'dict_sh cannot be None, if do_random is True in ' \
                  'check_stand_alone_build_th'
            raise AssertionError(msg)
        if dict_heatloads is None:
            msg = 'dict_heatloads cannot be None, if do_random is True in ' \
                  'check_stand_alone_build_th'
            raise AssertionError(msg)
        if dict_restr is None:
            msg = 'dict_restr cannot be None, if do_random is True in ' \
                  'check_stand_alone_build_th'
            raise AssertionError(msg)
        if use_pv:
            if dict_max_pv_area is None:
                msg = 'dict_max_pv_area cannot be None, if do_random is ' \
                      'True and use_pv is True in check_stand_alone_build_th'
                raise AssertionError(msg)

    is_correct = True

    list_lhn = []

    #  Generate list with all LHN connected building ids
    if len(ind['lhn']) > 0:
        for sublhn in ind['lhn']:
            for n in sublhn:
                list_lhn.append(n)

    # Generate difference to get all building ids without LHN connection
    list_non_lhn = list(set(ind.keys()) - set(list_lhn))
    #  Remove 'lhn' tag
    list_non_lhn.remove('lhn')

    list_ids_no_th = []  # List with build. ids without own th. supply

    for n in list_non_lhn:
        if (ind[n]['boi'] == 0 and ind[n]['chp'] == 0 and
                ind[n]['hp_aw'] == 0 and ind[n]['hp_ww'] == 0
                and ind[n]['eh'] == 0):
            is_correct = False
            list_ids_no_th.append(n)
            if do_correction is False:  # pragma: no cover
                break

    if do_correction:
        for n in list_ids_no_th:
            #  Randomly select esys type
            select = random.choice(['boi', 'chp', 'hp_ww', 'hp_aw'])

            #  Randomly choose size of esys
            if do_random:
                #  Define list with allowed sizes
                #  ##########################################################
                if dict_sh is not None and dict_heatloads is not None:
                    #  Boiler
                    list_boi_choice = \
                        modlist.get_list_values_larger_than_ref(
                            list_val=dict_restr['boi'],
                            ref_val=dict_heatloads[n])
                    #  Air/water heat pump
                    list_hp_aw_choice = modlist. \
                        get_list_values_larger_than_ref(
                        list_val=dict_restr['hp_aw'],
                        ref_val=dict_sh[n])
                    #  Water/water heat pump
                    list_hp_ww_choice = modlist. \
                        get_list_values_larger_than_ref(
                        list_val=dict_restr['hp_ww'],
                        ref_val=dict_sh[n])

                    #  CHP
                    list_chp_choice = modlist. \
                        get_list_values_smaller_than_ref(
                        list_val=dict_restr['chp'],
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
                # ###########################################################

                if select == 'boi':
                    ind[n]['boi'] = random.choice(list_boi_choice)
                elif select == 'chp':
                    ind[n]['boi'] = random.choice(list_boi_choice)
                    ind[n]['chp'] = random.choice(list_chp_choice)
                    ind[n]['tes'] = random.choice(dict_restr['tes'])
                elif select == 'hp_ww':
                    ind[n]['hp_ww'] = random.choice(list_hp_ww_choice)
                    ind[n]['eh'] = random.choice(dict_restr['eh'])
                    ind[n]['tes'] = random.choice(dict_restr['tes'])
                elif select == 'hp_aw':
                    ind[n]['hp_aw'] = random.choice(list_hp_aw_choice)
                    ind[n]['eh'] = random.choice(dict_restr['eh'])
                    ind[n]['tes'] = random.choice(dict_restr['tes'])
                else:  # pragma: no cover
                    msg = 'Unknown string selected by random.choice'
                    raise AssertionError(msg)

                #  Perform PV feeder mutation
                if random.random() < add_pv_prop and use_pv:
                    #  Mutate PV system
                    pv_max = dict_max_pv_area[n]
                    #  Generate PV
                    esyschanges.gen_or_del_pv(ind=ind, n=n,
                                              pv_min=pv_min,
                                              pv_max=pv_max,
                                              pv_step=pv_step)

            else:
                #  Fixed dimensioning
                if select == 'boi':
                    ind[n]['boi'] = 50000
                elif select == 'chp':
                    ind[n]['boi'] = 50000
                    ind[n]['chp'] = 3000
                    ind[n]['tes'] = 2000
                elif select == 'hp_ww':
                    ind[n]['hp_ww'] = 20000
                    ind[n]['eh'] = 10000
                    ind[n]['tes'] = 500
                elif select == 'hp_aw':
                    ind[n]['hp_aw'] = 10000
                    ind[n]['eh'] = 10000
                    ind[n]['tes'] = 500
                else:  # pragma: no cover
                    msg = 'Unknown string selected by random.choice'
                    raise AssertionError(msg)

    return is_correct


def check_no_chp_plus_hp(ind, do_correction=True):
    """

    Parameters
    ----------
    ind : dict
        Individuum dict for GA run
    do_correction : bool, optional
        Defines, if ind dict should be modified, if necessary (default: True).
        If True, deletes CHP or HP system.

    Returns
    -------
    is_correct : bool
        Boolean to define, if there is no building with CHP and HP at the same
        time
    """

    is_correct = True

    list_ids = analyse.get_build_ids_ind(ind=ind)

    list_ids_del = []

    for n in list_ids:
        if ((ind[n]['chp'] > 0 and ind[n]['hp_aw'] > 0) or
                (ind[n]['chp'] > 0 and ind[n]['hp_ww'] > 0)):
            is_correct = False
            if do_correction is False:  # pragma: no cover
                break
            else:
                list_ids_del.append(n)

    if do_correction:
        for n in list_ids_del:

            #  If building is LHN connected, delete heat pumps
            if findlhn.has_lhn_connection(ind=ind, id=n) is True:
                ind[n]['hp_aw'] = 0
                ind[n]['hp_ww'] = 0
                ind[n]['eh'] = 0
            else:  # No LHN connection
                select = random.choice(['chp', 'hp'])
                if select == 'chp':  # Delete heat pumps
                    ind[n]['hp_aw'] = 0
                    ind[n]['hp_ww'] = 0
                    ind[n]['eh'] = 0
                elif select == 'hp':  # Delete CHP
                    ind[n]['chp'] = 0

    return is_correct


def check_no_boi_lhn_only(ind, dict_restr, dict_sh=None,
                          do_correction=True, dict_heatloads=None):
    """
    Checks if boiler-lhn or eh-lhn only combinations exist. If yes,
    correct them by addding CHP system or deleting LHN and add boilers, only.

    Parameters
    ----------
    ind : dict
        Individuum dict for GA run
    dict_restr : dict
        Dict holding possible energy system sizes (default: None)
    dict_sh : dict, optional
        Dictionary holding building node ids as keys and maximum space heating
        power values in Watt as dict values (default: None). If not None,
        used for size limitation. If None, dict_restr is used for sizing.
        (default: None)
    do_correction : bool, optional
        Defines, if ind dict should be modified, if necessary (default: True).
        If True, deletes CHP or HP system.
    dict_heatloads : dict, optional
        Dict holding building ids as keys and design heat loads in Watt
        as values (default: None)

    Returns
    -------
    is_correct : bool
        Boolean to define, if there is no building with CHP and HP at the same
        time
    """

    is_correct = True

    list_subcities = []

    # check if heatpump is connected to LHN at ind1
    if len(ind['lhn']) > 0:
        for subcity in ind['lhn']:

            #  Assume supply is incorrect, until CHP is found
            has_chp = False

            for node in subcity:
                if ind[node]['chp'] > 0:
                    has_chp = True
                    break

            if has_chp is False:
                is_correct = False
                list_subcities.append(subcity)

    #  If has_chp is False and do_correction is True, add CHP
    if do_correction and is_correct is False:

        for subcity in list_subcities:

            sh_max = 0
            id_sh_max = None

            if dict_sh is not None:
                #  Search for node id in subcity, which has highest SH demand
                for node in subcity:
                    if dict_sh[node] > sh_max:
                        sh_max = dict_sh[node]
                        id_sh_max = node
            else:
                #  Random choice
                id_sh_max = random.choice(subcity)

            #  Calculate sh_power_min
            sh_power_min = 0

            if dict_heatloads is not None:
                #  Sum up space heating power demands
                for n in subcity:
                    sh_power_min += dict_heatloads[n]

                #  Use buffer factor for downscaling
                if len(subcity) >= 50:
                    sh_power_min *= 0.8
                elif len(subcity) >= 15:
                    sh_power_min *= 0.9

            else:  # Set fixed parameter
                sh_power_min = 500000

            #  Add CHP to node id_sh_max
            #  Generate chp, boiler and tes
            esyschanges.gen_chp_boi_tes(ind=ind, n=id_sh_max,
                                        dict_restr=dict_restr,
                                        dict_sh=dict_sh,
                                        sh_power_min=sh_power_min,
                                        to_lhn=True,
                                        dict_heatloads=dict_heatloads)

            #  Delete all other thermal feeders in LHN
            for node in subcity:
                if node != id_sh_max:
                    ind[node]['boi'] = 0
                    ind[node]['chp'] = 0
                    ind[node]['hp_aw'] = 0
                    ind[node]['hp_ww'] = 0
                    ind[node]['eh'] = 0
                    ind[node]['tes'] = 0

    return is_correct


def run_all_checks(ind, dict_max_pv_area, dict_restr=None, dict_sh=None,
                   pv_min=None, pv_step=1, use_pv=False, add_pv_prop=0,
                   do_random=True, prevent_boi_lhn=True, dict_heatloads=None):
    """
    Performs all checks on individuum. If invalid energy system or network,
    automatically corrects it.

    Parameters
    ----------
    ind : individuum
        Individuum of DEAP toolbox
    dict_max_pv_area : dict
        Dict holding maximum usable PV area values in m2 per building
    dict_restr : dict, optional
        Dict holding possible energy system sizes (default: None)
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
    do_random : bool, optional
        If True, uses random values to generate feeder node (default: True),
        when LHN has to be corrected.
        If False, uses default values
        ind[build_id]['boi'] = 500000  # in Watt
        ind[build_id]['chp'] = 10000  # in Watt th. power
        ind[build_id]['tes'] = 5000  # in liters
    prevent_boi_lhn : bool, optional
        Prevent boi/eh LHN combinations (without CHP) (default: True).
        If True, adds CHPs to LHN systems without CHP
    dict_heatloads : dict, optional
        Dict holding building ids as keys and design heat loads in Watt
        as values (default: None)
    """

    #  Check PV
    ############################
    #  Check if max usable_pv area is harmed.
    #  If yes, reset pv area value to max. possible usable roof area
    if dict_max_pv_area is not None:
        check_pv_max_areas(ind=ind, dict_max_pv_area=dict_max_pv_area)

    #  Check thermal supply of stand alone buildings
    #########################################################################
    check_stand_alone_build_th(ind=ind, dict_sh=dict_sh, dict_restr=dict_restr,
                               pv_min=pv_min, pv_step=pv_step, use_pv=use_pv,
                               add_pv_prop=add_pv_prop,
                               dict_max_pv_area=dict_max_pv_area,
                               dict_heatloads=dict_heatloads)

    #  Check that no CHP plus HP is build
    check_no_chp_plus_hp(ind=ind)

    #  Check battery
    ############################
    check_bat_only_with_pv_or_chp(ind=ind)

    #  Check LHN constraints
    ############################

    #  Check if heatpump is connected to LHN at ind
    check_no_hp_in_lhn(ind=ind)

    #  If LHN subcity has only one building it is deleted
    check_lhn_has_min_two_build(ind=ind)

    #  Check, if each subLHN has, at least, one feeder node
    check_lhn_th_supply(ind=ind, dict_restr=dict_restr,
                        dict_max_pv_area=dict_max_pv_area,
                        dict_heatloads=dict_heatloads,
                        dict_sh=dict_sh,
                        pv_min=pv_min, pv_step=pv_step, use_pv=use_pv,
                        add_pv_prop=add_pv_prop, do_random=do_random)

    if prevent_boi_lhn:
        check_no_boi_lhn_only(ind=ind,
                              dict_restr=dict_restr,
                              dict_sh=dict_sh,
                              dict_heatloads=dict_heatloads)

    #  TODO: Add further checks


#  TODO: if CHP or HP, use TES
#  TODO: Prevent EH-stand-alone
#  TODO: No stand-alone CHP (add boiler and tes)
#  TODO: No stand-alone HP (add EH and tes)
#  TODO: Only one type of heat pump
#  TODO: Bring functions in order
#  TODO: Add check that all nodes in LHN are unique

if __name__ == '__main__':
    #  Building dicts
    dict_b1 = {'bat': 5000,  # in Joule
               'boi': 10000,  # in Watt
               'chp': 1000,
               'eh': 0,
               'hp_aw': 0,
               'hp_ww': 0,
               'pv': 0,  # in m2
               'tes': 300}  # in kg

    dict_b2 = {'bat': 0,  # in Joule
               'boi': 10000,  # in Watt
               'chp': 0,
               'eh': 0,
               'hp_aw': 0,
               'hp_ww': 0,
               'pv': 0,  # in m2
               'tes': 300}  # in kg

    #  With HP
    dict_b3 = {'bat': 0,  # in Joule
               'boi': 0,  # in Watt
               'chp': 0,
               'eh': 20000,
               'hp_aw': 10000,
               'hp_ww': 0,
               'pv': 50,  # in m2
               'tes': 500}  # in kg

    #  Incorrect (with bat without CHP or PV
    dict_b4 = {'bat': 5000,  # in Joule
               'boi': 10000,  # in Watt
               'chp': 0,
               'eh': 0,
               'hp_aw': 0,
               'hp_ww': 0,
               'pv': 0,  # in m2
               'tes': 300}  # in kg

    #  (No thermal feeder)
    dict_b5 = {'bat': 5000,  # in Joule
               'boi': 0,  # in Watt
               'chp': 0,
               'eh': 0,
               'hp_aw': 0,
               'hp_ww': 0,
               'pv': 50,  # in m2
               'tes': 300}  # in kg



    #  Check if HP is in LHN
    #  ###################################################
    ind_hp_in_lhn = {1001: dict_b1, 1002: dict_b2, 1003: dict_b3,
                     'lhn': [[1001, 1002, 1003]]}

    valid = check_no_hp_in_lhn(ind=ind_hp_in_lhn)

    assert valid is False

    #  Show if lhn connection 1003 has been deleted
    print(ind_hp_in_lhn)
    assert ind_hp_in_lhn['lhn'] == [[1001, 1002]]

    #  Check if each LHN has, at least, two connection points
    #  ###################################################
    ind_single_b_lhn = {'lhn': [[1001]]}

    valid = check_lhn_has_min_two_build(ind=ind_single_b_lhn)

    assert valid is False

    print(ind_single_b_lhn['lhn'])
    assert ind_single_b_lhn['lhn'] == []

    #  Check if PV sizes are not exceeding max. PV rooftop usable area
    #  ###################################################

    dict_b3_copy = copy.deepcopy(dict_b3)

    ind_check_pv = {1001: dict_b3_copy}

    dict_max_pv_area = {1001: 0}

    valid = check_pv_max_areas(ind=ind_check_pv,
                               dict_max_pv_area=dict_max_pv_area)

    assert valid is False
    assert dict_b3_copy['pv'] == 0

    #  Check if batteries are only installed in buildings with CHP or PV
    #  ####################################################

    dict_b4_copy = copy.deepcopy(dict_b4)

    ind_check_bat = {1001: dict_b4_copy}

    valid = check_bat_only_with_pv_or_chp(ind=ind_check_bat)

    assert valid is False
    assert dict_b4_copy['bat'] == 0

    #  Check if LHN has, at least, one feeder node
    #  #################################################################

    dict_restr = {'boi': [100000],
                  'tes': [2000],
                  'chp': [30000],
                  'hp_aw': [40000],
                  'hp_ww': [50000],
                  'eh': [60000],
                  'bat': [80000]}

    dict_sh = {1001: 50000,
               1002: 40000}

    dict_b5_copy = copy.deepcopy(dict_b5)

    ind_lhn_no_feeder = {1001: dict_b5, 1002: dict_b5_copy,
                         'lhn': [[1001, 1002]]}

    valid = check_lhn_th_supply(ind=ind_lhn_no_feeder,
                                dict_restr=dict_restr,
                                dict_sh=dict_sh,
                                dict_heatloads=dict_sh)

    assert valid is False
    assert dict_b5['boi'] > 0 or dict_b5_copy['boi'] > 0
