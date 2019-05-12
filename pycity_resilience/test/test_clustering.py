#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

"""
from __future__ import division

import shapely.geometry.point as point

import pycity_resilience.ga.clustering.cluster as clust


class TestClustering():
    def test_kmeans_clustering(self):
        p1 = point.Point(0, 0)
        p2 = point.Point(1, 0)
        p3 = point.Point(12, 0)
        p4 = point.Point(15, 3)
        p5 = point.Point(10, 10)
        p6 = point.Point(20, 20)
        p7 = point.Point(24, 20)
        p8 = point.Point(0, 10)

        dict_pos = {1001: p1,
                    1002: p2,
                    1003: p3,
                    1004: p4,
                    1005: p5,
                    1006: p6,
                    1007: p7,
                    1008: p8}

        list_av_ids = [1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008]

        nb_clusters = 2

        dict_clusters = clust.kmeans_clustering(dict_pos=dict_pos,
                                                list_av_ids=list_av_ids,
                                                nb_clusters=nb_clusters)
