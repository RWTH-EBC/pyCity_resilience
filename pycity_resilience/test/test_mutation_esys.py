#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

"""
from __future__ import division

import pycity_resilience.ga.evolution.mutation_esys as mutateesys


class TestMutationEsys():
    def test_mut_esys_val_single_build(self):
        n = 1001
        prob_mut = 1

        dict_restr = {'boi': [1],
                      'tes': [2],
                      'chp': [3],
                      'hp_aw': [4],
                      'hp_ww': [5],
                      'eh': [6],
                      'bat': [7]}

        #  Test building dict  (mutate all esys, except heat pumps)
        b_dict = {'boi': 0.5,
                  'chp': 1,
                  'hp_aw': 0,
                  'hp_ww': 0,
                  'eh': 1,
                  'tes': 1,
                  'pv': 1,
                  'bat': 1}

        ind = {n: b_dict, 'lhn': []}

        pv_min = 5
        dict_max_pv_area = {1001: 50}

        mutateesys.mut_esys_val_single_build(ind=ind, n=n,
                                             prob_mut=prob_mut,
                                             dict_restr=dict_restr,
                                             pv_min=pv_min,
                                             dict_max_pv_area=dict_max_pv_area)

        assert ind[n]['boi'] == 1
        assert ind[n]['tes'] == 2
        assert ind[n]['chp'] == 3
        assert ind[n]['hp_aw'] == 0
        assert ind[n]['hp_ww'] == 0
        assert ind[n]['eh'] == 6
        assert ind[n]['bat'] == 7
        assert ind[n]['pv'] > 0

    def test_mut_esys_config_single_build(self):
        n = 1001

        dict_restr = {'boi': [1],
                      'tes': [2],
                      'chp': [3],
                      'hp_aw': [4],
                      'hp_ww': [5],
                      'eh': [6],
                      'bat': [7]}

        #  Test building dict  (mutate all esys, except heat pumps)
        b_dict = {'boi': 0,
                  'chp': 1,
                  'hp_aw': 1,
                  'hp_ww': 1,
                  'eh': 1,
                  'tes': 1,
                  'pv': 1,
                  'bat': 1}

        ind = {n: b_dict, 'lhn': []}

        pv_min = 0.5
        dict_max_pv_area = {1001: 50}

        list_options = ['boi']
        list_opt_prob = [1]

        mutateesys.mut_esys_config_single_build(ind, n, dict_restr, pv_min,
                                                dict_max_pv_area,
                                                list_options=list_options,
                                                list_opt_prob=list_opt_prob,
                                                list_lhn_opt=None,
                                                list_lhn_prob=None)

        assert ind[n]['boi'] == 1
        assert ind[n]['tes'] == 0
        assert ind[n]['chp'] == 0
        assert ind[n]['hp_aw'] == 0
        assert ind[n]['hp_ww'] == 0
        assert ind[n]['eh'] == 0
        assert ind[n]['bat'] == 1
        assert ind[n]['pv'] == 1

    def test_mut_esys_config_single_build2(self):
        n = 1001

        dict_restr = {'boi': [1],
                      'tes': [2],
                      'chp': [3],
                      'hp_aw': [4],
                      'hp_ww': [5],
                      'eh': [6],
                      'bat': [7]}

        #  Test building dict  (mutate all esys, except heat pumps)
        b_dict = {'boi': 0,
                  'chp': 1,
                  'hp_aw': 1,
                  'hp_ww': 1,
                  'eh': 1,
                  'tes': 0,
                  'pv': 1,
                  'bat': 1}

        ind = {n: b_dict, 'lhn': []}

        pv_min = 0.5
        dict_max_pv_area = {1001: 50}

        list_options = ['boi_tes']
        list_opt_prob = [1]

        mutateesys.mut_esys_config_single_build(ind, n, dict_restr, pv_min,
                                                dict_max_pv_area,
                                                list_options=list_options,
                                                list_opt_prob=list_opt_prob,
                                                list_lhn_opt=None,
                                                list_lhn_prob=None)

        assert ind[n]['boi'] == 1
        assert ind[n]['tes'] == 2
        assert ind[n]['chp'] == 0
        assert ind[n]['hp_aw'] == 0
        assert ind[n]['hp_ww'] == 0
        assert ind[n]['eh'] == 0
        assert ind[n]['bat'] == 1
        assert ind[n]['pv'] == 1

    def test_mut_esys_config_single_build3(self):
        n = 1001

        dict_restr = {'boi': [1],
                      'tes': [2],
                      'chp': [3],
                      'hp_aw': [4],
                      'hp_ww': [5],
                      'eh': [6],
                      'bat': [7]}

        #  Test building dict  (mutate all esys, except heat pumps)
        b_dict = {'boi': 0,
                  'chp': 0,
                  'hp_aw': 1,
                  'hp_ww': 1,
                  'eh': 1,
                  'tes': 0,
                  'pv': 1,
                  'bat': 1}

        ind = {n: b_dict, 'lhn': []}

        pv_min = 0.5
        dict_max_pv_area = {1001: 50}

        list_options = ['chp_boi_tes']
        list_opt_prob = [1]

        mutateesys.mut_esys_config_single_build(ind, n, dict_restr, pv_min,
                                                dict_max_pv_area,
                                                list_options=list_options,
                                                list_opt_prob=list_opt_prob,
                                                list_lhn_opt=None,
                                                list_lhn_prob=None)

        assert ind[n]['boi'] == 1
        assert ind[n]['tes'] == 2
        assert ind[n]['chp'] == 3
        assert ind[n]['hp_aw'] == 0
        assert ind[n]['hp_ww'] == 0
        assert ind[n]['eh'] == 0
        assert ind[n]['bat'] == 1
        assert ind[n]['pv'] == 1

    def test_mut_esys_config_single_build4(self):
        n = 1001

        dict_restr = {'boi': [1],
                      'tes': [2],
                      'chp': [3],
                      'hp_aw': [4],
                      'hp_ww': [5],
                      'eh': [6],
                      'bat': [7]}

        #  Test building dict  (mutate all esys, except heat pumps)
        b_dict = {'boi': 0,
                  'chp': 0,
                  'hp_aw': 1,
                  'hp_ww': 1,
                  'eh': 0,
                  'tes': 0,
                  'pv': 1,
                  'bat': 1}

        ind = {n: b_dict, 'lhn': []}

        pv_min = 0.5
        dict_max_pv_area = {1001: 50}

        list_options = ['chp_boi_eh_tes']
        list_opt_prob = [1]

        mutateesys.mut_esys_config_single_build(ind, n, dict_restr, pv_min,
                                                dict_max_pv_area,
                                                list_options=list_options,
                                                list_opt_prob=list_opt_prob,
                                                list_lhn_opt=None,
                                                list_lhn_prob=None)

        assert ind[n]['boi'] == 1
        assert ind[n]['tes'] == 2
        assert ind[n]['chp'] == 3
        assert ind[n]['hp_aw'] == 0
        assert ind[n]['hp_ww'] == 0
        assert ind[n]['eh'] == 6
        assert ind[n]['bat'] == 1
        assert ind[n]['pv'] == 1

    def test_mut_esys_config_single_build5(self):
        n = 1001

        dict_restr = {'boi': [1],
                      'tes': [2],
                      'chp': [3],
                      'hp_aw': [4],
                      'hp_ww': [5],
                      'eh': [6],
                      'bat': [7]}

        #  Test building dict  (mutate all esys, except heat pumps)
        b_dict = {'boi': 1,
                  'chp': 1,
                  'hp_aw': 0,
                  'hp_ww': 1,
                  'eh': 1,
                  'tes': 0,
                  'pv': 1,
                  'bat': 1}

        ind = {n: b_dict, 'lhn': []}

        pv_min = 0.5
        dict_max_pv_area = {1001: 50}

        list_options = ['hp_aw_eh']
        list_opt_prob = [1]

        mutateesys.mut_esys_config_single_build(ind, n, dict_restr, pv_min,
                                                dict_max_pv_area,
                                                list_options=list_options,
                                                list_opt_prob=list_opt_prob,
                                                list_lhn_opt=None,
                                                list_lhn_prob=None)

        assert ind[n]['boi'] == 0
        assert ind[n]['tes'] == 2
        assert ind[n]['chp'] == 0
        assert ind[n]['hp_aw'] == 4
        assert ind[n]['hp_ww'] == 0
        assert ind[n]['eh'] == 6
        assert ind[n]['bat'] == 1
        assert ind[n]['pv'] == 1

    def test_mut_esys_config_single_build6(self):
        n = 1001

        dict_restr = {'boi': [1],
                      'tes': [2],
                      'chp': [3],
                      'hp_aw': [4],
                      'hp_ww': [5],
                      'eh': [6],
                      'bat': [7]}

        #  Test building dict  (mutate all esys, except heat pumps)
        b_dict = {'boi': 1,
                  'chp': 1,
                  'hp_aw': 1,
                  'hp_ww': 0,
                  'eh': 1,
                  'tes': 0,
                  'pv': 1,
                  'bat': 1}

        ind = {n: b_dict, 'lhn': []}

        pv_min = 0.5
        dict_max_pv_area = {1001: 50}

        list_options = ['hp_ww_eh']
        list_opt_prob = [1]

        mutateesys.mut_esys_config_single_build(ind, n, dict_restr, pv_min,
                                                dict_max_pv_area,
                                                list_options=list_options,
                                                list_opt_prob=list_opt_prob,
                                                list_lhn_opt=None,
                                                list_lhn_prob=None)

        assert ind[n]['boi'] == 0
        assert ind[n]['tes'] == 2
        assert ind[n]['chp'] == 0
        assert ind[n]['hp_aw'] == 0
        assert ind[n]['hp_ww'] == 5
        assert ind[n]['eh'] == 6
        assert ind[n]['bat'] == 1
        assert ind[n]['pv'] == 1

    def test_mut_esys_config_single_build7(self):
        n = 1001

        dict_restr = {'boi': [1],
                      'tes': [2],
                      'chp': [3],
                      'hp_aw': [4],
                      'hp_ww': [5],
                      'eh': [6],
                      'bat': [7]}

        #  Test building dict  (mutate all esys, except heat pumps)
        b_dict = {'boi': 0,
                  'chp': 1,
                  'hp_aw': 0,
                  'hp_ww': 1,
                  'eh': 1,
                  'tes': 0,
                  'pv': 1,
                  'bat': 1}

        ind = {n: b_dict, 'lhn': []}

        pv_min = 0.5
        dict_max_pv_area = {1001: 50}

        list_options = ['hp_aw_boi']
        list_opt_prob = [1]

        mutateesys.mut_esys_config_single_build(ind, n, dict_restr, pv_min,
                                                dict_max_pv_area,
                                                list_options=list_options,
                                                list_opt_prob=list_opt_prob,
                                                list_lhn_opt=None,
                                                list_lhn_prob=None)

        assert ind[n]['boi'] == 1
        assert ind[n]['tes'] == 2
        assert ind[n]['chp'] == 0
        assert ind[n]['hp_aw'] == 4
        assert ind[n]['hp_ww'] == 0
        assert ind[n]['eh'] == 0
        assert ind[n]['bat'] == 1
        assert ind[n]['pv'] == 1

    def test_mut_esys_config_single_build8(self):
        n = 1001

        dict_restr = {'boi': [1],
                      'tes': [2],
                      'chp': [3],
                      'hp_aw': [4],
                      'hp_ww': [5],
                      'eh': [6],
                      'bat': [7]}

        #  Test building dict  (mutate all esys, except heat pumps)
        b_dict = {'boi': 0,
                  'chp': 1,
                  'hp_aw': 1,
                  'hp_ww': 0,
                  'eh': 1,
                  'tes': 0,
                  'pv': 1,
                  'bat': 1}

        ind = {n: b_dict, 'lhn': []}

        pv_min = 0.5
        dict_max_pv_area = {1001: 50}

        list_options = ['hp_ww_boi']
        list_opt_prob = [1]

        mutateesys.mut_esys_config_single_build(ind, n, dict_restr, pv_min,
                                                dict_max_pv_area,
                                                list_options=list_options,
                                                list_opt_prob=list_opt_prob,
                                                list_lhn_opt=None,
                                                list_lhn_prob=None)

        assert ind[n]['boi'] == 1
        assert ind[n]['tes'] == 2
        assert ind[n]['chp'] == 0
        assert ind[n]['hp_aw'] == 0
        assert ind[n]['hp_ww'] == 5
        assert ind[n]['eh'] == 0
        assert ind[n]['bat'] == 1
        assert ind[n]['pv'] == 1

    def test_mut_esys_config_single_build9(self):
        n = 1001

        dict_restr = {'boi': [1],
                      'tes': [2],
                      'chp': [3],
                      'hp_aw': [4],
                      'hp_ww': [5],
                      'eh': [6],
                      'bat': [7]}

        #  Test building dict  (mutate all esys, except heat pumps)
        b_dict = {'boi': 0,
                  'chp': 1,
                  'hp_aw': 1,
                  'hp_ww': 0,
                  'eh': 1,
                  'tes': 0,
                  'pv': 1,
                  'bat': 1}

        ind = {n: b_dict, 'lhn': []}

        pv_min = 0.5
        dict_max_pv_area = {1001: 50}

        list_options = ['hp_aw_eh_boi']
        list_opt_prob = [1]

        mutateesys.mut_esys_config_single_build(ind, n, dict_restr, pv_min,
                                                dict_max_pv_area,
                                                list_options=list_options,
                                                list_opt_prob=list_opt_prob,
                                                list_lhn_opt=None,
                                                list_lhn_prob=None)

        assert ind[n]['boi'] == 1
        assert ind[n]['tes'] == 2
        assert ind[n]['chp'] == 0
        assert ind[n]['hp_aw'] == 4
        assert ind[n]['hp_ww'] == 0
        assert ind[n]['eh'] == 6
        assert ind[n]['bat'] == 1
        assert ind[n]['pv'] == 1

    def test_mut_esys_config_single_build10(self):
        n = 1001

        dict_restr = {'boi': [1],
                      'tes': [2],
                      'chp': [3],
                      'hp_aw': [4],
                      'hp_ww': [5],
                      'eh': [6],
                      'bat': [7]}

        #  Test building dict  (mutate all esys, except heat pumps)
        b_dict = {'boi': 0,
                  'chp': 1,
                  'hp_aw': 1,
                  'hp_ww': 0,
                  'eh': 1,
                  'tes': 0,
                  'pv': 1,
                  'bat': 1}

        ind = {n: b_dict, 'lhn': []}

        pv_min = 0.5
        dict_max_pv_area = {1001: 50}

        list_options = ['hp_ww_eh_boi']
        list_opt_prob = [1]

        mutateesys.mut_esys_config_single_build(ind, n, dict_restr, pv_min,
                                                dict_max_pv_area,
                                                list_options=list_options,
                                                list_opt_prob=list_opt_prob,
                                                list_lhn_opt=None,
                                                list_lhn_prob=None)

        assert ind[n]['boi'] == 1
        assert ind[n]['tes'] == 2
        assert ind[n]['chp'] == 0
        assert ind[n]['hp_aw'] == 0
        assert ind[n]['hp_ww'] == 5
        assert ind[n]['eh'] == 6
        assert ind[n]['bat'] == 1
        assert ind[n]['pv'] == 1

    def test_mut_esys_config_single_build10(self):
        n = 1001

        dict_restr = {'boi': [1],
                      'tes': [2],
                      'chp': [3],
                      'hp_aw': [4],
                      'hp_ww': [5],
                      'eh': [6],
                      'bat': [7]}

        #  Test building dict  (mutate all esys, except heat pumps)
        b_dict = {'boi': 1,
                  'chp': 1,
                  'hp_aw': 0,
                  'hp_ww': 0,
                  'eh': 0,
                  'tes': 2,
                  'pv': 1,
                  'bat': 0}

        ind = {n: b_dict, 'lhn': []}

        pv_min = 0.5
        dict_max_pv_area = {1001: 50}

        list_options = ['bat']
        list_opt_prob = [1]

        mutateesys.mut_esys_config_single_build(ind, n, dict_restr, pv_min,
                                                dict_max_pv_area,
                                                list_options=list_options,
                                                list_opt_prob=list_opt_prob,
                                                list_lhn_opt=None,
                                                list_lhn_prob=None)

        assert ind[n]['boi'] == 1
        assert ind[n]['tes'] == 2
        assert ind[n]['chp'] == 1
        assert ind[n]['hp_aw'] == 0
        assert ind[n]['hp_ww'] == 0
        assert ind[n]['eh'] == 0
        assert ind[n]['bat'] == 7
        assert ind[n]['pv'] == 1

    def test_mut_esys_config_single_build11(self):
        n = 1001

        dict_restr = {'boi': [1],
                      'tes': [2],
                      'chp': [3],
                      'hp_aw': [4],
                      'hp_ww': [5],
                      'eh': [6],
                      'bat': [7]}

        #  Test building dict  (mutate all esys, except heat pumps)
        b_dict = {'boi': 1,
                  'chp': 1,
                  'hp_aw': 0,
                  'hp_ww': 0,
                  'eh': 0,
                  'tes': 2,
                  'pv': 0,
                  'bat': 0}

        ind = {n: b_dict, 'lhn': []}

        pv_min = 5
        dict_max_pv_area = {1001: 50}

        list_options = ['pv']
        list_opt_prob = [1]

        mutateesys.mut_esys_config_single_build(ind, n, dict_restr, pv_min,
                                                dict_max_pv_area,
                                                list_options=list_options,
                                                list_opt_prob=list_opt_prob,
                                                list_lhn_opt=None,
                                                list_lhn_prob=None)

        assert ind[n]['boi'] == 1
        assert ind[n]['tes'] == 2
        assert ind[n]['chp'] == 1
        assert ind[n]['hp_aw'] == 0
        assert ind[n]['hp_ww'] == 0
        assert ind[n]['eh'] == 0
        assert ind[n]['bat'] == 0
        assert ind[n]['pv'] > 0

    def test_mut_esys_config_single_build12(self):
        n = 1001

        dict_restr = {'boi': [1],
                      'tes': [2],
                      'chp': [3],
                      'hp_aw': [4],
                      'hp_ww': [5],
                      'eh': [6],
                      'bat': [7]}

        #  Test building dict  (mutate all esys, except heat pumps)
        b_dict = {'boi': 1,
                  'chp': 1,
                  'hp_aw': 1,
                  'hp_ww': 1,
                  'eh': 1,
                  'tes': 2,
                  'pv': 5,
                  'bat': 6}

        ind = {n: b_dict, 'lhn': []}

        pv_min = 0.5
        dict_max_pv_area = {1001: 50}

        list_options = ['no_th_supply']
        list_opt_prob = [1]

        mutateesys.mut_esys_config_single_build(ind, n, dict_restr, pv_min,
                                                dict_max_pv_area,
                                                list_options=list_options,
                                                list_opt_prob=list_opt_prob,
                                                list_lhn_opt=None,
                                                list_lhn_prob=None)

        assert ind[n]['boi'] == 0
        assert ind[n]['tes'] == 0
        assert ind[n]['chp'] == 0
        assert ind[n]['hp_aw'] == 0
        assert ind[n]['hp_ww'] == 0
        assert ind[n]['eh'] == 0
        assert ind[n]['bat'] == 6
        assert ind[n]['pv'] == 5
