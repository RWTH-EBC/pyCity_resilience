#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

"""
from __future__ import division

import copy

import pycity_resilience.ga.verify.check_validity as checkval


class TestCheckValidity():
    def test_check_no_hp_in_lhn(self):
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

        #  Check if HP is in LHN
        #  ###################################################
        ind_hp_in_lhn = {1001: dict_b1, 1002: dict_b2, 1003: dict_b3,
                         'lhn': [[1001, 1002, 1003]]}

        valid = checkval.check_no_hp_in_lhn(ind=ind_hp_in_lhn)

        assert valid is False

        #  Show if lhn connection 1003 has been deleted
        assert ind_hp_in_lhn['lhn'] == [[1001, 1002]]

    def test_check_lhn_has_min_two_build(self):
        ind_single_b_lhn = {'lhn': [[1001]]}

        valid = checkval.check_lhn_has_min_two_build(ind=ind_single_b_lhn)

        assert valid is False

        assert ind_single_b_lhn['lhn'] == []

    def test_check_pv_max_areas(self):
        #  With HP
        dict_b3 = {'bat': 0,  # in Joule
                   'boi': 0,  # in Watt
                   'chp': 0,
                   'eh': 20000,
                   'hp_aw': 10000,
                   'hp_ww': 0,
                   'pv': 50,  # in m2
                   'tes': 500}  # in kg

        ind_check_pv = {1001: dict_b3, 'lhn': []}

        dict_max_pv_area = {1001: 0}

        valid = checkval.check_pv_max_areas(ind=ind_check_pv,
                                            dict_max_pv_area=dict_max_pv_area)

        assert valid is False
        assert dict_b3['pv'] == 0

    def test_check_bat_only_with_pv_or_chp(self):
        #  Incorrect (with bat without CHP or PV
        dict_b4 = {'bat': 5000,  # in Joule
                   'boi': 10000,  # in Watt
                   'chp': 0,
                   'eh': 0,
                   'hp_aw': 0,
                   'hp_ww': 0,
                   'pv': 0,  # in m2
                   'tes': 300}  # in kg

        ind_check_bat = {1001: dict_b4, 'lhn': []}

        valid = checkval.check_bat_only_with_pv_or_chp(ind=ind_check_bat)

        assert valid is False
        assert dict_b4['bat'] == 0

    def test_check_lhn_th_supply(self):
        #  (No thermal feeder)
        dict_b5 = {'bat': 5000,  # in Joule
                   'boi': 0,  # in Watt
                   'chp': 0,
                   'eh': 0,
                   'hp_aw': 0,
                   'hp_ww': 0,
                   'pv': 50,  # in m2
                   'tes': 300}  # in kg

        dict_b5_copy = copy.deepcopy(dict_b5)

        ind_lhn_no_feeder = {1001: dict_b5, 1002: dict_b5_copy,
                             'lhn': [[1001, 1002]]}

        valid = checkval.check_lhn_th_supply(ind=ind_lhn_no_feeder,
                                             do_random=False)

        assert valid is False
        assert dict_b5['boi'] > 0 or dict_b5_copy['boi'] > 0

    def test_check_lhn_th_supply2(self):
        #  (No thermal feeder)
        dict_b5 = {'bat': 5000,  # in Joule
                   'boi': 0,  # in Watt
                   'chp': 0,
                   'eh': 0,
                   'hp_aw': 0,
                   'hp_ww': 0,
                   'pv': 50,  # in m2
                   'tes': 300}  # in kg

        dict_1002 = copy.deepcopy(dict_b5)
        dict_1003 = copy.deepcopy(dict_b5)
        dict_1004 = copy.deepcopy(dict_b5)

        ind_lhn_no_feeder = {1001: dict_b5, 1002: dict_1002,
                             1003: dict_1003,
                             1004: dict_1004,
                             'lhn': [[1001, 1003], [1002, 1004]]}

        valid = checkval.check_lhn_th_supply(ind=ind_lhn_no_feeder,
                                             do_random=False)

        assert valid is False
        assert dict_b5['boi'] > 0 or dict_1003['boi'] > 0
        assert dict_1002['boi'] > 0 or dict_1004['boi'] > 0

    def test_check_stand_alone_build_th(self):
        #  (No thermal feeder)
        dict_b5 = {'bat': 5000,  # in Joule
                   'boi': 0,  # in Watt
                   'chp': 0,
                   'eh': 0,
                   'hp_aw': 0,
                   'hp_ww': 0,
                   'pv': 50,  # in m2
                   'tes': 300}  # in kg

        ind_no_th_feeder = {1001: dict_b5, 'lhn': [[1002, 1003]]}

        valid = checkval.check_stand_alone_build_th(ind=ind_no_th_feeder,
                                                    do_random=False)

        assert valid is False
        assert dict_b5['boi'] > 0 or dict_b5['chp'] > 0 or \
               dict_b5['hp_aw'] > 0 or dict_b5['hp_ww'] > 0

    def test_check_no_chp_plus_hp(self):
        #  Invalid (HP + CHP)
        dict_b = {'bat': 5000,  # in Joule
                  'boi': 10000,  # in Watt
                  'chp': 1000,
                  'eh': 0,
                  'hp_aw': 10000,
                  'hp_ww': 0,
                  'pv': 50,  # in m2
                  'tes': 500}  # in kg

        ind_chp_and_hp = {1001: dict_b, 'lhn': []}

        assert checkval.check_no_chp_plus_hp(ind=ind_chp_and_hp) is False

        assert dict_b['chp'] == 0 or dict_b['hp_aw'] == 0

        #  Invalid (HP + CHP)
        dict_b = {'bat': 5000,  # in Joule
                  'boi': 10000,  # in Watt
                  'chp': 1000,
                  'eh': 0,
                  'hp_aw': 10000,
                  'hp_ww': 0,
                  'pv': 50,  # in m2
                  'tes': 500}  # in kg

        ind_chp_and_hp = {1001: dict_b, 'lhn': [[1001, 1002]]}

        assert checkval.check_no_chp_plus_hp(ind=ind_chp_and_hp) is False

        assert dict_b['chp'] > 0 and dict_b['hp_aw'] == 0

    def test_check_ind_is_valid(self):

        ind_valid = {1001: {}, 1002: {}, 1003: {}, 'lhn': []}

        assert checkval.check_ind_is_valid(ind=ind_valid) is True

        ind_invalid = {1001: {}, 1002: {}, 1003: {}}

        assert checkval.check_ind_is_valid(ind=ind_invalid) is False

        ind_invalid = {1001: {}, 1002: {}, 1003: {}, 'lhn': [[1004, 1005]]}

        assert checkval.check_ind_is_valid(ind=ind_invalid) is False

        ind_invalid = {1001: {}, 1002: {}, 1003: {}, 'lhn': None}

        assert checkval.check_ind_is_valid(ind=ind_invalid) is False

    def test_check_lhn_th_supply3(self):
        #  (No thermal feeder)
        chp_size = 10000
        boi_size = 30000
        tes_size = 500
        pv_area = 30

        dict_b1 = {'chp': chp_size, 'boi': boi_size, 'tes': tes_size,
                   'eh': 0, 'hp_aw': 0, 'hp_ww': 0, 'pv': pv_area,
                   'bat': 0}

        dict_no = {'chp': 0, 'boi': 0, 'tes': 0,
                   'eh': 0, 'hp_aw': 0, 'hp_ww': 0, 'pv': 0,
                   'bat': 0}

        dict_1002 = copy.deepcopy(dict_no)
        dict_1003 = copy.deepcopy(dict_no)
        dict_1004 = copy.deepcopy(dict_no)

        ind_lhn_no_feeder = {1001: dict_b1, 1002: dict_1002,
                             1003: dict_1003,
                             1004: dict_1004,
                             'lhn': [[1001, 1002], [1003, 1004]]}

        valid = checkval.check_lhn_th_supply(ind=ind_lhn_no_feeder,
                                             do_random=False)

        assert valid is False
        assert ind_lhn_no_feeder[1003]['boi'] > 0 or \
               ind_lhn_no_feeder[1004]['boi'] > 0

    def test_check_no_boi_lhn_only(self):
        dict_b1 = {'bat': 0,  # in Joule
                   'boi': 200000,  # in Watt
                   'chp': 0,
                   'eh': 0,
                   'hp_aw': 0,
                   'hp_ww': 0,
                   'pv': 50,  # in m2
                   'tes': 300}  # in kg

        dict_b2 = {'bat': 0,  # in Joule
                   'boi': 200000,  # in Watt
                   'chp': 20000,
                   'eh': 0,
                   'hp_aw': 0,
                   'hp_ww': 0,
                   'pv': 50,  # in m2
                   'tes': 5000}  # in kg

        #  (No thermal feeder)
        dict_b3 = {'bat': 0,  # in Joule
                   'boi': 0,  # in Watt
                   'chp': 0,
                   'eh': 0,
                   'hp_aw': 0,
                   'hp_ww': 0,
                   'pv': 50,  # in m2
                   'tes': 0}  # in kg

        ind_lhns = {1001: dict_b1,
                    1002: dict_b2,
                    1003: dict_b3,
                    1004: dict_b3,
                    'lhn': [[1001, 1003], [1002, 1004]]}

        dict_sh = {1001: 100000,
                   1002: 50000,
                   1003: 100000,
                   1004: 50000}

        dict_restr = {'boi': [100000],
                      'tes': [2000],
                      'chp': [30000],
                      'hp_aw': [40000],
                      'hp_ww': [50000],
                      'eh': [60000],
                      'bat': [80000]}

        valid = checkval.check_no_boi_lhn_only(ind=ind_lhns, dict_sh=dict_sh,
                                               dict_restr=dict_restr)

        assert valid is False

        #  Check, if CHP has been added to
        assert dict_b1['chp'] > 0 and dict_b1['boi'] > 0 and dict_b1['tes'] > 0
        assert dict_b2['boi'] > 0 and dict_b2['chp'] > 0

    def test_check_no_boi_lhn_only2(self):
        dict_b1 = {'bat': 0,  # in Joule
                   'boi': 200000,  # in Watt
                   'chp': 0,
                   'eh': 0,
                   'hp_aw': 0,
                   'hp_ww': 0,
                   'pv': 50,  # in m2
                   'tes': 300}  # in kg

        dict_b2 = {'bat': 0,  # in Joule
                   'boi': 200000,  # in Watt
                   'chp': 20000,
                   'eh': 0,
                   'hp_aw': 0,
                   'hp_ww': 0,
                   'pv': 50,  # in m2
                   'tes': 5000}  # in kg

        #  (No thermal feeder)
        dict_b3 = {'bat': 0,  # in Joule
                   'boi': 0,  # in Watt
                   'chp': 0,
                   'eh': 0,
                   'hp_aw': 0,
                   'hp_ww': 0,
                   'pv': 50,  # in m2
                   'tes': 0}  # in kg

        ind_lhns = {1001: dict_b1,
                    1002: dict_b2,
                    1003: dict_b3,
                    1004: dict_b3,
                    'lhn': [[1001, 1003], [1002, 1004]]}

        dict_restr = {'boi': [100000],
                      'tes': [2000],
                      'chp': [30000],
                      'hp_aw': [40000],
                      'hp_ww': [50000],
                      'eh': [60000],
                      'bat': [80000]}

        valid = checkval.check_no_boi_lhn_only(ind=ind_lhns,
                                               dict_restr=dict_restr)

        assert valid is False

        #  Check, if CHP has been added to
        assert (dict_b1['chp'] > 0 and dict_b1['boi'] > 0 or
                dict_b3['boi'] > 0 and dict_b3['chp'] > 0)
