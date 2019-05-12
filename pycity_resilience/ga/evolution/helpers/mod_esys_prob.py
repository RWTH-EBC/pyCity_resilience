#!/usr/bin/env python
# coding=utf-8
"""
Script to modify probabilities of energy system change options
"""
from __future__ import division

import copy
import random as rd


def mod_list_esys_options(list_options,
                          list_opt_prob,
                          use_bat,
                          use_pv,
                          use_chp,
                          use_hp_aw,
                          use_hp_ww,
                          prevent_boi_hp,
                          prevent_chp_eh,
                          incr=0.001):
    """
    Modifies energy system option probability list, based on boolean inputs

    Parameters
    ----------
    list_options : list (of str)
        List holding strings with energy system options,
        e.g. ['boi', 'boi_tes', 'chp_boi_tes',
        'chp_boi_eh_tes', 'hp_aw_eh', 'hp_ww_eh', 'hp_aw_boi', 'hp_ww_boi',
        'hp_aw_eh_boi', 'hp_ww_eh_boi', 'bat', 'pv']
    list_opt_prob : list (of floats)
        List holding probability factors for energy system options in
        list_options,
        e.g. [0.1, 0.1, 0.2, 0.05, 0.1, 0.1, 0.05,
        0.05, 0.05, 0.05, 0.05, 0.1]
    use_bat : bool
        Defines, if battery can be used
    use_pv : bool
        Defines, if PV can be used
    use_chp : bool
        Defines, if CHP can be used
    use_lhn :  : bool
        Defines, if LHN can be used
    use_hp_aw : bool
        Defines, if air water heat pump can be used
    use_hp_ww : bool
        Defines, if air water heat pump can be used
    prevent_boi_hp : bool
        Prevents boiler / heat pump combinations
    prevent_chp_eh : bool
        Prevents CHP / EH combinations
    incr : float, optional
        Increment, which is used to fill up missing probability values in
        list_opt_prob_mod (default: 0.001)

    Returns
    -------
    list_opt_prob_mod : list (of floats)
        List with modified probabilities
    """

    assert abs(sum(list_opt_prob) - 1) < 0.000000001
    assert len(list_opt_prob) == len(list_options)

    list_opt_prob_mod = copy.copy(list_opt_prob)

    if use_bat is False:
        #  Return index of bat in list_options
        if 'bat' in list_options:
            idx = list_options.index('bat')
            #  Set value of list_opt_prob_mod at index idx to zero
            list_opt_prob_mod[idx] = 0

    if use_pv is False:
        #  Return index of bat in list_options
        if 'pv' in list_options:
            idx = list_options.index('pv')
            #  Set value of list_opt_prob_mod at index idx to zero
            list_opt_prob_mod[idx] = 0

    if use_chp is False:
        #  Return index of bat in list_options
        if 'chp_boi_tes' in list_options:
            idx = list_options.index('chp_boi_tes')
            #  Set value of list_opt_prob_mod at index idx to zero
            list_opt_prob_mod[idx] = 0
        if 'chp_boi_eh_tes' in list_options:
            idx = list_options.index('chp_boi_eh_tes')
            #  Set value of list_opt_prob_mod at index idx to zero
            list_opt_prob_mod[idx] = 0

    if use_hp_aw is False:
        #  Return index of bat in list_options
        if 'hp_aw_eh' in list_options:
            idx = list_options.index('hp_aw_eh')
            #  Set value of list_opt_prob_mod at index idx to zero
            list_opt_prob_mod[idx] = 0
        if 'hp_aw_boi' in list_options:
            idx = list_options.index('hp_aw_boi')
            #  Set value of list_opt_prob_mod at index idx to zero
            list_opt_prob_mod[idx] = 0
        if 'hp_aw_eh_boi' in list_options:
            idx = list_options.index('hp_aw_eh_boi')
            #  Set value of list_opt_prob_mod at index idx to zero
            list_opt_prob_mod[idx] = 0

    if use_hp_ww is False:
        #  Return index of bat in list_options
        if 'hp_ww_eh' in list_options:
            idx = list_options.index('hp_ww_eh')
            #  Set value of list_opt_prob_mod at index idx to zero
            list_opt_prob_mod[idx] = 0
        if 'hp_ww_boi' in list_options:
            idx = list_options.index('hp_ww_boi')
            #  Set value of list_opt_prob_mod at index idx to zero
            list_opt_prob_mod[idx] = 0
        if 'hp_ww_eh_boi' in list_options:
            idx = list_options.index('hp_ww_eh_boi')
            #  Set value of list_opt_prob_mod at index idx to zero
            list_opt_prob_mod[idx] = 0

    if prevent_boi_hp:
        if 'hp_aw_boi' in list_options:
            idx = list_options.index('hp_aw_boi')
            #  Set value of list_opt_prob_mod at index idx to zero
            list_opt_prob_mod[idx] = 0
        if 'hp_aw_eh_boi' in list_options:
            idx = list_options.index('hp_aw_eh_boi')
            #  Set value of list_opt_prob_mod at index idx to zero
            list_opt_prob_mod[idx] = 0
        if 'hp_ww_boi' in list_options:
            idx = list_options.index('hp_ww_boi')
            #  Set value of list_opt_prob_mod at index idx to zero
            list_opt_prob_mod[idx] = 0
        if 'hp_ww_eh_boi' in list_options:
            idx = list_options.index('hp_ww_eh_boi')
            #  Set value of list_opt_prob_mod at index idx to zero
            list_opt_prob_mod[idx] = 0

    if prevent_chp_eh:
        if 'chp_boi_eh_tes' in list_options:
            idx = list_options.index('chp_boi_eh_tes')
            #  Set value of list_opt_prob_mod at index idx to zero
            list_opt_prob_mod[idx] = 0

    # Check discrepancy to 1 and fill up with values (if values is not 0)
    delta = 1 - sum(list_opt_prob_mod)

    assert abs(delta + 0.000000000001) >= 0

    if delta < 1:

        list_indexes = []
        #  Search for values larger than zero and return index
        for i in range(len(list_opt_prob_mod)):
            if list_opt_prob_mod[i] > 0:
                list_indexes.append(i)

        while delta > incr/10:
            #  Move increment of incr to list

            #  Select random index of values larger zero
            idx = rd.choice(list_indexes)

            #  Add incr
            list_opt_prob_mod[idx] += incr

            #  Subtract from delta
            delta -= incr

    return list_opt_prob_mod


