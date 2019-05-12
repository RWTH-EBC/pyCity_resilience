#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

"""
from __future__ import division

import copy
import shapely.geometry.point as point

import pycity_resilience.ga.evolution.lhn_changes as lhnchanges


class TestLHNChanges():
    def test_add_lhn_all_build(self):
        dict_restr = {'boi': [1],
                      'tes': [2],
                      'chp': [3],
                      'hp_aw': [4],
                      'hp_ww': [5],
                      'eh': [6],
                      'pv': [7],
                      'bat': [8]}

        b_dict = {'boi': 0,
                  'chp': 0,
                  'hp_aw': 20,
                  'hp_ww': 0,
                  'eh': 0,
                  'tes': 0,
                  'pv': 0,
                  'bat': 0}

        ind = {1001: b_dict,
               1002: copy.copy(b_dict),
               1003: copy.copy(b_dict),
               1008: copy.copy(b_dict),
               'lhn': []}

        dict_max_pv_area = {1001: 10,
                            1002: 20,
                            1003: 30,
                            1008: 40}

        lhnchanges.add_lhn_all_build(ind=ind, dict_restr=dict_restr, pv_min=0,
                                     dict_max_pv_area=dict_max_pv_area,
                                     prob_feed=[1, 0])

        #  Check if all buildings have been connected to LHN
        assert sorted(ind['lhn'][0]) == [1001, 1002, 1003, 1008]

        #  Check if, at least, on CHP has been build
        assert (ind[1001]['chp'] > 0 or ind[1002]['chp'] > 0
                or ind[1003]['chp'] > 0 or ind[1008]['chp'] > 0)

        #  Check if number of CHPs is one, number of tes is one
        #  and HPs have been removed
        count_chp = 0
        count_hp_aw = 0
        count_tes = 0
        for i in [1001, 1002, 1003, 1008]:
            if ind[i]['chp'] > 0:
                count_chp += 1
            if ind[i]['hp_aw'] > 0:
                count_hp_aw += 1
            if ind[i]['tes'] > 0:
                count_tes += 1

        assert count_chp == 1
        assert count_hp_aw == 0
        assert count_tes == 1

    def test_add_lhn_all_build2(self):
        dict_restr = {'boi': [1],
                      'tes': [2],
                      'chp': [3],
                      'hp_aw': [4],
                      'hp_ww': [5],
                      'eh': [6],
                      'pv': [7],
                      'bat': [8]}

        b_dict = {'boi': 0,
                  'chp': 0,
                  'hp_aw': 20,
                  'hp_ww': 0,
                  'eh': 0,
                  'tes': 0,
                  'pv': 0,
                  'bat': 0}

        ind = {1001: b_dict,
               1002: copy.copy(b_dict),
               1003: copy.copy(b_dict),
               1008: copy.copy(b_dict),
               'lhn': []}

        dict_max_pv_area = {1001: 10,
                            1002: 20,
                            1003: 30,
                            1008: 40}

        lhnchanges.add_lhn_all_build(ind=ind, dict_restr=dict_restr, pv_min=0,
                                     dict_max_pv_area=dict_max_pv_area,
                                     prob_feed=[0, 1])

        #  Check if all buildings have been connected to LHN
        assert sorted(ind['lhn'][0]) == [1001, 1002, 1003, 1008]

        count_chp = 0
        count_hp_aw = 0
        count_tes = 0
        for i in [1001, 1002, 1003, 1008]:
            if ind[i]['chp'] > 0:
                count_chp += 1
            if ind[i]['hp_aw'] > 0:
                count_hp_aw += 1
            if ind[i]['tes'] > 0:
                count_tes += 1

        assert count_chp > 1
        assert count_hp_aw == 0
        assert count_tes > 1

    def test_del_lhn(self):

        dict_restr = {'boi': [1],
                      'tes': [2],
                      'chp': [3],
                      'hp_aw': [4],
                      'hp_ww': [5],
                      'eh': [6],
                      'pv': [7],
                      'bat': [8]}

        b_dict = {'boi': 0,
                  'chp': 0,
                  'hp_aw': 0,
                  'hp_ww': 0,
                  'eh': 0,
                  'tes': 0,
                  'pv': 0,
                  'bat': 0}

        ind = {1001: b_dict,
               1002: copy.copy(b_dict),
               1003: copy.copy(b_dict),
               1004: copy.copy(b_dict),
               1005: copy.copy(b_dict),
               1006: copy.copy(b_dict),
               1007: copy.copy(b_dict),
               1008: copy.copy(b_dict),
               'lhn': [[1001, 1002, 1003, 1004], [1005, 1006, 1007, 1008]]}

        dict_max_pv_area = {1001: 10,
                            1002: 20,
                            1003: 30,
                            1004: 10,
                            1005: 20,
                            1006: 30,
                            1007: 50,
                            1008: 40}

        lhnchanges.del_lhn(ind=ind, dict_restr=dict_restr, pv_min=0,
                           dict_max_pv_area=dict_max_pv_area,
                           prob_del=[1, 0])

        #  Check if only one LHN is left
        assert len(ind['lhn']) == 1

        assert (sorted(ind['lhn'][0]) == [1001, 1002, 1003, 1004]
                or sorted(ind['lhn'][0]) == [1005, 1006, 1007, 1008])

    def test_del_lhn2(self):

        dict_restr = {'boi': [1],
                      'tes': [2],
                      'chp': [3],
                      'hp_aw': [4],
                      'hp_ww': [5],
                      'eh': [6],
                      'pv': [7],
                      'bat': [8]}

        b_dict = {'boi': 0,
                  'chp': 0,
                  'hp_aw': 0,
                  'hp_ww': 0,
                  'eh': 0,
                  'tes': 0,
                  'pv': 0,
                  'bat': 0}

        ind = {1001: b_dict,
               1002: copy.copy(b_dict),
               1003: copy.copy(b_dict),
               1004: copy.copy(b_dict),
               'lhn': [[1001, 1002, 1003, 1004]]}

        dict_max_pv_area = {1001: 10,
                            1002: 20,
                            1003: 30,
                            1004: 10}

        lhnchanges.del_lhn(ind=ind, dict_restr=dict_restr, pv_min=0,
                           dict_max_pv_area=dict_max_pv_area)

        #  Check if no LHN is left
        assert len(ind['lhn']) == 0

        #  Check if every building id has, at least, one thermal device
        for n in [1001, 1002, 1003, 1004]:
            has_th_sup = False  # Initial dummy value
            if ind[n]['boi'] > 0:
                has_th_sup = True
            elif ind[n]['chp'] > 0:
                has_th_sup = True
            elif ind[n]['hp_aw'] > 0:
                has_th_sup = True
            elif ind[n]['hp_ww'] > 0:
                has_th_sup = True

            assert has_th_sup is True

    def test_del_lhn3(self):

        dict_restr = {'boi': [1],
                      'tes': [2],
                      'chp': [3],
                      'hp_aw': [4],
                      'hp_ww': [5],
                      'eh': [6],
                      'pv': [7],
                      'bat': [8]}

        b_dict = {'boi': 0,
                  'chp': 0,
                  'hp_aw': 0,
                  'hp_ww': 0,
                  'eh': 0,
                  'tes': 0,
                  'pv': 0,
                  'bat': 0}

        ind = {1001: b_dict,
               1002: copy.copy(b_dict),
               1003: copy.copy(b_dict),
               1004: copy.copy(b_dict),
               1005: copy.copy(b_dict),
               1006: copy.copy(b_dict),
               1007: copy.copy(b_dict),
               1008: copy.copy(b_dict),
               'lhn': [[1001, 1002, 1003, 1004], [1005, 1006, 1007, 1008]]}

        dict_max_pv_area = {1001: 10,
                            1002: 20,
                            1003: 30,
                            1004: 10,
                            1005: 20,
                            1006: 30,
                            1007: 50,
                            1008: 40}

        lhnchanges.del_lhn(ind=ind, dict_restr=dict_restr, pv_min=0,
                           dict_max_pv_area=dict_max_pv_area,
                           prob_del=[0, 1])

        #  Check if no LHN is left
        assert len(ind['lhn']) == 0

    def test_add_lhn(self):
        dict_restr = {'boi': [1],
                      'tes': [2],
                      'chp': [3],
                      'hp_aw': [4],
                      'hp_ww': [5],
                      'eh': [6],
                      'pv': [7],
                      'bat': [8]}

        b_dict = {'boi': 0,
                  'chp': 0,
                  'hp_aw': 20,
                  'hp_ww': 0,
                  'eh': 0,
                  'tes': 30,
                  'pv': 0,
                  'bat': 0}

        ind = {1001: b_dict,
               1002: copy.copy(b_dict),
               1003: copy.copy(b_dict),
               1008: copy.copy(b_dict),
               'lhn': []}

        dict_max_pv_area = {1001: 10,
                            1002: 20,
                            1003: 30,
                            1008: 40}

        p1 = point.Point(0, 0)
        p2 = point.Point(10, 0)
        p3 = point.Point(20, 0)
        p8 = point.Point(30, 0)

        dict_pos = {1001: p1, 1002: p2, 1003: p3, 1008: p8}

        lhnchanges.add_lhn(ind=ind, dict_restr=dict_restr, pv_min=0,
                           dict_max_pv_area=dict_max_pv_area,
                           dict_pos=dict_pos, list_prob_lhn=[1, 0],
                           prob_gen_method=[1, 0, 0])

        assert len(ind['lhn'][0]) > 0

        count_chp = 0
        count_tes = 0
        for i in [1001, 1002, 1003, 1008]:
            if ind[i]['chp'] > 0:
                count_chp += 1
            if ind[i]['tes'] > 0:
                count_tes += 1

        assert count_chp > 0
        assert count_tes > 0

    def test_add_lhn2(self):
        dict_restr = {'boi': [1],
                      'tes': [2],
                      'chp': [3],
                      'hp_aw': [4],
                      'hp_ww': [5],
                      'eh': [6],
                      'pv': [7],
                      'bat': [8]}

        b_dict = {'boi': 0,
                  'chp': 0,
                  'hp_aw': 20,
                  'hp_ww': 0,
                  'eh': 0,
                  'tes': 0,
                  'pv': 0,
                  'bat': 0}

        ind = {1001: b_dict,
               1002: copy.copy(b_dict),
               1003: copy.copy(b_dict),
               1004: copy.copy(b_dict),
               1005: copy.copy(b_dict),
               1006: copy.copy(b_dict),
               1007: copy.copy(b_dict),
               1008: copy.copy(b_dict),
               'lhn': []}

        dict_max_pv_area = {1001: 10,
                            1002: 20,
                            1003: 30,
                            1004: 20,
                            1005: 60,
                            1006: 20,
                            1007: 30,
                            1008: 40}

        p1 = point.Point(0, 0)
        p2 = point.Point(10, 0)
        p3 = point.Point(20, 0)
        p4 = point.Point(0, 10)
        p5 = point.Point(10, 10)
        p6 = point.Point(20, 10)
        p7 = point.Point(30, 10)
        p8 = point.Point(30, 0)

        dict_pos = {1001: p1, 1002: p2, 1003: p3, 1004: p4, 1005: p5,
                    1006: p6, 1007: p7, 1008: p8}

        lhnchanges.add_lhn(ind=ind, dict_restr=dict_restr, pv_min=0,
                           dict_max_pv_area=dict_max_pv_area,
                           dict_pos=dict_pos, list_prob_lhn=[0, 1],
                           prob_gen_method=[1, 0, 0])

        assert len(ind['lhn'][0]) > 0
        assert len(ind['lhn']) > 0  # Might only generate single LHN

        count_chp = 0
        count_tes = 0
        for i in [1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008]:
            if ind[i]['chp'] > 0:
                count_chp += 1
            if ind[i]['tes'] > 0:
                count_tes += 1

        assert count_chp > 0
        assert count_tes > 0

    def test_add_lhn_kmeans(self):
        dict_restr = {'boi': [1],
                      'tes': [2],
                      'chp': [3],
                      'hp_aw': [4],
                      'hp_ww': [5],
                      'eh': [6],
                      'pv': [7],
                      'bat': [8]}

        b_dict = {'boi': 0,
                  'chp': 0,
                  'hp_aw': 20,
                  'hp_ww': 0,
                  'eh': 0,
                  'tes': 0,
                  'pv': 0,
                  'bat': 0}

        ind = {1001: b_dict,
               1002: copy.copy(b_dict),
               1003: copy.copy(b_dict),
               1004: copy.copy(b_dict),
               1005: copy.copy(b_dict),
               1006: copy.copy(b_dict),
               1007: copy.copy(b_dict),
               1008: copy.copy(b_dict),
               'lhn': []}

        dict_max_pv_area = {1001: 10,
                            1002: 20,
                            1003: 30,
                            1004: 20,
                            1005: 60,
                            1006: 20,
                            1007: 30,
                            1008: 40}

        p1 = point.Point(0, 0)
        p2 = point.Point(10, 0)
        p3 = point.Point(20, 0)
        p4 = point.Point(0, 10)
        p5 = point.Point(10, 10)
        p6 = point.Point(20, 10)
        p7 = point.Point(30, 10)
        p8 = point.Point(30, 0)

        dict_pos = {1001: p1, 1002: p2, 1003: p3, 1004: p4, 1005: p5,
                    1006: p6, 1007: p7, 1008: p8}

        lhnchanges.add_lhn(ind=ind, dict_restr=dict_restr, pv_min=0,
                           dict_max_pv_area=dict_max_pv_area,
                           dict_pos=dict_pos, list_prob_lhn=[0, 1],
                           prob_feed=[0, 1],
                           prob_gen_method=[0, 1, 0])

        assert len(ind['lhn'][0]) > 0
        assert len(ind['lhn']) > 0  # Might only generate single LHN

        count_chp = 0
        count_hp_aw = 0
        count_tes = 0
        for i in [1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008]:
            if ind[i]['chp'] > 0:
                count_chp += 1
            if ind[i]['hp_aw'] > 0:
                count_hp_aw += 1
            if ind[i]['tes'] > 0:
                count_tes += 1

        assert count_chp > 0
        assert count_hp_aw == 0
        assert count_tes > 0

    def test_add_lhn_meanshift(self):
        dict_restr = {'boi': [1],
                      'tes': [2],
                      'chp': [3],
                      'hp_aw': [4],
                      'hp_ww': [5],
                      'eh': [6],
                      'pv': [7],
                      'bat': [8]}

        b_dict = {'boi': 0,
                  'chp': 0,
                  'hp_aw': 20,
                  'hp_ww': 0,
                  'eh': 0,
                  'tes': 0,
                  'pv': 0,
                  'bat': 0}

        ind = {1001: b_dict,
               1002: copy.copy(b_dict),
               1003: copy.copy(b_dict),
               1004: copy.copy(b_dict),
               1005: copy.copy(b_dict),
               1006: copy.copy(b_dict),
               1007: copy.copy(b_dict),
               1008: copy.copy(b_dict),
               'lhn': []}

        dict_max_pv_area = {1001: 10,
                            1002: 20,
                            1003: 30,
                            1004: 20,
                            1005: 60,
                            1006: 20,
                            1007: 30,
                            1008: 40}

        p1 = point.Point(0, 0)
        p2 = point.Point(10, 0)
        p3 = point.Point(20, 0)
        p4 = point.Point(0, 10)
        p5 = point.Point(10, 10)
        p6 = point.Point(20, 10)
        p7 = point.Point(30, 10)
        p8 = point.Point(30, 0)

        dict_pos = {1001: p1, 1002: p2, 1003: p3, 1004: p4, 1005: p5,
                    1006: p6, 1007: p7, 1008: p8}

        lhnchanges.add_lhn(ind=ind, dict_restr=dict_restr, pv_min=0,
                           dict_max_pv_area=dict_max_pv_area,
                           dict_pos=dict_pos, list_prob_lhn=[0, 1],
                           prob_feed=[0, 1],
                           prob_gen_method=[0, 0, 1])

        assert len(ind['lhn'][0]) > 0
        assert len(ind['lhn']) > 0  # Might only generate single LHN

        count_chp = 0
        count_hp_aw = 0
        count_tes = 0
        for i in [1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008]:
            if ind[i]['chp'] > 0:
                count_chp += 1
            if ind[i]['hp_aw'] > 0:
                count_hp_aw += 1
            if ind[i]['tes'] > 0:
                count_tes += 1

        assert count_chp > 0
        assert count_hp_aw == 0
        assert count_tes > 0

    def test_add_lhn_node(self):
        dict_restr = {'boi': [1],
                      'tes': [2],
                      'chp': [3],
                      'hp_aw': [4],
                      'hp_ww': [5],
                      'eh': [6],
                      'pv': [7],
                      'bat': [8]}

        b_dict = {'boi': 10,
                  'chp': 20,
                  'hp_aw': 0,
                  'hp_ww': 0,
                  'eh': 0,
                  'tes': 30,
                  'pv': 0,
                  'bat': 0}

        b_dict2 = {'boi': 0,
                   'chp': 0,
                   'hp_aw': 0,
                   'hp_ww': 0,
                   'eh': 0,
                   'tes': 0,
                   'pv': 0,
                   'bat': 0}

        ind = {1001: b_dict,
               1002: b_dict2,
               1003: copy.copy(b_dict2),
               1004: copy.copy(b_dict2),
               1005: copy.copy(b_dict2),
               1006: copy.copy(b_dict2),
               1007: copy.copy(b_dict2),
               1008: copy.copy(b_dict2),
               'lhn': [[1001, 1002, 1003]]}

        dict_max_pv_area = {1001: 10,
                            1002: 20,
                            1003: 30,
                            1004: 20,
                            1005: 60,
                            1006: 20,
                            1007: 30,
                            1008: 40}

        p1 = point.Point(0, 0)
        p2 = point.Point(10, 0)
        p3 = point.Point(20, 0)
        p4 = point.Point(0, 10)
        p5 = point.Point(10, 10)
        p6 = point.Point(20, 10)
        p7 = point.Point(30, 10)
        p8 = point.Point(30, 0)

        dict_pos = {1001: p1, 1002: p2, 1003: p3, 1004: p4, 1005: p5,
                    1006: p6, 1007: p7, 1008: p8}

        idx_lhn = 0

        lhnchanges.add_lhn_node(ind=ind,
                                idx_lhn=idx_lhn,
                                dict_restr=dict_restr,
                                dict_pos=dict_pos,
                                prob_nodes=[1, 0],
                                prob_lhn_mut=1,
                                prob_no_th_sup=1,
                                prob_closest=1)

        assert len(ind['lhn'][0]) == 4

    def test_add_lhn_node2(self):
        dict_restr = {'boi': [1],
                      'tes': [2],
                      'chp': [3],
                      'hp_aw': [4],
                      'hp_ww': [5],
                      'eh': [6],
                      'pv': [7],
                      'bat': [8]}

        b_dict = {'boi': 10,
                  'chp': 20,
                  'hp_aw': 0,
                  'hp_ww': 0,
                  'eh': 0,
                  'tes': 30,
                  'pv': 0,
                  'bat': 0}

        b_dict2 = {'boi': 0,
                   'chp': 0,
                   'hp_aw': 0,
                   'hp_ww': 0,
                   'eh': 0,
                   'tes': 0,
                   'pv': 0,
                   'bat': 0}

        ind = {1001: b_dict,
               1002: b_dict2,
               1003: copy.copy(b_dict2),
               1004: copy.copy(b_dict2),
               1005: copy.copy(b_dict2),
               1006: copy.copy(b_dict2),
               1007: copy.copy(b_dict2),
               1008: copy.copy(b_dict2),
               'lhn': [[1001, 1002, 1003]]}

        dict_max_pv_area = {1001: 10,
                            1002: 20,
                            1003: 30,
                            1004: 20,
                            1005: 60,
                            1006: 20,
                            1007: 30,
                            1008: 40}

        p1 = point.Point(0, 0)
        p2 = point.Point(10, 0)
        p3 = point.Point(20, 0)
        p4 = point.Point(0, 10)
        p5 = point.Point(10, 10)
        p6 = point.Point(20, 10)
        p7 = point.Point(30, 10)
        p8 = point.Point(30, 0)

        dict_pos = {1001: p1, 1002: p2, 1003: p3, 1004: p4, 1005: p5,
                    1006: p6, 1007: p7, 1008: p8}

        idx_lhn = 0

        lhnchanges.add_lhn_node(ind=ind,
                                idx_lhn=idx_lhn,
                                dict_restr=dict_restr,
                                dict_pos=dict_pos,
                                prob_nodes=[1, 0],
                                prob_lhn_mut=1,
                                prob_no_th_sup=0,
                                prob_closest=1)

        assert len(ind['lhn'][0]) == 4

    def test_add_lhn_node3(self):
        dict_restr = {'boi': [1],
                      'tes': [2],
                      'chp': [3],
                      'hp_aw': [4],
                      'hp_ww': [5],
                      'eh': [6],
                      'pv': [7],
                      'bat': [8]}

        b_dict = {'boi': 10,
                  'chp': 20,
                  'hp_aw': 0,
                  'hp_ww': 0,
                  'eh': 0,
                  'tes': 30,
                  'pv': 0,
                  'bat': 0}

        b_dict2 = {'boi': 0,
                   'chp': 0,
                   'hp_aw': 0,
                   'hp_ww': 0,
                   'eh': 0,
                   'tes': 0,
                   'pv': 0,
                   'bat': 0}

        ind = {1001: b_dict,
               1002: b_dict2,
               1003: copy.copy(b_dict2),
               1004: copy.copy(b_dict2),
               1005: copy.copy(b_dict2),
               1006: copy.copy(b_dict2),
               1007: copy.copy(b_dict2),
               1008: copy.copy(b_dict2),
               'lhn': [[1001, 1002, 1003]]}

        dict_max_pv_area = {1001: 10,
                            1002: 20,
                            1003: 30,
                            1004: 20,
                            1005: 60,
                            1006: 20,
                            1007: 30,
                            1008: 40}

        p1 = point.Point(0, 0)
        p2 = point.Point(10, 0)
        p3 = point.Point(20, 0)
        p4 = point.Point(0, 10)
        p5 = point.Point(10, 10)
        p6 = point.Point(20, 10)
        p7 = point.Point(30, 10)
        p8 = point.Point(30, 0)

        dict_pos = {1001: p1, 1002: p2, 1003: p3, 1004: p4, 1005: p5,
                    1006: p6, 1007: p7, 1008: p8}

        idx_lhn = 0

        lhnchanges.add_lhn_node(ind=ind,
                                idx_lhn=idx_lhn,
                                dict_restr=dict_restr,
                                dict_pos=dict_pos,
                                prob_nodes=[1, 0],
                                prob_lhn_mut=1,
                                prob_no_th_sup=0,
                                prob_closest=0)

        assert len(ind['lhn'][0]) == 4

    def test_add_lhn_node4(self):
        dict_restr = {'boi': [1],
                      'tes': [2],
                      'chp': [3],
                      'hp_aw': [4],
                      'hp_ww': [5],
                      'eh': [6],
                      'pv': [7],
                      'bat': [8]}

        b_dict = {'boi': 10,
                  'chp': 20,
                  'hp_aw': 0,
                  'hp_ww': 0,
                  'eh': 0,
                  'tes': 30,
                  'pv': 0,
                  'bat': 0}

        b_dict2 = {'boi': 0,
                   'chp': 0,
                   'hp_aw': 0,
                   'hp_ww': 0,
                   'eh': 0,
                   'tes': 0,
                   'pv': 0,
                   'bat': 0}

        ind = {1001: b_dict,
               1002: b_dict2,
               1003: copy.copy(b_dict2),
               1004: copy.copy(b_dict2),
               1005: copy.copy(b_dict2),
               1006: copy.copy(b_dict2),
               1007: copy.copy(b_dict2),
               1008: copy.copy(b_dict2),
               'lhn': [[1001, 1002, 1003]]}

        dict_max_pv_area = {1001: 10,
                            1002: 20,
                            1003: 30,
                            1004: 20,
                            1005: 60,
                            1006: 20,
                            1007: 30,
                            1008: 40}

        p1 = point.Point(0, 0)
        p2 = point.Point(10, 0)
        p3 = point.Point(20, 0)
        p4 = point.Point(0, 10)
        p5 = point.Point(10, 10)
        p6 = point.Point(20, 10)
        p7 = point.Point(30, 10)
        p8 = point.Point(30, 0)

        dict_pos = {1001: p1, 1002: p2, 1003: p3, 1004: p4, 1005: p5,
                    1006: p6, 1007: p7, 1008: p8}

        idx_lhn = 0

        lhnchanges.add_lhn_node(ind=ind,
                                idx_lhn=idx_lhn,
                                dict_restr=dict_restr,
                                dict_pos=dict_pos,
                                prob_nodes=[0, 1],
                                prob_lhn_mut=1,
                                prob_no_th_sup=1,
                                prob_closest=1)

        assert len(ind['lhn'][0]) > 4

    def test_add_single_lhn(self):
        dict_restr = {'boi': [1],
                      'tes': [2],
                      'chp': [3],
                      'hp_aw': [4],
                      'hp_ww': [5],
                      'eh': [6],
                      'pv': [7],
                      'bat': [8]}

        b_dict = {'boi': 10,
                  'chp': 20,
                  'hp_aw': 0,
                  'hp_ww': 0,
                  'eh': 0,
                  'tes': 30,
                  'pv': 0,
                  'bat': 0}

        b_dict2 = {'boi': 0,
                   'chp': 0,
                   'hp_aw': 0,
                   'hp_ww': 0,
                   'eh': 0,
                   'tes': 0,
                   'pv': 0,
                   'bat': 0}

        ind = {1001: b_dict,
               1002: b_dict2,
               1003: copy.copy(b_dict2),
               1004: copy.copy(b_dict2),
               1005: copy.copy(b_dict2),
               1006: copy.copy(b_dict2),
               1007: copy.copy(b_dict2),
               1008: copy.copy(b_dict2),
               'lhn': []}

        dict_max_pv_area = {1001: 10,
                            1002: 20,
                            1003: 30,
                            1004: 20,
                            1005: 60,
                            1006: 20,
                            1007: 30,
                            1008: 40}

        p1 = point.Point(0, 0)
        p2 = point.Point(10, 0)
        p3 = point.Point(20, 0)
        p4 = point.Point(0, 10)
        p5 = point.Point(10, 10)
        p6 = point.Point(20, 10)
        p7 = point.Point(30, 10)
        p8 = point.Point(30, 0)

        dict_pos = {1001: p1, 1002: p2, 1003: p3, 1004: p4, 1005: p5,
                    1006: p6, 1007: p7, 1008: p8}

        lhnchanges.add_single_lhn(ind, dict_restr, pv_min=0,
                                  dict_max_pv_area=dict_max_pv_area,
                                  dict_pos=dict_pos,
                                  max_dist=None, prob_feed=[0, 1])

        assert len(ind['lhn'][0]) >= 2  # Min. two nodes
        assert len(ind['lhn']) == 1  # Min. one network

        #  Check if number of CHPs is one, number of tes is one
        #  and HPs have been removed
        count_chp = 0
        count_hp_aw = 0
        count_tes = 0
        for i in [1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008]:
            if ind[i]['chp'] > 0:
                count_chp += 1
            if ind[i]['hp_aw'] > 0:
                count_hp_aw += 1
            if ind[i]['tes'] > 0:
                count_tes += 1

        assert count_chp >= 2
        assert count_hp_aw == 0
        assert count_tes >= 2

    def test_del_lhn_node(self):
        dict_restr = {'boi': [1],
                      'tes': [2],
                      'chp': [3],
                      'hp_aw': [4],
                      'hp_ww': [5],
                      'eh': [6],
                      'pv': [7],
                      'bat': [8]}

        b_dict = {'boi': 10,
                  'chp': 20,
                  'hp_aw': 0,
                  'hp_ww': 0,
                  'eh': 0,
                  'tes': 30,
                  'pv': 0,
                  'bat': 0}

        b_dict2 = {'boi': 0,
                   'chp': 0,
                   'hp_aw': 0,
                   'hp_ww': 0,
                   'eh': 0,
                   'tes': 0,
                   'pv': 0,
                   'bat': 0}

        ind = {1001: b_dict,
               1002: b_dict2,
               1003: copy.copy(b_dict2),
               1004: copy.copy(b_dict2),
               1005: copy.copy(b_dict2),
               1006: copy.copy(b_dict2),
               1007: copy.copy(b_dict2),
               1008: copy.copy(b_dict2),
               'lhn': [[1001, 1002, 1003]]}

        dict_max_pv_area = {1001: 10,
                            1002: 20,
                            1003: 30,
                            1004: 20,
                            1005: 60,
                            1006: 20,
                            1007: 30,
                            1008: 40}

        p1 = point.Point(0, 0)
        p2 = point.Point(10, 0)
        p3 = point.Point(20, 0)
        p4 = point.Point(0, 10)
        p5 = point.Point(10, 10)
        p6 = point.Point(20, 10)
        p7 = point.Point(30, 10)
        p8 = point.Point(30, 0)

        dict_pos = {1001: p1, 1002: p2, 1003: p3, 1004: p4, 1005: p5,
                    1006: p6, 1007: p7, 1008: p8}

        idx_lhn = 0

        lhnchanges.del_lhn_node(ind,
                                idx_lhn,
                                dict_restr,
                                pv_min=0,
                                dict_max_pv_area=dict_max_pv_area,
                                dict_pos=dict_pos,
                                prob_nodes=[1, 0],
                                prob_lhn_mut=1)

        assert len(ind['lhn'][0]) == 2

    def test_del_lhn_node2(self):
        dict_restr = {'boi': [1],
                      'tes': [2],
                      'chp': [3],
                      'hp_aw': [4],
                      'hp_ww': [5],
                      'eh': [6],
                      'pv': [7],
                      'bat': [8]}

        b_dict = {'boi': 10,
                  'chp': 20,
                  'hp_aw': 0,
                  'hp_ww': 0,
                  'eh': 0,
                  'tes': 30,
                  'pv': 0,
                  'bat': 0}

        b_dict2 = {'boi': 0,
                   'chp': 0,
                   'hp_aw': 0,
                   'hp_ww': 0,
                   'eh': 0,
                   'tes': 0,
                   'pv': 0,
                   'bat': 0}

        ind = {1001: b_dict,
               1002: b_dict2,
               1003: copy.copy(b_dict2),
               1004: copy.copy(b_dict2),
               1005: copy.copy(b_dict2),
               1006: copy.copy(b_dict2),
               1007: copy.copy(b_dict2),
               1008: copy.copy(b_dict2),
               'lhn': [[1001, 1002, 1003, 1004]]}

        dict_max_pv_area = {1001: 10,
                            1002: 20,
                            1003: 30,
                            1004: 20,
                            1005: 60,
                            1006: 20,
                            1007: 30,
                            1008: 40}

        p1 = point.Point(0, 0)
        p2 = point.Point(10, 0)
        p3 = point.Point(20, 0)
        p4 = point.Point(0, 10)
        p5 = point.Point(10, 10)
        p6 = point.Point(20, 10)
        p7 = point.Point(30, 10)
        p8 = point.Point(30, 0)

        dict_pos = {1001: p1, 1002: p2, 1003: p3, 1004: p4, 1005: p5,
                    1006: p6, 1007: p7, 1008: p8}

        idx_lhn = 0

        lhnchanges.del_lhn_node(ind,
                                idx_lhn,
                                dict_restr,
                                pv_min=0,
                                dict_max_pv_area=dict_max_pv_area,
                                dict_pos=dict_pos,
                                prob_nodes=[0, 1],
                                prob_lhn_mut=1)

        assert len(ind['lhn'][0]) == 2

    def test_add_lhn_feeder_node(self):
        dict_restr = {'boi': [1],
                      'tes': [2],
                      'chp': [3],
                      'hp_aw': [4],
                      'hp_ww': [5],
                      'eh': [6],
                      'pv': [7],
                      'bat': [8]}

        b_dict = {'boi': 10,
                  'chp': 20,
                  'hp_aw': 0,
                  'hp_ww': 0,
                  'eh': 0,
                  'tes': 30,
                  'pv': 0,
                  'bat': 0}

        b_dict2 = {'boi': 0,
                   'chp': 0,
                   'hp_aw': 0,
                   'hp_ww': 0,
                   'eh': 0,
                   'tes': 0,
                   'pv': 0,
                   'bat': 0}

        ind = {1001: b_dict,
               1002: b_dict2,
               1003: copy.copy(b_dict2),
               1004: copy.copy(b_dict2),
               1005: copy.copy(b_dict2),
               1006: copy.copy(b_dict2),
               1007: copy.copy(b_dict2),
               1008: copy.copy(b_dict2),
               'lhn': [[1001, 1002, 1003, 1004]]}

        dict_max_pv_area = {1001: 10,
                            1002: 20,
                            1003: 30,
                            1004: 20,
                            1005: 60,
                            1006: 20,
                            1007: 30,
                            1008: 40}

        p1 = point.Point(0, 0)
        p2 = point.Point(10, 0)
        p3 = point.Point(20, 0)
        p4 = point.Point(0, 10)
        p5 = point.Point(10, 10)
        p6 = point.Point(20, 10)
        p7 = point.Point(30, 10)
        p8 = point.Point(30, 0)

        dict_pos = {1001: p1, 1002: p2, 1003: p3, 1004: p4, 1005: p5,
                    1006: p6, 1007: p7, 1008: p8}

        idx_lhn = 0

        lhnchanges.add_lhn_feeder_node(ind, idx_lhn, dict_restr, pv_min=0,
                                       dict_max_pv_area=dict_max_pv_area,
                                       prob_feed=[1, 0], prob_lhn_mut=1)

        assert len(ind['lhn'][0]) == 4

        #  Check if another CHP has been added
        count_chp = 0
        count_hp_aw = 0
        count_tes = 0
        for i in [1001, 1002, 1003, 1004]:
            if ind[i]['chp'] > 0:
                count_chp += 1
            if ind[i]['hp_aw'] > 0:
                count_hp_aw += 1
            if ind[i]['tes'] > 0:
                count_tes += 1

        assert count_chp == 2
        assert count_hp_aw == 0
        assert count_tes == 2

    def test_del_lhn_feeder(self):
        dict_restr = {'boi': [1],
                      'tes': [2],
                      'chp': [3],
                      'hp_aw': [4],
                      'hp_ww': [5],
                      'eh': [6],
                      'pv': [7],
                      'bat': [8]}

        b_dict = {'boi': 10,
                  'chp': 20,
                  'hp_aw': 0,
                  'hp_ww': 0,
                  'eh': 0,
                  'tes': 30,
                  'pv': 0,
                  'bat': 0}

        b_dict2 = {'boi': 0,
                   'chp': 0,
                   'hp_aw': 0,
                   'hp_ww': 0,
                   'eh': 0,
                   'tes': 0,
                   'pv': 0,
                   'bat': 0}

        ind = {1001: b_dict,
               1002: b_dict2,
               1003: copy.copy(b_dict),
               1004: copy.copy(b_dict2),
               1005: copy.copy(b_dict2),
               1006: copy.copy(b_dict2),
               1007: copy.copy(b_dict2),
               1008: copy.copy(b_dict2),
               'lhn': [[1001, 1002, 1003, 1004]]}

        dict_max_pv_area = {1001: 10,
                            1002: 20,
                            1003: 30,
                            1004: 20,
                            1005: 60,
                            1006: 20,
                            1007: 30,
                            1008: 40}

        p1 = point.Point(0, 0)
        p2 = point.Point(10, 0)
        p3 = point.Point(20, 0)
        p4 = point.Point(0, 10)
        p5 = point.Point(10, 10)
        p6 = point.Point(20, 10)
        p7 = point.Point(30, 10)
        p8 = point.Point(30, 0)

        dict_pos = {1001: p1, 1002: p2, 1003: p3, 1004: p4, 1005: p5,
                    1006: p6, 1007: p7, 1008: p8}

        idx_lhn = 0

        lhnchanges.del_lhn_feeder(ind, idx_lhn, prob_feed=[1, 0],
                                  prob_lhn_mut=1)

        assert len(ind['lhn'][0]) == 4

        #  Check if number of CHPs is one, number of tes is one
        #  and HPs have been removed
        count_chp = 0
        count_hp_aw = 0
        count_tes = 0
        for i in [1001, 1002, 1003, 1004]:
            if ind[i]['chp'] > 0:
                count_chp += 1
            if ind[i]['hp_aw'] > 0:
                count_hp_aw += 1
            if ind[i]['tes'] > 0:
                count_tes += 1

        assert count_chp == 1
        assert count_hp_aw == 0
        assert count_tes == 1

    def test_del_lhn_feeder(self):
        dict_restr = {'boi': [1],
                      'tes': [2],
                      'chp': [3],
                      'hp_aw': [4],
                      'hp_ww': [5],
                      'eh': [6],
                      'pv': [7],
                      'bat': [8]}

        b_dict = {'boi': 10,
                  'chp': 20,
                  'hp_aw': 0,
                  'hp_ww': 0,
                  'eh': 0,
                  'tes': 30,
                  'pv': 0,
                  'bat': 0}

        b_dict2 = {'boi': 0,
                   'chp': 0,
                   'hp_aw': 0,
                   'hp_ww': 0,
                   'eh': 0,
                   'tes': 0,
                   'pv': 0,
                   'bat': 0}

        ind = {1001: b_dict,
               1002: copy.copy(b_dict),
               1003: copy.copy(b_dict),
               1004: copy.copy(b_dict2),
               1005: copy.copy(b_dict2),
               1006: copy.copy(b_dict2),
               1007: copy.copy(b_dict2),
               1008: copy.copy(b_dict2),
               'lhn': [[1001, 1002, 1003, 1004]]}

        dict_max_pv_area = {1001: 10,
                            1002: 20,
                            1003: 30,
                            1004: 20,
                            1005: 60,
                            1006: 20,
                            1007: 30,
                            1008: 40}

        p1 = point.Point(0, 0)
        p2 = point.Point(10, 0)
        p3 = point.Point(20, 0)
        p4 = point.Point(0, 10)
        p5 = point.Point(10, 10)
        p6 = point.Point(20, 10)
        p7 = point.Point(30, 10)
        p8 = point.Point(30, 0)

        dict_pos = {1001: p1, 1002: p2, 1003: p3, 1004: p4, 1005: p5,
                    1006: p6, 1007: p7, 1008: p8}

        idx_lhn = 0

        lhnchanges.del_lhn_feeder(ind, idx_lhn, prob_feed=[0, 1],
                                  prob_lhn_mut=1)

        assert len(ind['lhn'][0]) == 4

        #  Check if number of CHPs is one, number of tes is one
        #  and HPs have been removed
        count_chp = 0
        count_hp_aw = 0
        count_tes = 0
        for i in [1001, 1002, 1003, 1004]:
            if ind[i]['chp'] > 0:
                count_chp += 1
            if ind[i]['hp_aw'] > 0:
                count_hp_aw += 1
            if ind[i]['tes'] > 0:
                count_tes += 1

        assert count_chp == 1
        assert count_hp_aw == 0
        assert count_tes == 1

    def test_change_lhn_feeder_node(self):
        dict_restr = {'boi': [1],
                      'tes': [2],
                      'chp': [3],
                      'hp_aw': [4],
                      'hp_ww': [5],
                      'eh': [6],
                      'pv': [7],
                      'bat': [8]}

        b_dict = {'boi': 10,
                  'chp': 20,
                  'hp_aw': 0,
                  'hp_ww': 0,
                  'eh': 0,
                  'tes': 30,
                  'pv': 0,
                  'bat': 0}

        b_dict2 = {'boi': 0,
                   'chp': 0,
                   'hp_aw': 0,
                   'hp_ww': 0,
                   'eh': 0,
                   'tes': 0,
                   'pv': 0,
                   'bat': 0}

        ind = {1001: b_dict,
               1002: b_dict2,
               1003: copy.copy(b_dict2),
               1004: copy.copy(b_dict2),
               1005: copy.copy(b_dict2),
               1006: copy.copy(b_dict2),
               1007: copy.copy(b_dict2),
               1008: copy.copy(b_dict2),
               'lhn': [[1001, 1002, 1003, 1004]]}

        dict_max_pv_area = {1001: 10,
                            1002: 20,
                            1003: 30,
                            1004: 20,
                            1005: 60,
                            1006: 20,
                            1007: 30,
                            1008: 40}

        p1 = point.Point(0, 0)
        p2 = point.Point(10, 0)
        p3 = point.Point(20, 0)
        p4 = point.Point(0, 10)
        p5 = point.Point(10, 10)
        p6 = point.Point(20, 10)
        p7 = point.Point(30, 10)
        p8 = point.Point(30, 0)

        dict_pos = {1001: p1, 1002: p2, 1003: p3, 1004: p4, 1005: p5,
                    1006: p6, 1007: p7, 1008: p8}

        idx_lhn = 0

        lhnchanges.change_lhn_feeder_node(ind, idx_lhn, dict_restr, pv_min=0,
                                          dict_max_pv_area=dict_max_pv_area,
                                          prob_feed=[1, 0],
                                          prob_lhn_mut=1)

        assert len(ind['lhn'][0]) == 4

        #  Check if number of CHPs is one, number of tes is one
        #  and HPs have been removed
        count_chp = 0
        count_hp_aw = 0
        count_tes = 0
        for i in [1001, 1002, 1003, 1004]:
            if ind[i]['chp'] > 0:
                count_chp += 1
            if ind[i]['hp_aw'] > 0:
                count_hp_aw += 1
            if ind[i]['tes'] > 0:
                count_tes += 1

        assert count_chp == 1
        assert count_hp_aw == 0
        assert count_tes == 1

        assert ind[1001]['chp'] == 0  # CHP moved to other node
