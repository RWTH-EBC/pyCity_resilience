#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

"""
from __future__ import division

import pycity_resilience.ga.evolution.esys_changes as esyschanges


class TestEsysChanges():
    def test_gen_boiler_only(self):
        n = 1001

        dict_restr = {'boi': [1],
                      'tes': [2],
                      'chp': [3],
                      'hp_aw': [4],
                      'hp_ww': [5],
                      'eh': [6],
                      'bat': [7]}

        #  Test building dict
        b_dict = {'boi': 10,
                  'chp': 20,
                  'hp_aw': 30,
                  'hp_ww': 40,
                  'eh': 50,
                  'tes': 60,
                  'pv': 0,
                  'bat': 70}

        ind = {n: b_dict, 'lhn': []}

        esyschanges.gen_boiler_only(ind=ind, n=n, dict_restr=dict_restr)

        assert ind[n]['boi'] > 0
        assert ind[n]['chp'] == 0
        assert ind[n]['hp_aw'] == 0
        assert ind[n]['hp_ww'] == 0
        assert ind[n]['eh'] == 0
        assert ind[n]['tes'] == 0

        assert ind[n]['bat'] == 0

    def test_gen_boi_tes(self):
        n = 1001

        dict_restr = {'boi': [1],
                      'tes': [2],
                      'chp': [3],
                      'hp_aw': [4],
                      'hp_ww': [5],
                      'eh': [6],
                      'bat': [7]}

        #  Test building dict
        b_dict = {'boi': 10,
                  'chp': 20,
                  'hp_aw': 30,
                  'hp_ww': 40,
                  'eh': 50,
                  'tes': 60,
                  'pv': 0,
                  'bat': 70}

        ind = {n: b_dict, 'lhn': []}

        esyschanges.gen_boi_tes(ind=ind, n=n, dict_restr=dict_restr)

        assert ind[n]['boi'] > 0
        assert ind[n]['chp'] == 0
        assert ind[n]['hp_aw'] == 0
        assert ind[n]['hp_ww'] == 0
        assert ind[n]['eh'] == 0
        assert ind[n]['tes'] > 0

        assert ind[n]['bat'] == 0

    def test_gen_chp_boi_tes(self):
        n = 1001

        dict_restr = {'boi': [1],
                      'tes': [2],
                      'chp': [3],
                      'hp_aw': [4],
                      'hp_ww': [5],
                      'eh': [6],
                      'bat': [7]}

        #  Test building dict
        b_dict = {'boi': 10,
                  'chp': 20,
                  'hp_aw': 30,
                  'hp_ww': 40,
                  'eh': 50,
                  'tes': 60,
                  'pv': 0,
                  'bat': 70}

        ind = {n: b_dict, 'lhn': []}

        esyschanges.gen_chp_boi_tes(ind=ind, n=n, dict_restr=dict_restr)

        assert ind[n]['boi'] > 0
        assert ind[n]['chp'] > 0
        assert ind[n]['hp_aw'] == 0
        assert ind[n]['hp_ww'] == 0
        assert ind[n]['eh'] == 0
        assert ind[n]['tes'] > 0

        assert ind[n]['bat'] == 70

    def test_gen_chp_boi_eh_tes(self):
        n = 1001

        dict_restr = {'boi': [1],
                      'tes': [2],
                      'chp': [3],
                      'hp_aw': [4],
                      'hp_ww': [5],
                      'eh': [6],
                      'bat': [7]}

        #  Test building dict
        b_dict = {'boi': 10,
                  'chp': 20,
                  'hp_aw': 30,
                  'hp_ww': 40,
                  'eh': 50,
                  'tes': 60,
                  'pv': 0,
                  'bat': 70}

        ind = {n: b_dict, 'lhn': []}

        esyschanges.gen_chp_boi_eh_tes(ind=ind, n=n, dict_restr=dict_restr)

        assert ind[n]['boi'] > 0
        assert ind[n]['chp'] > 0
        assert ind[n]['hp_aw'] == 0
        assert ind[n]['hp_ww'] == 0
        assert ind[n]['eh'] > 0
        assert ind[n]['tes'] > 0

        assert ind[n]['bat'] == 70

    def test_gen_hp_aw_eh(self):
        n = 1001

        dict_restr = {'boi': [1],
                      'tes': [2],
                      'chp': [3],
                      'hp_aw': [4],
                      'hp_ww': [5],
                      'eh': [6],
                      'bat': [7]}

        #  Test building dict
        b_dict = {'boi': 10,
                  'chp': 20,
                  'hp_aw': 30,
                  'hp_ww': 40,
                  'eh': 50,
                  'tes': 60,
                  'pv': 0,
                  'bat': 70}

        ind = {n: b_dict, 'lhn': []}

        esyschanges.gen_hp_aw_eh(ind=ind, n=n, dict_restr=dict_restr)

        assert ind[n]['boi'] == 0
        assert ind[n]['chp'] == 0
        assert ind[n]['hp_aw'] > 0
        assert ind[n]['hp_ww'] == 0
        assert ind[n]['eh'] > 0
        assert ind[n]['tes'] > 0

        assert ind[n]['bat'] == 0

    def test_gen_hp_ww_eh(self):
        n = 1001

        dict_restr = {'boi': [1],
                      'tes': [2],
                      'chp': [3],
                      'hp_aw': [4],
                      'hp_ww': [5],
                      'eh': [6],
                      'bat': [7]}

        #  Test building dict
        b_dict = {'boi': 10,
                  'chp': 20,
                  'hp_aw': 30,
                  'hp_ww': 40,
                  'eh': 50,
                  'tes': 60,
                  'pv': 0,
                  'bat': 70}

        ind = {n: b_dict, 'lhn': []}

        esyschanges.gen_hp_ww_eh(ind=ind, n=n, dict_restr=dict_restr)

        assert ind[n]['boi'] == 0
        assert ind[n]['chp'] == 0
        assert ind[n]['hp_aw'] == 0
        assert ind[n]['hp_ww'] > 0
        assert ind[n]['eh'] > 0
        assert ind[n]['tes'] > 0

        assert ind[n]['bat'] == 0

    def test_gen_hp_aw_boi(self):
        n = 1001

        dict_restr = {'boi': [1],
                      'tes': [2],
                      'chp': [3],
                      'hp_aw': [4],
                      'hp_ww': [5],
                      'eh': [6],
                      'bat': [7]}

        #  Test building dict
        b_dict = {'boi': 10,
                  'chp': 20,
                  'hp_aw': 30,
                  'hp_ww': 40,
                  'eh': 50,
                  'tes': 60,
                  'pv': 0,
                  'bat': 70}

        ind = {n: b_dict, 'lhn': []}

        esyschanges.gen_hp_aw_boi(ind=ind, n=n, dict_restr=dict_restr)

        assert ind[n]['boi'] > 0
        assert ind[n]['chp'] == 0
        assert ind[n]['hp_aw'] > 0
        assert ind[n]['hp_ww'] == 0
        assert ind[n]['eh'] == 0
        assert ind[n]['tes'] > 0

        assert ind[n]['bat'] == 0

    def test_gen_hp_ww_boi(self):
        n = 1001

        dict_restr = {'boi': [1],
                      'tes': [2],
                      'chp': [3],
                      'hp_aw': [4],
                      'hp_ww': [5],
                      'eh': [6],
                      'bat': [7]}

        #  Test building dict
        b_dict = {'boi': 10,
                  'chp': 20,
                  'hp_aw': 30,
                  'hp_ww': 40,
                  'eh': 50,
                  'tes': 60,
                  'pv': 0,
                  'bat': 70}

        ind = {n: b_dict, 'lhn': []}

        esyschanges.gen_hp_ww_boi(ind=ind, n=n, dict_restr=dict_restr)

        assert ind[n]['boi'] > 0
        assert ind[n]['chp'] == 0
        assert ind[n]['hp_aw'] == 0
        assert ind[n]['hp_ww'] > 0
        assert ind[n]['eh']== 0
        assert ind[n]['tes'] > 0

        assert ind[n]['bat'] == 0

    def test_gen_hp_aw_boi_eh(self):
        n = 1001

        dict_restr = {'boi': [1],
                      'tes': [2],
                      'chp': [3],
                      'hp_aw': [4],
                      'hp_ww': [5],
                      'eh': [6],
                      'bat': [7]}

        #  Test building dict
        b_dict = {'boi': 10,
                  'chp': 20,
                  'hp_aw': 30,
                  'hp_ww': 40,
                  'eh': 50,
                  'tes': 60,
                  'pv': 0,
                  'bat': 70}

        ind = {n: b_dict, 'lhn': []}

        esyschanges.gen_hp_aw_boi_eh(ind=ind, n=n, dict_restr=dict_restr)

        assert ind[n]['boi'] > 0
        assert ind[n]['chp'] == 0
        assert ind[n]['hp_aw'] > 0
        assert ind[n]['hp_ww'] == 0
        assert ind[n]['eh'] > 0
        assert ind[n]['tes'] > 0

        assert ind[n]['bat'] == 0

    def test_gen_hp_ww_boi_eh(self):
        n = 1001

        dict_restr = {'boi': [1],
                      'tes': [2],
                      'chp': [3],
                      'hp_aw': [4],
                      'hp_ww': [5],
                      'eh': [6],
                      'bat': [7]}

        #  Test building dict
        b_dict = {'boi': 10,
                  'chp': 20,
                  'hp_aw': 30,
                  'hp_ww': 40,
                  'eh': 50,
                  'tes': 60,
                  'pv': 0,
                  'bat': 70}

        ind = {n: b_dict, 'lhn': []}

        esyschanges.gen_hp_ww_boi_eh(ind=ind, n=n, dict_restr=dict_restr)

        assert ind[n]['boi'] > 0
        assert ind[n]['chp'] == 0
        assert ind[n]['hp_aw'] == 0
        assert ind[n]['hp_ww'] > 0
        assert ind[n]['eh'] > 0
        assert ind[n]['tes'] > 0

        assert ind[n]['bat'] == 0

    def test_gen_or_del_bat1(self):
        n = 1001

        dict_restr = {'boi': [1],
                      'tes': [2],
                      'chp': [3],
                      'hp_aw': [4],
                      'hp_ww': [5],
                      'eh': [6],
                      'bat': [7]}

        #  Test building dict
        b_dict = {'boi': 10,
                  'chp': 20,
                  'hp_aw': 30,
                  'hp_ww': 40,
                  'eh': 50,
                  'tes': 60,
                  'pv': 0,
                  'bat': 70}

        ind = {n: b_dict, 'lhn': []}

        esyschanges.gen_or_del_bat(ind=ind, n=n, dict_restr=dict_restr)

        assert ind[n]['boi'] > 0
        assert ind[n]['chp'] > 0
        assert ind[n]['hp_aw'] > 0
        assert ind[n]['hp_ww'] > 0
        assert ind[n]['eh'] > 0
        assert ind[n]['tes'] > 0

        assert ind[n]['bat'] == 0

    def test_gen_or_del_bat2(self):
        n = 1001

        dict_restr = {'boi': [1],
                      'tes': [2],
                      'chp': [3],
                      'hp_aw': [4],
                      'hp_ww': [5],
                      'eh': [6],
                      'bat': [7]}

        #  Test building dict
        b_dict = {'boi': 10,
                  'chp': 20,
                  'hp_aw': 30,
                  'hp_ww': 40,
                  'eh': 50,
                  'tes': 60,
                  'pv': 0,
                  'bat': 0}

        ind = {n: b_dict, 'lhn': []}

        esyschanges.gen_or_del_bat(ind=ind, n=n, dict_restr=dict_restr)

        assert ind[n]['boi'] > 0
        assert ind[n]['chp'] > 0
        assert ind[n]['hp_aw'] > 0
        assert ind[n]['hp_ww'] > 0
        assert ind[n]['eh'] > 0
        assert ind[n]['tes'] > 0

        assert ind[n]['bat'] > 0

    def test_gen_or_del_bat3(self):
        n = 1001

        dict_restr = {'boi': [1],
                      'tes': [2],
                      'chp': [3],
                      'hp_aw': [4],
                      'hp_ww': [5],
                      'eh': [6],
                      'bat': [7]}

        #  Test building dict
        b_dict = {'boi': 10,
                  'chp': 0,
                  'hp_aw': 30,
                  'hp_ww': 40,
                  'eh': 50,
                  'tes': 60,
                  'pv': 0,
                  'bat': 0}

        ind = {n: b_dict, 'lhn': []}

        esyschanges.gen_or_del_bat(ind=ind, n=n, dict_restr=dict_restr)

        assert ind[n]['boi'] > 0
        assert ind[n]['chp'] == 0
        assert ind[n]['hp_aw'] > 0
        assert ind[n]['hp_ww'] > 0
        assert ind[n]['eh'] > 0
        assert ind[n]['tes'] > 0

        assert ind[n]['bat'] == 0

    def test_gen_or_del_pv1(self):
        n = 1001

        pv_min = 10
        pv_max = 20

        #  Test building dict
        b_dict = {'boi': 10,
                  'chp': 20,
                  'hp_aw': 30,
                  'hp_ww': 40,
                  'eh': 50,
                  'tes': 60,
                  'pv': 0,
                  'bat': 0}

        ind = {n: b_dict, 'lhn': []}

        esyschanges.gen_or_del_pv(ind=ind, n=n, pv_min=pv_min, pv_max=pv_max)

        assert ind[n]['boi'] > 0
        assert ind[n]['chp'] > 0
        assert ind[n]['hp_aw'] > 0
        assert ind[n]['hp_ww'] > 0
        assert ind[n]['eh'] > 0
        assert ind[n]['tes'] > 0

        assert ind[n]['bat'] == 0
        assert ind[n]['pv'] >= pv_min
        assert ind[n]['pv'] <= pv_max

    def test_gen_or_del_pv2(self):
        n = 1001

        pv_min = 10
        pv_max = 20

        #  Test building dict
        b_dict = {'boi': 10,
                  'chp': 20,
                  'hp_aw': 30,
                  'hp_ww': 40,
                  'eh': 50,
                  'tes': 60,
                  'pv': 10,
                  'bat': 0}

        ind = {n: b_dict, 'lhn': []}

        esyschanges.gen_or_del_pv(ind=ind, n=n, pv_min=pv_min, pv_max=pv_max)

        assert ind[n]['boi'] > 0
        assert ind[n]['chp'] > 0
        assert ind[n]['hp_aw'] > 0
        assert ind[n]['hp_ww'] > 0
        assert ind[n]['eh'] > 0
        assert ind[n]['tes'] > 0

        assert ind[n]['bat'] == 0
        assert ind[n]['pv'] == 0

    def test_set_th_supply_off(self):
        n = 1001

        #  Test building dict
        b_dict = {'boi': 10,
                  'chp': 20,
                  'hp_aw': 30,
                  'hp_ww': 40,
                  'eh': 50,
                  'tes': 60,
                  'pv': 0,
                  'bat': 20}

        ind = {n: b_dict, 'lhn': []}

        esyschanges.set_th_supply_off(ind=ind, n=n)

        assert ind[n]['boi'] == 0
        assert ind[n]['chp'] == 0
        assert ind[n]['hp_aw'] == 0
        assert ind[n]['hp_ww'] == 0
        assert ind[n]['eh'] == 0
        assert ind[n]['tes'] == 0

        assert ind[n]['bat'] == 0
