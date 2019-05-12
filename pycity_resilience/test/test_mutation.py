#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

"""
from __future__ import division

import copy
import shapely.geometry.point as point

import pycity_resilience.ga.evolution.mutation as mutate


class TestMutation():
    def test_mutation(self):
        dict_restr = {'boi': [1],
                      'tes': [2],
                      'chp': [3],
                      'hp_aw': [4],
                      'hp_ww': [5],
                      'eh': [6],
                      'bat': [8]}

        b_dict = {'boi': 10,
                  'chp': 20,
                  'hp_aw': 0,
                  'hp_ww': 0,
                  'eh': 50,
                  'tes': 60,
                  'pv': 70,
                  'bat': 80}

        ind = {1001: b_dict,
               1002: copy.copy(b_dict),
               1003: copy.copy(b_dict),
               1008: copy.copy(b_dict),
               'lhn': []}

        dict_max_pv_area = {1001: 100,
                            1002: 100,
                            1003: 100,
                            1008: 100}

        p1 = point.Point(0, 0)
        p2 = point.Point(10, 0)
        p3 = point.Point(20, 0)
        p8 = point.Point(30, 0)

        dict_pos = {1001: p1, 1002: p2, 1003: p3, 1008: p8}
        dict_sh = {1001: 1, 1002: 1, 1003: 1, 1008: 1}

        ind_new = mutate.do_mutate(ind=ind, prob_mut=1, prob_lhn=1,
                                   dict_restr=dict_restr,
                                   dict_max_pv_area=dict_max_pv_area,
                                   pv_min=10,
                                   dict_pos=dict_pos,
                                   list_prob_lhn_and_esys=[0, 0, 1],
                                   # Only esys mutation
                                   list_prob_mute_type=[1, 0],
                                   # Only attribute changes
                                   list_prob_lhn_gen_mut=[0.3, 0.7],
                                   # Not used, here
                                   max_dist=None,
                                   dict_sh=dict_sh,
                                   dict_heatloads=dict_sh)

        assert ind_new[1001]['boi'] == 1
        assert ind_new[1001]['tes'] == 2
        assert ind_new[1001]['chp'] == 3
        assert ind_new[1001]['hp_aw'] == 0
        assert ind_new[1001]['hp_ww'] == 0
        assert ind_new[1001]['eh'] == 6
        assert ind_new[1001]['pv'] > 0
        assert ind_new[1001]['bat'] == 8

    def test_mutation2(self):
        dict_restr = {'boi': [1],
                      'tes': [2],
                      'chp': [3],
                      'hp_aw': [4],
                      'hp_ww': [5],
                      'eh': [6],
                      'bat': [8]}

        b_dict = {'boi': 10,
                  'chp': 20,
                  'hp_aw': 0,
                  'hp_ww': 0,
                  'eh': 0,
                  'tes': 60,
                  'pv': 70,
                  'bat': 80}

        ind = {1001: b_dict,
               1002: copy.copy(b_dict),
               1003: copy.copy(b_dict),
               1008: copy.copy(b_dict),
               'lhn': [[1001, 1002, 1003]]}

        dict_max_pv_area = {1001: 100,
                            1002: 100,
                            1003: 100,
                            1008: 100}

        p1 = point.Point(0, 0)
        p2 = point.Point(10, 0)
        p3 = point.Point(20, 0)
        p8 = point.Point(30, 0)

        dict_pos = {1001: p1, 1002: p2, 1003: p3, 1008: p8}
        dict_sh = {1001: 1, 1002: 1, 1003: 1, 1008: 1}

        ind_new = mutate.do_mutate(ind=ind, prob_mut=1, prob_lhn=1,
                                   dict_restr=dict_restr,
                                   dict_max_pv_area=dict_max_pv_area,
                                   pv_min=10,
                                   dict_pos=dict_pos,
                                   list_prob_lhn_and_esys=[0, 1, 0],
                                   # Only LHN mutation
                                   list_prob_mute_type=[1, 0],
                                   #  Only LHN attribute change
                                   list_prob_lhn_gen_mut=[0.3, 0.7],
                                   # Not used, here
                                   max_dist=None, dict_sh=dict_sh,
                                   dict_heatloads=dict_sh)

    def test_mutation_loop(self):
        dict_restr = {'boi': [1, 2],
                      'tes': [2, 3],
                      'chp': [3, 4],
                      'hp_aw': [4, 5],
                      'hp_ww': [5, 6],
                      'eh': [6, 7],
                      'bat': [8, 9]}

        b_dict = {'boi': 10,
                  'chp': 20,
                  'hp_aw': 0,
                  'hp_ww': 0,
                  'eh': 0,
                  'tes': 60,
                  'pv': 70,
                  'bat': 80}

        ind = {1001: b_dict,
               1002: copy.copy(b_dict),
               1003: copy.copy(b_dict),
               1004: copy.copy(b_dict),
               1005: copy.copy(b_dict),
               1006: copy.copy(b_dict),
               1007: copy.copy(b_dict),
               1008: copy.copy(b_dict),
               'lhn': [[1001, 1002, 1003, 1004]]}

        dict_max_pv_area = {1001: 100,
                            1002: 100,
                            1003: 100,
                            1004: 100,
                            1005: 100,
                            1006: 100,
                            1007: 100,
                            1008: 100}

        p1 = point.Point(0, 0)
        p2 = point.Point(10, 0)
        p3 = point.Point(20, 0)
        p4 = point.Point(0, 10)
        p5 = point.Point(10, 10)
        p6 = point.Point(20, 10)
        p7 = point.Point(30, 10)
        p8 = point.Point(30, 20)

        dict_pos = {1001: p1, 1002: p2, 1003: p3, 1004: p4,
                    1005: p5, 1006: p6, 1007: p7, 1008: p8}
        dict_sh = {1001: 1, 1002: 1, 1003: 1, 1004: 1,
                    1005: 1, 1006: 1, 1007: 1, 1008: 1}

        for i in range(500):
            mutate.do_mutate(ind=ind, prob_mut=0.7, prob_lhn=0.7,
                             dict_restr=dict_restr,
                             dict_max_pv_area=dict_max_pv_area,
                             pv_min=10,
                             dict_pos=dict_pos, dict_sh=dict_sh,
                             dict_heatloads=dict_sh)