def mod_list_lhn_options(list_lhn_opt,
                         list_lhn_prob,
                         use_bat, use_pv,
                         incr=0.001):
    """
    Modify probability list for LHN energy system changes

    Parameters
    ----------
    list_lhn_opt : list (of str)
        List holding strings with LHN mutation options, e.g.
        ['chp_boi_tes', 'chp_boi_eh_tes', 'bat', 'pv', 'no_th_supply']
    list_lhn_prob : list (of floats)
        List holding probability factors for LHN mutation options in
        list_lhn_opt, e.g.
        [0.1, 0.05, 0.05, 0.2, 0.6]
    use_bat : bool
        Defines, if battery should be used.
    use_pv : bool
        Defines, if PV should be used. If False, prevents PV usage.
    incr : float, optional
        Increment, which is used to fill up missing probability values in
        list_opt_prob_mod (default: 0.001)

    Returns
    -------
    list_lhn_prob_mod : list (of floats)
        List holding modified LHN mutation probabilities
    """

    assert abs(sum(list_lhn_prob) - 1) < 0.000000001
    assert len(list_lhn_prob) == len(list_lhn_opt)

    list_lhn_prob_mod = copy.copy(list_lhn_prob)

    if use_bat is False:
        #  Return index of bat in list_options
        if 'bat' in list_lhn_opt:
            idx = list_lhn_opt.index('bat')
            #  Set value of list_lhn_prob_mod at index idx to zero
            list_lhn_prob_mod[idx] = 0

    if use_pv is False:
        #  Return index of bat in list_options
        if 'pv' in list_lhn_opt:
            idx = list_lhn_opt.index('pv')
            #  Set value of list_lhn_prob_mod at index idx to zero
            list_lhn_prob_mod[idx] = 0

    # Check discrepancy to 1 and fill up with values (if values is not 0)
    delta = 1 - sum(list_lhn_prob_mod)

    assert delta >= 0

    if delta < 1:

        list_indexes = []
        #  Search for values larger than zero and return index
        for i in range(len(list_lhn_prob_mod)):
            if list_lhn_prob_mod[i] > 0:
                list_indexes.append(i)

        while delta > incr/10:
            #  Move increment of incr to list

            #  Select random index of values larger zero
            idx = rd.choice(list_indexes)

            #  Add incr
            list_lhn_prob_mod[idx] += incr

            #  Subtract from delta
            delta -= incr

    return list_lhn_prob_mod


if __name__ == '__main__':
    use_bat = False
    use_pv = True
    use_chp = True
    use_hp_aw = False
    use_hp_ww = True
    prevent_boi_hp = True
    prevent_chp_eh = True

    list_options = ['boi', 'boi_tes', 'chp_boi_tes', 'chp_boi_eh_tes',
                    'hp_aw_eh', 'hp_ww_eh', 'hp_aw_boi', 'hp_ww_boi',
                    'hp_aw_eh_boi', 'hp_ww_eh_boi', 'bat', 'pv']

    list_opt_prob = [0.1, 0.1, 0.2, 0.05, 0.1, 0.1, 0.05, 0.05, 0.05,
                     0.05, 0.05, 0.1]

    list_opt_prob_mod = \
        mod_list_esys_options(list_options=list_options,
                              list_opt_prob=list_opt_prob,
                              use_bat=use_bat,
                              use_pv=use_pv,
                              use_chp=use_chp,
                              use_hp_aw=use_hp_aw,
                              use_hp_ww=use_hp_ww,
                              prevent_boi_hp=prevent_boi_hp,
                              prevent_chp_eh=prevent_chp_eh)

    print('list_options:')
    print(list_options)
    print()

    print('list_opt_prob_mod:')
    print(list_opt_prob_mod)
    print()

    print('Sum of probabilities:')
    print(sum(list_opt_prob_mod))
    assert abs(sum(list_opt_prob_mod) - 1) <= 0.00000001
    print('##############################################')
    print()

    #  LHN modifications
    #  ####################################################################

    list_lhn_opt = ['chp_boi_tes', 'chp_boi_eh_tes',
                    'bat', 'pv', 'no_th_supply']

    list_lhn_prob = [0.1, 0.05, 0.05, 0.2, 0.6]

    list_lhn_prob_mod = mod_list_lhn_options(list_lhn_opt=list_lhn_opt,
                                             list_lhn_prob=list_lhn_prob,
                                             use_bat=use_bat, use_pv=use_pv)

    print('list_options (LHN):')
    print(list_lhn_opt)
    print()

    print('list_lhn_prob:')
    print(list_lhn_prob_mod)
    print()

    print('Sum of probabilities:')
    print(sum(list_lhn_prob_mod))
    assert abs(sum(list_lhn_prob_mod) - 1) < 0.00000001
