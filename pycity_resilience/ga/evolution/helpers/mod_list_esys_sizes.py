#!/usr/bin/env python
# coding=utf-8
"""

"""
from __future__ import division

import warnings
import copy


def get_list_values_larger_than_ref(list_val, ref_val):
    """
    Returns list of values in list_val, which are larger than ref_val

    Parameters
    ----------
    list_val : list (of floats)
        Value list
    ref_val : float
        Reference value, which defines lower bound for search

    Returns
    -------
    list_larger : list (of floats)
        List holding all values of list_val, which are larger than or equal to
        ref_value
    """

    list_larger = copy.copy(list_val)

    for val in list_val:
        if val < ref_val:
            list_larger.remove(val)

    if list_larger == []:
        msg = 'list_larger is empty list. Thus, going to use largest values' \
              ' of original list list_val.'
        warnings.warn(msg)
        list_larger.append(max(list_val))

    return list_larger


def get_list_values_smaller_than_ref(list_val, ref_val):
    """
    Returns list of values in list_val, which are smaller than ref_val

    Parameters
    ----------
    list_val : list (of floats)
        Value list
    ref_val : float
        Reference value, which defines upper bound for search

    Returns
    -------
    list_smaller : list (of floats)
        List holding all values of list_val, which are smaller than or equal to
        ref_value
    """

    list_smaller = copy.copy(list_val)

    for val in list_val:
        if val > ref_val:
            list_smaller.remove(val)

    if list_smaller == []:
        msg = 'list_smaller is empty list. Thus, going to use smallest ' \
              'values of original list list_val.'
        warnings.warn(msg)
        list_smaller.append(min(list_val))

    return list_smaller


if __name__ == '__main__':
    list_input = [1, 2, 3, 4, 5, 6, 7, 8]
    ref_val = 2.5

    list_larger = get_list_values_larger_than_ref(list_val=list_input,
                                                  ref_val=ref_val)

    print('list_larger: ', list_larger)
    assert list_larger == [3, 4, 5, 6, 7, 8]

    ref_val = 6.3

    list_smaller = get_list_values_smaller_than_ref(list_val=list_input,
                                                    ref_val=ref_val)

    print('list_smaller: ', list_smaller)
    assert list_smaller == [1, 2, 3, 4, 5, 6]
