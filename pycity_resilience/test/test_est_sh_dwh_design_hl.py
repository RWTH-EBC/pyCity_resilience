#!/usr/bin/env python
# coding=utf-8
"""

"""
from __future__ import division

import pycity_resilience.ga.preprocess.est_sh_dhw_design_heat_load as est


class TestEstimatorDesignHeatLoad():
    def test_est_sh_dhw_design_hl(self):

        nfa = 1000

        hl = est.est_sh_dhw_design_hl(nfa=nfa, build_standard='old')

        assert abs(hl - 150 * 1000) <= 0.001

        hl = est.est_sh_dhw_design_hl(nfa=nfa, build_standard='average')

        assert abs(hl - 100 * 1000) <= 0.001

        hl = est.est_sh_dhw_design_hl(nfa=nfa, build_standard='modern')

        assert abs(hl - 50 * 1000) <= 0.001
