#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to check different functions to calculate "decision" based on different
given gaussian distributions (mean and std)

Used for maximization of objectives
"""
from __future__ import division

import math
import numpy as np
import matplotlib.pyplot as plt


def obj_fkt(mean, std):
    """
    Function to estimate objective function value based on gaussian
    distribution.

    Parameters
    ----------
    mean : float
        Mean value of distribution
    std : float
        Standard deviation of distribution

    Returns
    -------
    obj_val : float
        Objective function output value (larger is better)
    """

    return mean / (std ** (10 / 25))


def check_1(factor=1):
    nb_samples = 10000

    mean_a = 10 * factor
    std_a = 1 * factor

    mean_b = 20 * factor
    std_b = 1 * factor

    #  Calculate distributions
    array_a = np.random.normal(loc=mean_a, scale=std_a, size=nb_samples)
    array_b = np.random.normal(loc=mean_b, scale=std_b, size=nb_samples)

    #  Calculate single objective value
    obj_val_a = obj_fkt(mean=mean_a, std=std_a)
    obj_val_b = obj_fkt(mean=mean_b, std=std_b)

    if obj_val_a > obj_val_b:
        chosen = 'a'
    elif obj_val_a == obj_val_b:
        chosen = 'Indifferent'
    elif obj_val_a < obj_val_b:
        chosen = 'b'

    title = 'Should be b (chose ' + str(chosen) + ')'

    plt.hist(array_a, label='a')
    plt.hist(array_b, label='b')
    plt.legend()
    plt.title(title)
    plt.tight_layout()
    plt.show()
    plt.close()


def check_2(factor=1):
    nb_samples = 10000

    mean_a = 10 * factor
    std_a = 2 * factor

    mean_b = 10 * factor
    std_b = 1 * factor

    #  Calculate distributions
    array_a = np.random.normal(loc=mean_a, scale=std_a, size=nb_samples)
    array_b = np.random.normal(loc=mean_b, scale=std_b, size=nb_samples)

    #  Calculate single objective value
    obj_val_a = obj_fkt(mean=mean_a, std=std_a)
    obj_val_b = obj_fkt(mean=mean_b, std=std_b)

    if obj_val_a > obj_val_b:
        chosen = 'a'
    elif obj_val_a == obj_val_b:
        chosen = 'Indifferent'
    elif obj_val_a < obj_val_b:
        chosen = 'b'

    title = 'Should be b (chose ' + str(chosen) + ')'

    plt.hist(array_a, label='a')
    plt.hist(array_b, label='b')
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    plt.show()
    plt.close()


def check_3(factor=1):
    nb_samples = 10000

    mean_a = 12 * factor
    std_a = 4 * factor

    mean_b = 10 * factor
    std_b = 1 * factor

    #  Calculate distributions
    array_a = np.random.normal(loc=mean_a, scale=std_a, size=nb_samples)
    array_b = np.random.normal(loc=mean_b, scale=std_b, size=nb_samples)

    #  Calculate single objective value
    obj_val_a = obj_fkt(mean=mean_a, std=std_a)
    obj_val_b = obj_fkt(mean=mean_b, std=std_b)

    if obj_val_a > obj_val_b:
        chosen = 'a'
    elif obj_val_a == obj_val_b:
        chosen = 'Indifferent'
    elif obj_val_a < obj_val_b:
        chosen = 'b'

    title = 'Should be b (chose ' + str(chosen) + ')'

    plt.hist(array_a, label='a')
    plt.hist(array_b, label='b')
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    plt.show()
    plt.close()


def check_4(factor=1):
    nb_samples = 10000

    mean_a = 12 * factor
    std_a = 4 * factor

    mean_b = 7 * factor
    std_b = 1 * factor

    #  Calculate distributions
    array_a = np.random.normal(loc=mean_a, scale=std_a, size=nb_samples)
    array_b = np.random.normal(loc=mean_b, scale=std_b, size=nb_samples)

    #  Calculate single objective value
    obj_val_a = obj_fkt(mean=mean_a, std=std_a)
    obj_val_b = obj_fkt(mean=mean_b, std=std_b)

    if obj_val_a > obj_val_b:
        chosen = 'a'
    elif obj_val_a == obj_val_b:
        chosen = 'Indifferent'
    elif obj_val_a < obj_val_b:
        chosen = 'b'

    title = 'Should be b (chose ' + str(chosen) + ')'

    plt.hist(array_a, label='a')
    plt.hist(array_b, label='b')
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    plt.show()
    plt.close()


def check_5(factor=1):
    nb_samples = 10000

    mean_a = 10 * factor
    std_a = 1 * factor

    mean_b = 38 * factor
    std_b = 4 * factor

    #  Calculate distributions
    array_a = np.random.normal(loc=mean_a, scale=std_a, size=nb_samples)
    array_b = np.random.normal(loc=mean_b, scale=std_b, size=nb_samples)

    #  Calculate single objective value
    obj_val_a = obj_fkt(mean=mean_a, std=std_a)
    obj_val_b = obj_fkt(mean=mean_b, std=std_b)

    if obj_val_a > obj_val_b:
        chosen = 'a'
    elif obj_val_a == obj_val_b:
        chosen = 'Indifferent'
    elif obj_val_a < obj_val_b:
        chosen = 'b'

    title = 'Should be b (chose ' + str(chosen) + ')'

    plt.hist(array_a, label='a')
    plt.hist(array_b, label='b')
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    plt.show()
    plt.close()


def check_6(factor=1):
    nb_samples = 10000

    mean_a = 10 * factor
    std_a = 1 * factor

    mean_b = 38 * factor
    std_b = 7 * factor

    #  Calculate distributions
    array_a = np.random.normal(loc=mean_a, scale=std_a, size=nb_samples)
    array_b = np.random.normal(loc=mean_b, scale=std_b, size=nb_samples)

    #  Calculate single objective value
    obj_val_a = obj_fkt(mean=mean_a, std=std_a)
    obj_val_b = obj_fkt(mean=mean_b, std=std_b)

    if obj_val_a > obj_val_b:
        chosen = 'a'
    elif obj_val_a == obj_val_b:
        chosen = 'Indifferent'
    elif obj_val_a < obj_val_b:
        chosen = 'b'

    title = 'Should be b (chose ' + str(chosen) + ')'

    plt.hist(array_a, label='a', bins='auto')
    plt.hist(array_b, label='b', bins='auto')
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    plt.show()
    plt.close()


def check_7(factor=1):
    nb_samples = 10000

    mean_a = 10 * factor
    std_a = 1 * factor

    mean_b = 23 * factor
    std_b = 4 * factor

    #  Calculate distributions
    array_a = np.random.normal(loc=mean_a, scale=std_a, size=nb_samples)
    array_b = np.random.normal(loc=mean_b, scale=std_b, size=nb_samples)

    #  Calculate single objective value
    obj_val_a = obj_fkt(mean=mean_a, std=std_a)
    obj_val_b = obj_fkt(mean=mean_b, std=std_b)

    if obj_val_a > obj_val_b:
        chosen = 'a'
    elif obj_val_a == obj_val_b:
        chosen = 'Indifferent'
    elif obj_val_a < obj_val_b:
        chosen = 'b'

    title = 'Should be b (chose ' + str(chosen) + ')'

    plt.hist(array_a, label='a', bins='auto')
    plt.hist(array_b, label='b', bins='auto')
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    plt.show()
    plt.close()


def check_8(factor=1):
    nb_samples = 10000

    mean_a = 10 * factor
    std_a = 1 * factor

    mean_b = 18 * factor
    std_b = 4 * factor

    #  Calculate distributions
    array_a = np.random.normal(loc=mean_a, scale=std_a, size=nb_samples)
    array_b = np.random.normal(loc=mean_b, scale=std_b, size=nb_samples)

    #  Calculate single objective value
    obj_val_a = obj_fkt(mean=mean_a, std=std_a)
    obj_val_b = obj_fkt(mean=mean_b, std=std_b)

    if obj_val_a > obj_val_b:
        chosen = 'a'
    elif obj_val_a == obj_val_b:
        chosen = 'Indifferent'
    elif obj_val_a < obj_val_b:
        chosen = 'b'

    title = 'Should be b (chose ' + str(chosen) + ')'

    plt.hist(array_a, label='a', bins='auto', alpha=0.7)
    plt.hist(array_b, label='b', bins='auto', alpha=0.7)
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    plt.show()
    plt.close()


if __name__ == '__main__':
    factor = 1

    check_1(factor=factor)
    check_2(factor=factor)
    check_3(factor=factor)
    check_4(factor=factor)
    check_5(factor=factor)
    check_6(factor=factor)
    check_7(factor=factor)
    check_8(factor=factor)
