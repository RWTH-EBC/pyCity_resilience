#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

"""
from __future__ import division

import copy
import random
import numpy as np

import pycity_resilience.ga.verify.check_validity as checkval
import pycity_resilience.ga.analyse.analyse as analyse
import pycity_resilience.ga.evolution.lhn_changes as lhnchanges
import pycity_resilience.ga.evolution.mutation_esys as mutateesys


def do_mutate(ind, prob_mut, prob_lhn, dict_restr, dict_max_pv_area, pv_min,
              dict_pos, dict_sh=None,
              list_prob_lhn_and_esys=[0.4, 0.3, 0.3],
              list_prob_mute_type=[0.5, 0.5],
              list_prob_lhn_gen_mut=[0.3, 0.7],
              max_dist=None, perform_checks=True,
              use_bat=True,
              use_pv=True,
              use_lhn=True,
              list_options=None,
              list_opt_prob=None,
              list_lhn_opt=None,
              list_lhn_prob=None,
              list_lhn_to_stand_alone=None,
              pv_step=1, add_pv_prop=0, add_bat_prob=0,
              prevent_boi_lhn=True,
              dict_heatloads=None):
    """
    Perform mutation at individuums (energy system and/or LHN mutation)

    Parameters
    ----------
    ind : dict
        Individuum dictionary holding node ids with energy system dicts
        and 'lhn' with list of LHN subnetworks
    prob_mut : float
        Probability of mutation (e.g. 0.2 --> 20 % chance of mutation of
        single attribute)
    prob_lhn : float
        Probability of LHN mutation
    dict_restr : dict
        Dict holding possible energy system sizes
    dict_max_pv_area : dict
        Dict holding maximum usable PV area values in m2 per building
    pv_min : float
        Minimum possible PV area per building in m2
    dict_pos : dict
        Dict holding building node ids as keys and shapely point objects (2d)
        as values
    dict_sh : dict, optional
        Dictionary holding building node ids as keys and maximum space heating
        power values in Watt as dict values (default: None). If not None,
        used for size limitation. If None, dict_restr is used for sizing.
    list_prob_lhn_and_esys : list (of floats)
        List holding probabilities for LHN and esys mutation (index 0),
        LHN mutation (index 1) and single energy system mutation (index 2).
        Sum of probabilities has to be 1.
        (default: [0.4, 0.3, 0.3])
    list_prob_mute_type : list (of floats)
        List holding probabilities for attribute change (index 0) and attribute
        generation/deletion (index 1). Sum of probabilities has to be 1.
        (default: [0.5, 0.5])
    list_prob_lhn_gen_mut : list (of floats)
        List holding probabilities for gen/delete LHN (index 0) and
        probabilites to mutate LHN (index 1). Sum of probabilities has to be 1.
        (default. [0.3, 0.7]
    max_dist : float, optional
        Maximum allowed distance in m from building to building, which
        can be connected to LHN (default: None)
    perform_checks : bool, optional
        Defines, if individuums should be checked on plausibility (default:
        True). Canb be deactivated to increase speed (check is also performed
        before running evaluation)
    use_bat : bool, optional
        Defines, if battery can be used (default: True)
    use_pv : bool, optional
        Defines, if PV can be used (default: True)
    use_lhn :  : bool, optional
        Defines, if LHN can be used (default: True)
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
    list_lhn_to_stand_alone : list (of floats)
        List holding probability factors for energy system options in
        list_options (default: None).
        If None, uses default values [0.1, 0.15, 0.25, 0.05, 0.125, 0.125,
        0.05, 0.05, 0.05, 0.05, 0, 0]
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
        Defines additional probability ofBAT being changed, if only thermal
        mutation has been applied (defauft: 0). E.g. if boiler system has
        been changed to CHP, there is a change of add_pv_prob that also BAT
        is mutated.
    prevent_boi_lhn : bool, optional
		Prevent boi/eh LHN combinations (without CHP) (default: True).
		If True, adds CHPs to LHN systems without CHP
	dict_heatloads : dict, optional
        Dict holding building ids as keys and design heat loads in Watt
        as values (default: None)

    Returns
    -------
    ind : dict
        Mutated individuum (Copy. Input ind is not modified)
    """

    assert abs(sum(list_prob_mute_type) - 1) < 0.0000000001
    assert abs(sum(list_prob_lhn_and_esys) - 1) < 0.0000000001
    assert abs(sum(list_prob_lhn_gen_mut) - 1) < 0.0000000001
    assert prob_mut >= 0
    assert prob_mut <= 1
    assert prob_lhn >= 0
    assert prob_lhn <= 1
    assert pv_step > 0

    if list_opt_prob is not None:
        assert abs(sum(list_opt_prob) - 1) < 0.0000000001
    if list_lhn_prob is not None:
        assert abs(sum(list_lhn_prob) - 1) < 0.0000000001
    if list_lhn_to_stand_alone is not None:
        assert abs(sum(list_lhn_to_stand_alone) - 1) < 0.0000000001

    #  Get list with building ids (delete key 'lhn')
    list_ids = analyse.get_build_ids_ind(ind=ind)

    #  Copy ind dict
    ind = copy.deepcopy(ind)

    #  Decide if LHN and/or single esys mutation should be done
    lhn_esys_choice = np.random.choice(a=['lhn_and_esys', 'lhn', 'esys'],
                                       p=list_prob_lhn_and_esys)

    if lhn_esys_choice == 'lhn_and_esys' and use_lhn:
        do_esys_mut = True
        do_lhn_mut = True
    elif lhn_esys_choice == 'lhn' and use_lhn:
        do_esys_mut = False
        do_lhn_mut = True
    else:
        do_esys_mut = True
        do_lhn_mut = False

    if do_lhn_mut:
        # Mutate LHN system
        #  #############################################################

        #  Check if LHN(s) exists or not
        if ind['lhn'] == []:  # [Prob. of gen/del, Prob. of muation]
            list_prob_lhn_gen_mut = [1, 0]

        select_lhn = np.random.choice(a=['gen_lhn', 'mut_lhn'],
                                      p=list_prob_lhn_gen_mut)

        #  Generate or delete LHN
        #  #############################################################
        if select_lhn == 'gen_lhn':
            #  Generate new or delete existing LHN
            #  Options
            #  Connect all buildings to LHN (one feeder or multiple feeders)
            #  If, at least, one LHN exists, delete it
            #  (call new esys gen for buildings)
            #  Random nb. of subnetworks between 2 and n/3 (choose neighbors)

            if len(ind['lhn']) > 0 and len(ind['lhn']) < len(list_ids) - 1:
                #  At least on LHN, not all buildings are connected
                list_prob_gen = [0.1, 0.4, 0.5]
            elif ind['lhn'] == []:  # No LHN
                list_prob_gen = [0.3, 0, 0.7]
            elif len(ind['lhn'][0]) == len(list_ids):
                #  All buildings are connected to a single LHN
                list_prob_gen = [0, 1, 0]
            else:
                list_prob_gen = [0.2, 0.4, 0.4]

            select_lhn_gen = np.random.choice(a=['all', 'del', 'subnet'],
                                              p=list_prob_gen)

            if select_lhn_gen == 'all':

                #  Add single LHN to all buildings
                lhnchanges.add_lhn_all_build(ind=ind,
                                             dict_restr=dict_restr,
                                             pv_min=pv_min,
                                             dict_max_pv_area=
                                             dict_max_pv_area,
                                             dict_sh=dict_sh,
                                             add_pv_prop=add_pv_prop,
                                             add_bat_prob=add_bat_prob,
                                             dict_heatloads=dict_heatloads)

            elif select_lhn_gen == 'del':
                #  Delete network(s)
                lhnchanges.del_lhn(ind=ind,
                                   dict_restr=dict_restr,
                                   pv_min=pv_min,
                                   dict_max_pv_area=dict_max_pv_area,
                                   list_options=list_options,
                                   list_lhn_to_stand_alone=
                                   list_lhn_to_stand_alone,
                                   dict_sh=dict_sh,
                                   add_pv_prop=add_pv_prop,
                                   add_bat_prob=add_bat_prob,
                                   dict_heatloads=dict_heatloads)

            elif select_lhn_gen == 'subnet':
                #  Add specific number of subnetworks to ind

                lhnchanges.add_lhn(ind=ind, dict_restr=dict_restr,
                                   pv_min=pv_min,
                                   dict_max_pv_area=dict_max_pv_area,
                                   dict_pos=dict_pos,
                                   max_dist=max_dist,
                                   dict_sh=dict_sh,
                                   add_pv_prop=add_pv_prop,
                                   add_bat_prob=add_bat_prob)

        # Mutate existing LHN(s)
        #  #############################################################
        elif select_lhn == 'mut_lhn':
            #  Mutate existing LHN

            if len(ind['lhn']) > 0:  # Only mutate, if LHN exist

                select_lhn_mut = np.random.choice(a=['add_node',
                                                     'del_node',
                                                     'change_feed',
                                                     'add_feed',
                                                     'del_feed',
                                                     'all_modes'],
                                                  p=[0.1, 0.1, 0.1, 0.1, 0.1,
                                                     0.5])

                #  Randomly select index of LHN list
                idx_lhn = random.randint(0, int(len(ind['lhn']) - 1))

                #  Add neighbor node
                if select_lhn_mut == 'add_node':

                    lhnchanges.add_lhn_node(ind=ind, idx_lhn=idx_lhn,
                                            dict_restr=dict_restr,
                                            dict_pos=dict_pos,
                                            max_dist=max_dist,
                                            dict_sh=dict_sh,
                                            dict_heatloads=dict_heatloads)

                # Delete neighbor node
                elif select_lhn_mut == 'del_node':

                    lhnchanges.del_lhn_node(ind=ind,
                                            idx_lhn=idx_lhn,
                                            dict_restr=dict_restr,
                                            pv_min=pv_min,
                                            dict_max_pv_area=
                                            dict_max_pv_area,
                                            dict_pos=dict_pos,
                                            list_options=list_options,
                                            list_lhn_to_stand_alone=
                                            list_lhn_to_stand_alone,
                                            dict_heatloads=dict_heatloads)

                # Add feeder
                elif select_lhn_mut == 'add_feed':

                    lhnchanges.add_lhn_feeder_node(ind=ind,
                                                   idx_lhn=idx_lhn,
                                                   dict_restr=dict_restr,
                                                   pv_min=pv_min,
                                                   dict_max_pv_area=
                                                   dict_max_pv_area,
                                                   dict_sh=dict_sh,
                                                   add_pv_prop=add_pv_prop,
                                                   add_bat_prob=add_bat_prob,
                                                   dict_heatloads=
                                                   dict_heatloads
                                                   )

                # Delete feeder
                elif select_lhn_mut == 'del_feed':

                    lhnchanges.del_lhn_feeder(ind=ind, idx_lhn=idx_lhn)

                # Change feeder node
                elif select_lhn_mut == 'change_feed':

                    lhnchanges. \
                        change_lhn_feeder_node(ind=ind,
                                               idx_lhn=idx_lhn,
                                               dict_restr=dict_restr,
                                               pv_min=pv_min,
                                               dict_max_pv_area=
                                               dict_max_pv_area,
                                               dict_sh=dict_sh,
                                               add_pv_prop=add_pv_prop,
                                               add_bat_prob=add_bat_prob,
                                               dict_heatloads=dict_heatloads)

                # Multi options to mutate existing LHN
                elif select_lhn_mut == 'all_modes':

                    #  Loop over all LHN networks
                    for idx_lhn in range(len(ind['lhn'])):

                        add_node = False
                        if random.random() < prob_lhn:
                            #  Add new node
                            lhnchanges.add_lhn_node(
                                ind=ind, idx_lhn=idx_lhn,
                                dict_restr=dict_restr,
                                dict_pos=dict_pos,
                                max_dist=max_dist,
                                dict_sh=dict_sh,
                                dict_heatloads=dict_heatloads)
                            add_node = True

                        if random.random() < prob_lhn and add_node is False:
                            #  Delete node
                            lhnchanges.del_lhn_node(ind=ind,
                                                    idx_lhn=idx_lhn,
                                                    dict_restr=dict_restr,
                                                    pv_min=pv_min,
                                                    dict_max_pv_area=
                                                    dict_max_pv_area,
                                                    dict_pos=dict_pos,
                                                    list_options=list_options,
                                                    list_lhn_to_stand_alone=
                                                    list_lhn_to_stand_alone,
                                                    dict_heatloads=
                                                    dict_heatloads)

                        if random.random() < prob_lhn:
                            #  Add feeder node(s)
                            lhnchanges.\
                                add_lhn_feeder_node(ind=ind,
                                                    idx_lhn=idx_lhn,
                                                    dict_restr=dict_restr,
                                                    pv_min=pv_min,
                                                    dict_max_pv_area=
                                                    dict_max_pv_area,
                                                    dict_sh=dict_sh,
                                                    add_pv_prop=add_pv_prop,
                                                    add_bat_prob=add_bat_prob,
                                                    dict_heatloads=
                                                    dict_heatloads
                                                    )

                        if random.random() < prob_lhn:
                            #  Delete feeder(s)
                            lhnchanges.del_lhn_feeder(ind=ind, idx_lhn=idx_lhn)

                        if random.random() < prob_lhn:
                            #  Change feeder node
                            lhnchanges. \
                                change_lhn_feeder_node(
                                ind=ind,
                                idx_lhn=idx_lhn,
                                dict_restr=dict_restr,
                                pv_min=pv_min,
                                dict_max_pv_area=
                                dict_max_pv_area,
                                dict_sh=dict_sh,
                                add_pv_prop=add_pv_prop,
                                add_bat_prob=add_bat_prob,
                                dict_heatloads=dict_heatloads)

        # Check configuration
        #  #############################################################
        if perform_checks:
            checkval.run_all_checks(ind=ind,
                                    dict_max_pv_area=dict_max_pv_area,
                                    dict_restr=dict_restr, dict_sh=dict_sh,
                                    pv_min=pv_min, pv_step=pv_step,
                                    use_pv=use_pv,
                                    add_pv_prop=add_pv_prop,
                                    prevent_boi_lhn=prevent_boi_lhn,
                                    dict_heatloads=dict_heatloads
                                    )

    # Mutate single energy system configurations or attributes
    #  #############################################################
    if do_esys_mut:

        for n in list_ids:

            type_mute = np.random.choice(a=[0, 1], p=list_prob_mute_type)

            if type_mute == 0:
                #  Change attributes of existing esys
                mutateesys.mut_esys_val_single_build(
                    ind=ind, n=n,
                    prob_mut=prob_mut,
                    dict_restr=dict_restr,
                    pv_min=pv_min,
                    dict_max_pv_area=
                    dict_max_pv_area,
                    dict_sh=dict_sh,
                    pv_step=pv_step,
                    dict_heatloads=dict_heatloads)

            elif type_mute == 1:

                #  Generate/delete energy systems in use
                #  Differentiate between LHN and non-LHN connected buildings
                mutateesys. \
                    mut_esys_config_single_build(ind=ind, n=n,
                                                 dict_restr=dict_restr,
                                                 pv_min=pv_min,
                                                 dict_max_pv_area=
                                                 dict_max_pv_area,
                                                 use_bat=use_bat,
                                                 use_pv=use_pv,
                                                 list_options=list_options,
                                                 list_opt_prob=list_opt_prob,
                                                 list_lhn_opt=list_lhn_opt,
                                                 list_lhn_prob=list_lhn_prob,
                                                 dict_sh=dict_sh,
                                                 pv_step=pv_step,
                                                 add_pv_prop=add_pv_prop,
                                                 add_bat_prob=add_bat_prob,
                                                 dict_heatloads=dict_heatloads)

            else:
                msg = 'Unknown type_mute!'
                raise AssertionError(msg)

    # Check configuration
    #  #############################################################

    # Check configuration
    #  #############################################################
    if perform_checks:
        checkval.run_all_checks(ind=ind,
                                dict_max_pv_area=dict_max_pv_area,
                                dict_restr=dict_restr, dict_sh=dict_sh,
                                pv_min=pv_min, pv_step=pv_step, use_pv=use_pv,
                                add_pv_prop=add_pv_prop,
                                prevent_boi_lhn=prevent_boi_lhn,
                                dict_heatloads=dict_heatloads
                                )

    print('Performed mutation')

    return ind
