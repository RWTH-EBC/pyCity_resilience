#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

"""
from __future__ import division

import shapely.geometry.point as point

import pycity_resilience.ga.analyse.find_lhn as findlhn
import pycity_resilience.ga.analyse.analyse as analyse


class TestAnalysis():
    def test_has_lhn_connection(self):
        id = 1002

        ind = {1001: {}, 1002: {}, 1003: {}, 'lhn': [[1002, 1003]]}

        assert findlhn.has_lhn_connection(ind=ind, id=id) is True

        ind = {1001: {}, 1002: {}, 1003: {}, 'lhn': [[1003, 1004]]}

        assert findlhn.has_lhn_connection(ind=ind, id=id) is False

        ind = {1001: {}, 1002: {}, 1003: {}, 'lhn': []}

        assert findlhn.has_lhn_connection(ind=ind, id=id) is False

    def test_get_build_ids_ind(self):
        ind = {1001: {}, 1002: {}, 1003: {}, 'lhn': []}

        assert sorted(analyse.get_build_ids_ind(ind=ind)) == [1001, 1002, 1003]

    def test_get_all_lhn_ids(self):
        ind = {1001: {}, 1002: {}, 1003: {}, 'lhn': [[1002, 1003],
                                                     [1004, 1005],
                                                     [1010, 1011, 1012]]}

        list_lhn_ids = findlhn.get_all_lhn_ids(ind=ind)

        assert sorted(list_lhn_ids) == [1002, 1003, 1004, 1005, 1010, 1011,
                                        1012]

    def test_get_ids_sorted_by_dist(self):
        id = 1001

        p1 = point.Point(0, 0)
        p4 = point.Point(10, 0)
        p2 = point.Point(20, 0)
        p3 = point.Point(30, 0)
        p5 = point.Point(30, 10)

        dict_pos = {1001: p1, 1002: p2, 1003: p3, 1004: p4, 1005: p5}

        list_av = [1001, 1002, 1003, 1004, 1005]

        list_sorted = analyse. \
            get_ids_sorted_by_dist(id=id, dict_pos=dict_pos, list_av=list_av)

        assert list_sorted == [1004, 1002, 1003, 1005]

    def test_get_ids_sorted_by_dist2(self):
        id = 1001

        max_dist = 25

        p1 = point.Point(0, 0)
        p4 = point.Point(10, 0)
        p2 = point.Point(20, 0)
        p3 = point.Point(30, 0)
        p5 = point.Point(30, 10)

        dict_pos = {1001: p1, 1002: p2, 1003: p3, 1004: p4, 1005: p5}

        list_av = [1001, 1002, 1003, 1004, 1005]

        list_sorted = analyse. \
            get_ids_sorted_by_dist(id=id, dict_pos=dict_pos, list_av=list_av,
                                   max_dist=max_dist)

        assert list_sorted == [1004, 1002]

    def test_get_ids_closest_dist_to_list_of_build(self):
        list_ref = [1001, 1002, 1003]
        list_search = [1004, 1005, 1006]

        p1 = point.Point(0, 0)
        p2 = point.Point(10, 0)
        p3 = point.Point(0, 10)
        p4 = point.Point(0, 30)
        p5 = point.Point(40, 0)
        p6 = point.Point(0, -10)

        dict_pos = {1001: p1, 1002: p2, 1003: p3,
                    1004: p4, 1005: p5, 1006: p6}

        dict_dist = analyse. \
            get_ids_closest_dist_to_list_of_build(list_ref=list_ref,
                                                  list_search=list_search,
                                                  dict_pos=dict_pos)

        assert dict_dist == {1004: 20, 1005: 30, 1006: 10}

    def test_get_list_ids_sorted_by_dist_to_ref_list(self):
        list_ref = [1001, 1002, 1003]
        list_search = [1004, 1005, 1006]

        p1 = point.Point(0, 0)
        p2 = point.Point(10, 0)
        p3 = point.Point(0, 10)
        p4 = point.Point(0, 30)
        p5 = point.Point(40, 0)
        p6 = point.Point(0, -10)

        dict_pos = {1001: p1, 1002: p2, 1003: p3,
                    1004: p4, 1005: p5, 1006: p6}

        list_sorted = analyse. \
            get_list_ids_sorted_by_dist_to_ref_list(list_ref=list_ref,
                                                    list_search=list_search,
                                                    dict_pos=dict_pos)

        assert list_sorted == [(1006, 10), (1004, 20), (1005, 30)]

    def test_get_list_ids_sorted_by_dist_to_ref_list2(self):
        list_ref = [1001, 1002, 1003]
        list_search = [1004, 1005, 1006]

        p1 = point.Point(0, 0)
        p2 = point.Point(10, 0)
        p3 = point.Point(0, 10)
        p4 = point.Point(0, 30)
        p5 = point.Point(40, 0)
        p6 = point.Point(0, -10)

        dict_pos = {1001: p1, 1002: p2, 1003: p3,
                    1004: p4, 1005: p5, 1006: p6}

        max_dist = 25

        list_sorted = analyse. \
            get_list_ids_sorted_by_dist_to_ref_list(list_ref=list_ref,
                                                    list_search=list_search,
                                                    dict_pos=dict_pos,
                                                    max_dist=max_dist)

        assert list_sorted == [(1006, 10), (1004, 20)]

    def test_get_build_ids_without_th_supply(self):
        dict_b1 = {'bat': 5000,  # in Joule
                   'boi': 10000,  # in Watt
                   'chp': 1000,
                   'eh': 0,
                   'hp_aw': 0,
                   'hp_ww': 0,
                   'pv': 0,  # in m2
                   'tes': 300}  # in kg

        dict_b2 = {'bat': 0,  # in Joule
                   'boi': 0,  # in Watt
                   'chp': 0,
                   'eh': 0,
                   'hp_aw': 0,
                   'hp_ww': 0,
                   'pv': 0,  # in m2
                   'tes': 0}  # in kg

        #  With HP
        dict_b3 = {'bat': 0,  # in Joule
                   'boi': 0,  # in Watt
                   'chp': 0,
                   'eh': 20000,
                   'hp_aw': 10000,
                   'hp_ww': 0,
                   'pv': 50,  # in m2
                   'tes': 500}  # in kg

        ind = {1001: dict_b1, 1002: dict_b2, 1003: dict_b3,
               'lhn': [[1001, 1002]]}

        list_no_th_sup = analyse.get_build_ids_without_th_supply(ind=ind)

        assert list_no_th_sup == [1002]
