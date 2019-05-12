#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

"""
from __future__ import division

import copy

import pycity_resilience.ga.evolution.crossover as cx


class TestCrossover():
    def test_cx_1(self):
        #  Test building dict
        b_dict1 = {'boi': 10,
                  'chp': 20,
                  'hp_aw': 0,
                  'hp_ww': 0,
                  'eh': 50,
                  'tes': 60,
                  'pv': 70,
                  'bat': 80}

        b_dict1b = copy.deepcopy(b_dict1)

        #  Test building dict
        b_dict2 = {'boi': 1,
                  'chp': 2,
                  'hp_aw': 0,
                  'hp_ww': 0,
                  'eh': 5,
                  'tes': 6,
                  'pv': 7,
                  'bat': 8}

        b_dict2b = copy.deepcopy(b_dict2)

        ind1 = {1001: b_dict1,
                #1002: b_dict1b,
                'lhn': []}
        ind2 = {1001: b_dict2,
                #1002: b_dict2b,
                'lhn': []}

        dict_max_pv_area = {1001: 100,
                            # 1002: 100
                            }

        #  Shuffle all values
        list_cx_combis = [['chp', 'boi', 'hp_aw', 'hp_ww',
             'eh', 'bat', 'pv', 'tes']]

        (ind1_res, ind2_res) = \
            cx.do_crossover(ind1=ind1, ind2=ind2,
                            dict_max_pv_area=dict_max_pv_area,
                            list_cx_combis=list_cx_combis,
                            perform_checks=False)

        assert ind1_res[1001] == b_dict2
        assert ind2_res[1001] == b_dict1

    def test_cx_2(self):
        #  Test building dict
        b_dict1 = {'boi': 10,
                   'chp': 20,
                   'hp_aw': 0,
                   'hp_ww': 0,
                   'eh': 50,
                   'tes': 60,
                   'pv': 70,
                   'bat': 80}

        b_dict1b = copy.deepcopy(b_dict1)

        #  Test building dict
        b_dict2 = {'boi': 1,
                   'chp': 2,
                   'hp_aw': 0,
                   'hp_ww': 0,
                   'eh': 5,
                   'tes': 6,
                   'pv': 7,
                   'bat': 8}

        b_dict2b = copy.deepcopy(b_dict2)

        ind1 = {1001: b_dict1,
                # 1002: b_dict1b,
                'lhn': []}
        ind2 = {1001: b_dict2,
                # 1002: b_dict2b,
                'lhn': []}

        dict_max_pv_area = {1001: 100,
                            # 1002: 100
                            }

        #  Shuffle all values
        list_cx_combis = [['chp']]

        (ind1_res, ind2_res) = \
            cx.do_crossover(ind1=ind1, ind2=ind2,
                            dict_max_pv_area=dict_max_pv_area,
                            list_cx_combis=list_cx_combis,
                            perform_checks=False)

        assert ind1_res[1001]['chp'] == b_dict2['chp']
        assert ind2_res[1001]['chp'] == b_dict1['chp']

    def test_cx_3(self):
        #  Test building dict
        b_dict1 = {'boi': 10,
                   'chp': 20,
                   'hp_aw': 0,
                   'hp_ww': 0,
                   'eh': 50,
                   'tes': 60,
                   'pv': 70,
                   'bat': 80}

        b_dict1b = copy.deepcopy(b_dict1)

        #  Test building dict
        b_dict2 = {'boi': 1,
                   'chp': 2,
                   'hp_aw': 0,
                   'hp_ww': 0,
                   'eh': 5,
                   'tes': 6,
                   'pv': 7,
                   'bat': 8}

        b_dict2b = copy.deepcopy(b_dict2)

        ind1 = {1001: b_dict1,
                # 1002: b_dict1b,
                'lhn': []}
        ind2 = {1001: b_dict2,
                # 1002: b_dict2b,
                'lhn': []}

        dict_max_pv_area = {1001: 100,
                            # 1002: 100
                            }

        #  Shuffle all values
        list_cx_combis = [['boi']]

        (ind1_res, ind2_res) = \
            cx.do_crossover(ind1=ind1, ind2=ind2,
                            dict_max_pv_area=dict_max_pv_area,
                            list_cx_combis=list_cx_combis,
                            perform_checks=False)

        assert ind1_res[1001]['boi'] == b_dict2['boi']
        assert ind2_res[1001]['boi'] == b_dict1['boi']

    def test_cx_4(self):
        #  Test building dict
        b_dict1 = {'boi': 10,
                   'chp': 20,
                   'hp_aw': 0,
                   'hp_ww': 0,
                   'eh': 50,
                   'tes': 60,
                   'pv': 70,
                   'bat': 80}

        b_dict1b = copy.deepcopy(b_dict1)

        #  Test building dict
        b_dict2 = {'boi': 1,
                   'chp': 2,
                   'hp_aw': 0,
                   'hp_ww': 0,
                   'eh': 5,
                   'tes': 6,
                   'pv': 7,
                   'bat': 8}

        b_dict2b = copy.deepcopy(b_dict2)

        ind1 = {1001: b_dict1,
                # 1002: b_dict1b,
                'lhn': []}
        ind2 = {1001: b_dict2,
                # 1002: b_dict2b,
                'lhn': []}

        dict_max_pv_area = {1001: 100,
                            # 1002: 100
                            }

        #  Shuffle all values
        list_cx_combis = [['pv']]

        (ind1_res, ind2_res) = \
            cx.do_crossover(ind1=ind1, ind2=ind2,
                            dict_max_pv_area=dict_max_pv_area,
                            list_cx_combis=list_cx_combis,
                            perform_checks=False)

        assert ind1_res[1001]['pv'] == b_dict2['pv']
        assert ind2_res[1001]['pv'] == b_dict1['pv']

    def test_cx_5(self):
        dict_restr = {'boi': [1],
                      'tes': [2],
                      'chp': [3],
                      'hp_aw': [4],
                      'hp_ww': [5],
                      'eh': [6],
                      'bat': [7]}

        #  Test building dict
        b_dict1 = {'boi': 10,
                   'chp': 20,
                   'hp_aw': 0,
                   'hp_ww': 0,
                   'eh': 50,
                   'tes': 60,
                   'pv': 70,
                   'bat': 80}

        b_dict1b = copy.deepcopy(b_dict1)

        #  Test building dict
        b_dict2 = {'boi': 1,
                   'chp': 2,
                   'hp_aw': 0,
                   'hp_ww': 0,
                   'eh': 5,
                   'tes': 6,
                   'pv': 75,
                   'bat': 8}

        b_dict2b = copy.deepcopy(b_dict2)

        dict_sh = {1001: 20000, 1002: 30000}

        ind1 = {1001: b_dict1,
                # 1002: b_dict1b,
                'lhn': []}
        ind2 = {1001: b_dict2,
                # 1002: b_dict2b,
                'lhn': []}

        dict_max_pv_area = {1001: 20,
                            # 1002: 100
                            }

        #  Shuffle all values
        list_cx_combis = [['pv']]

        (ind1_res, ind2_res) = \
            cx.do_crossover(ind1=ind1, ind2=ind2,
                            dict_max_pv_area=dict_max_pv_area,
                            list_cx_combis=list_cx_combis,
                            perform_checks=True, dict_restr=dict_restr,
                            dict_sh=dict_sh,
                            dict_heatloads=dict_sh)

        #  Reduce to max value
        assert ind1_res[1001]['pv'] == 20
        assert ind2_res[1001]['pv'] == 20

    def test_cx_6(self):
        #  Test building dict
        b_dict1 = {'boi': 10,
                   'chp': 20,
                   'hp_aw': 0,
                   'hp_ww': 0,
                   'eh': 50,
                   'tes': 60,
                   'pv': 70,
                   'bat': 80}

        b_dict1b = copy.deepcopy(b_dict1)

        #  Test building dict
        b_dict2 = {'boi': 1,
                   'chp': 2,
                   'hp_aw': 0,
                   'hp_ww': 0,
                   'eh': 5,
                   'tes': 6,
                   'pv': 7,
                   'bat': 8}

        b_dict2b = copy.deepcopy(b_dict2)

        ind1 = {1001: b_dict1,
                # 1002: b_dict1b,
                'lhn': []}
        ind2 = {1001: b_dict2,
                # 1002: b_dict2b,
                'lhn': []}

        dict_max_pv_area = {1001: 100,
                            # 1002: 100
                            }

        #  Shuffle all values
        list_cx_combis = [['bat']]

        (ind1_res, ind2_res) = \
            cx.do_crossover(ind1=ind1, ind2=ind2,
                            dict_max_pv_area=dict_max_pv_area,
                            list_cx_combis=list_cx_combis,
                            perform_checks=False)

        assert ind1_res[1001]['bat'] == b_dict2['bat']
        assert ind2_res[1001]['bat'] == b_dict1['bat']

    def test_cx_loop(self):
        #  Test building dict
        b_dict1 = {'boi': 10,
                  'chp': 20,
                  'hp_aw': 0,
                  'hp_ww': 0,
                  'eh': 50,
                  'tes': 60,
                  'pv': 70,
                  'bat': 80}

        #  Test building dict
        b_dict2 = {'boi': 1,
                  'chp': 2,
                  'hp_aw': 0,
                  'hp_ww': 0,
                  'eh': 5,
                  'tes': 6,
                  'pv': 7,
                  'bat': 8}

        ind1 = {1001: b_dict1,
                'lhn': []}
        ind2 = {1001: b_dict2,
                'lhn': []}

        dict_max_pv_area = {1001: 100}

        for i in range(50):
            cx.do_crossover(ind1=ind1, ind2=ind2,
                            dict_max_pv_area=dict_max_pv_area,
                            perform_checks=False)
