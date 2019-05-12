#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

"""
from __future__ import division

import copy
import warnings
import numpy as np
import shapely.geometry.point as point

from sklearn.cluster import MeanShift, estimate_bandwidth
from sklearn.datasets.samples_generator import make_blobs

import pycity_calc.toolbox.clustering.experiments.kmeans_city_clustering \
    as kmean
import pycity_calc.toolbox.clustering.experiments.kmeans_lloyd as kmeanslloyd


def get_id_of_pos(dict_pos, pos):
    """
    Returns id to given position

    Parameters
    ----------
    dict_pos : dict
        Dict holding building node ids as key and shapely geometry points as
        values
    pos : object
        Shapely geometry point object (2d)

    Returns
    -------
    id : int
        Id of key of dict_pos with position pos
    """

    id = None

    for key in dict_pos.keys():
        if dict_pos[key] == pos:
            id = key

    return id


def conv_point_to_ids(dict_pos, dict_clust_points):
    """
    Convert point dictionary to ind ids

    Parameters
    ----------
    dict_pos : dict
        Dict holding building node ids as keys and shapely point objects (2d)
        as values
    dict_clust_points : dict
        Dictionary holding cluster numbers (int) as keys and list of points
        as values

    Returns
    -------
    dict_ids : dict
        Dictionary holding cluster numbers (int) as keys and list of node
        ids as values
    """

    dict_ids = {}

    for key in dict_clust_points:
        list_points = dict_clust_points[key]
        list_nodes = []

        for i in range(len(list_points)):
            point = list_points[i]

            id = get_id_of_pos(dict_pos=dict_pos, pos=point)

            assert id is not None

            list_nodes.append(id)

        dict_ids[key] = list_nodes

    return dict_ids


def kmeans_clustering(dict_pos, list_av_ids, nb_clusters):
    """
    Perform kmeans clustering on ind dict

    Parameters
    ----------
    dict_pos : dict
        Dict holding building node ids as keys and shapely point objects (2d)
        as values
    list_av_ids : list
        List with available node ids for clustering
    nb_clusters : int
        Number of desired clusters

    Returns
    -------
    dict_clusters : dict
        Dictionary holding cluster numbers (int) as keys and list of node
        ids as values
    """

    #  Generate dummy array to extract
    x_y_array = np.zeros((len(list_av_ids), 2))

    #  Extract x/y coordinates
    for i in range(len(list_av_ids)):
        x_y_array[i][0] = dict_pos[list_av_ids[i]].x
        x_y_array[i][1] = dict_pos[list_av_ids[i]].y

    cluster_dict = None
    nb_tries = 0
    # Perform kmeans clustering
    while cluster_dict is None and nb_tries <= 10:
        mu, cluster_dict = kmeanslloyd.find_centers(x_y_array, nb_clusters)
        nb_tries += 1

    if cluster_dict is None:
        #  If kmeans could not finde solution, return None
        msg = 'Kmeans could not find a solution. Return None'
        warnings.warn(msg)
        return None

    #  Convert cluster array to points
    cluster_dict = kmean.conv_cluster_array_to_point(cluster_dict)

    #  Get point ids to positions
    dict_clusters = conv_point_to_ids(dict_pos=dict_pos,
                                      dict_clust_points=cluster_dict)

    used_cleanup = False
    #  Cleanup dict; Erase all lists with only a single node
    dict_clusters_copy = copy.deepcopy(dict_clusters)
    for key in dict_clusters.keys():
        if len(dict_clusters[key]) == 1:  # If only holds single node
            del dict_clusters_copy[key]
            used_cleanup = True
    #  Overwrite
    dict_clusters = dict_clusters_copy

    #  Solves #255: Check key has been deleted, shift keys back into order
    #  0, 1, 2, 3, ..., n
    if used_cleanup:
        dict_clusters_new = {}
        list_ids_sorted = sorted(list(dict_clusters.keys()))

        i = 0
        for key in list_ids_sorted:
            dict_clusters_new[i] = dict_clusters[key]
            i += 1
        #  Overwrite
        dict_clusters = dict_clusters_new

    return dict_clusters


def meanshift_clustering(dict_pos, list_av_ids):
    """
    Perform meanshift clustering (

    Parameters
    ----------
    dict_pos : dict
        Dict holding building node ids as keys and shapely point objects (2d)
        as values
    list_av_ids : list
        List with available node ids for clustering

    Returns
    -------
    dict_clusters : dict
        Dictionary holding cluster numbers (int) as keys and list of node
        ids as values
    """

    #  Generate numpy position array (init with zeros)
    xy_array = np.zeros((len(list_av_ids), 2))

    #  Extract building ndoe positions and add to X
    for i in range(len(list_av_ids)):
        id = list_av_ids[i]
        point = dict_pos[id]
        xy_array[i][0] = point.x
        xy_array[i][1] = point.y

    # The following bandwidth can be automatically detected using
    bandwidth = estimate_bandwidth(xy_array,
                                   # quantile=0.2,
                                   )

    ms = MeanShift(bandwidth=bandwidth, bin_seeding=True)

    ms.fit(xy_array)

    labels = ms.labels_
    cluster_centers = ms.cluster_centers_
    labels_unique = np.unique(labels)
    n_clusters_ = len(labels_unique)

    #  Sort copy of building node list according to labels list
    list_ids = copy.deepcopy(list_av_ids)
    labels, list_ids = zip(*sorted(zip(labels, list_ids)))

    #  Generate cluster_dict
    dict_clusters = {}
    for i in range(len(labels)):
        label = labels[i]
        node_id = list_ids[i]
        #  Append (or generate) list with cluster number as key
        dict_clusters.setdefault(label, []).append(node_id)

    #  Cleanup dict; Erase all lists with only a single node
    dict_clusters_copy = copy.deepcopy(dict_clusters)
    for key in dict_clusters.keys():
        if len(dict_clusters[key]) == 1:  # If only holds single node
            del dict_clusters_copy[key]
    #  Overwrite
    dict_clusters = dict_clusters_copy

    return dict_clusters

def main():
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

    nb_clusters = 3

    dict_clusters = kmeans_clustering(dict_pos=dict_pos,
                                      list_av_ids=list_av_ids,
                                      nb_clusters=nb_clusters)

    print('Results of kmeans clustering:')
    print(dict_clusters)
    print()
    for key in dict_clusters.keys():
        print('Key: ', key)
        print('Values: ', dict_clusters[key])
        print()
    print('###########################################################')

    dict_clusters = meanshift_clustering(dict_pos=dict_pos,
                                         list_av_ids=list_av_ids)

    print('Results of meanshift clustering:')
    print(dict_clusters)
    print()
    for key in dict_clusters.keys():
        print('Key: ', key)
        print('Values: ', dict_clusters[key])
        print()
    print('###########################################################')

if __name__ == '__main__':
    main()
