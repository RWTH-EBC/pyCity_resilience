#!/usr/bin/env python
# coding=utf-8
"""

"""
from __future__ import division

import os
import pickle
import copy
import numpy as np
import matplotlib.pylab as plt

import pycity_calc.cities.scripts.energy_network_generator as enetgen
import pycity_calc.cities.scripts.energy_sys_generator as esysgen
import pycity_calc.environments.germanmarket as gmarket
import pycity_calc.simulation.energy_balance.city_eb_calc as citeb
import pycity_calc.economic.annuity_calculation as annu
import pycity_calc.economic.city_economic_calc as citecon


def do_wm_comp(city, dhw_scale=True, eeg_pv_limit=False):
    #  Generate german market instance (if not already included in environment)
    ger_market = gmarket.GermanMarket()

    #  Add GermanMarket object instance to city
    city.environment.prices = ger_market

    #  Scenario 1: Add CHP dim. with single LHN
    #  #####################################################################

    city_scen_1 = copy.deepcopy(city)

    #  Connect all building nodes to local heating network
    dict_e_net_data = {1: {'type': 'heating',
                           'method': 2,
                           'nodelist': [1001, 1002, 1003, 1004, 1005, 1006,
                                        1007]}}

    #  Add energy networks to city
    enetgen.add_energy_networks_to_city(city=city_scen_1,
                                        dict_data=dict_e_net_data)

    #  Generate one feeder with CHP, boiler and TES
    list_esys = [(1005, 1, 1)]

    #  Generate energy systems
    esysgen.gen_esys_for_city(city=city_scen_1,
                              list_data=list_esys,
                              dhw_scale=dhw_scale)

    #  Scenario 2: Add decentral CHPs
    #  #####################################################################

    city_scen_2 = copy.deepcopy(city)

    #  Generate one feeder with CHP, boiler and TES
    list_esys = [(1001, 1, 1),
                 (1002, 1, 1),
                 (1003, 1, 1),
                 (1004, 1, 1),
                 (1005, 1, 1),
                 (1006, 1, 1),
                 (1007, 1, 1)]

    #  Generate energy systems
    esysgen.gen_esys_for_city(city=city_scen_2,
                              list_data=list_esys,
                              dhw_scale=dhw_scale)

    #  Scenario 3: Boilers, only
    #  #####################################################################

    city_scen_3 = copy.deepcopy(city)

    #  Generate one feeder with CHP, boiler and TES
    list_esys = [(1001, 0, 1),
                 (1002, 0, 1),
                 (1003, 0, 1),
                 (1004, 0, 1),
                 (1005, 0, 1),
                 (1006, 0, 1),
                 (1007, 0, 1)]

    #  Generate energy systems
    esysgen.gen_esys_for_city(city=city_scen_3,
                              list_data=list_esys,
                              dhw_scale=dhw_scale)

    #  Scenario 4: Boilers and TES, only
    #  #####################################################################

    city_scen_4 = copy.deepcopy(city)

    #  Generate one feeder with CHP, boiler and TES
    list_esys = [(1001, 0, 2),
                 (1002, 0, 2),
                 (1003, 0, 2),
                 (1004, 0, 2),
                 (1005, 0, 2),
                 (1006, 0, 2),
                 (1007, 0, 2)]

    #  Generate energy systems
    esysgen.gen_esys_for_city(city=city_scen_4,
                              list_data=list_esys,
                              dhw_scale=dhw_scale)

    #  Scenario 5: Air/water heat pumps
    #  #####################################################################

    city_scen_5 = copy.deepcopy(city)

    #  Generate one feeder with CHP, boiler and TES
    list_esys = [(1001, 2, 1),
                 (1002, 2, 1),
                 (1003, 2, 1),
                 (1004, 2, 1),
                 (1005, 2, 1),
                 (1006, 2, 1),
                 (1007, 2, 1)]

    #  Generate energy systems
    esysgen.gen_esys_for_city(city=city_scen_5,
                              list_data=list_esys,
                              dhw_scale=dhw_scale)

    city_scen_5.nodes[1006]['entity'].bes.electricalHeater.qNominal *= 5

    #  Scenario 6: Air/water heat pumps
    #  #####################################################################

    city_scen_6 = copy.deepcopy(city)

    #  Generate one feeder with CHP, boiler and TES
    list_esys = [(1001, 2, 2),
                 (1002, 2, 2),
                 (1003, 2, 2),
                 (1004, 2, 2),
                 (1005, 2, 2),
                 (1006, 2, 2),
                 (1007, 2, 2)]

    #  Generate energy systems
    esysgen.gen_esys_for_city(city=city_scen_6,
                              list_data=list_esys,
                              dhw_scale=dhw_scale)

    city_scen_6.nodes[1006]['entity'].bes.electricalHeater.qNominal *= 5

    #  Scenario 7: Boilers with small PV
    #  #####################################################################

    city_scen_7 = copy.deepcopy(city)

    #  Generate one feeder with CHP, boiler and TES
    list_esys = [(1001, 0, 1),
                 (1002, 0, 1),
                 (1003, 0, 1),
                 (1004, 0, 1),
                 (1005, 0, 1),
                 (1006, 0, 1),
                 (1007, 0, 1),
                 (1001, 3, 30),
                 (1002, 3, 30),
                 (1003, 3, 30),
                 (1004, 3, 30),
                 (1005, 3, 30),
                 (1006, 3, 30),
                 (1007, 3, 30)
                 ]

    #  Generate energy systems
    esysgen.gen_esys_for_city(city=city_scen_7,
                              list_data=list_esys,
                              dhw_scale=dhw_scale)

    #  Scenario 8: Boilers with medium PV
    #  #####################################################################

    city_scen_8 = copy.deepcopy(city)

    #  Generate one feeder with CHP, boiler and TES
    list_esys = [(1001, 0, 1),
                 (1002, 0, 1),
                 (1003, 0, 1),
                 (1004, 0, 1),
                 (1005, 0, 1),
                 (1006, 0, 1),
                 (1007, 0, 1),
                 (1001, 3, 60),
                 (1002, 3, 60),
                 (1003, 3, 60),
                 (1004, 3, 60),
                 (1005, 3, 60),
                 (1006, 3, 60),
                 (1007, 3, 60)
                 ]

    #  Generate energy systems
    esysgen.gen_esys_for_city(city=city_scen_8,
                              list_data=list_esys,
                              dhw_scale=dhw_scale)

    #  Scenario 9: Boilers with large PV
    #  #####################################################################

    city_scen_9 = copy.deepcopy(city)

    #  Generate one feeder with CHP, boiler and TES
    list_esys = [(1001, 0, 1),
                 (1002, 0, 1),
                 (1003, 0, 1),
                 (1004, 0, 1),
                 (1005, 0, 1),
                 (1006, 0, 1),
                 (1007, 0, 1),
                 (1001, 3, 80),
                 (1002, 3, 80),
                 (1003, 3, 80),
                 (1004, 3, 80),
                 (1005, 3, 80),
                 (1006, 3, 80),
                 (1007, 3, 80)
                 ]

    #  Generate energy systems
    esysgen.gen_esys_for_city(city=city_scen_9,
                              list_data=list_esys,
                              dhw_scale=dhw_scale)

    #  Scenario 10: Boilers with PV (over 10 kW peak)
    #  #####################################################################

    city_scen_10 = copy.deepcopy(city)

    #  Generate one feeder with CHP, boiler and TES
    list_esys = [(1001, 0, 1),
                 (1002, 0, 1),
                 (1003, 0, 1),
                 (1004, 0, 1),
                 (1005, 0, 1),
                 (1006, 0, 1),
                 (1007, 0, 1),
                 (1001, 3, 100),
                 (1002, 3, 100),
                 (1003, 3, 100),
                 (1004, 3, 100),
                 (1005, 3, 100),
                 (1006, 3, 100),
                 (1007, 3, 100)
                 ]

    #  Generate energy systems
    esysgen.gen_esys_for_city(city=city_scen_10,
                              list_data=list_esys,
                              dhw_scale=dhw_scale)

    #  Scenario 11: CHP with PV
    #  #####################################################################

    city_scen_11 = copy.deepcopy(city)

    #  Connect all building nodes to local heating network
    dict_e_net_data = {1: {'type': 'heating',
                           'method': 2,
                           'nodelist': [1001, 1002, 1003, 1004, 1005, 1006,
                                        1007]}}

    #  Add energy networks to city
    enetgen.add_energy_networks_to_city(city=city_scen_11,
                                        dict_data=dict_e_net_data)

    #  Generate one feeder with CHP, boiler and TES (plus PV)
    list_esys = [(1005, 1, 1),
                 (1001, 3, 60),
                 (1002, 3, 60),
                 (1003, 3, 60),
                 (1004, 3, 60),
                 (1005, 3, 60),
                 (1006, 3, 60),
                 (1007, 3, 60)
                 ]

    #  Generate energy systems
    esysgen.gen_esys_for_city(city=city_scen_11,
                              list_data=list_esys,
                              dhw_scale=dhw_scale)

    #  Scenario 12: CHP with PV
    #  #####################################################################

    city_scen_12 = copy.deepcopy(city)

    #  Connect all building nodes to local heating network
    dict_e_net_data = {1: {'type': 'heating',
                           'method': 2,
                           'nodelist': [1001, 1002, 1003, 1004, 1005, 1006,
                                        1007]}}

    #  Add energy networks to city
    enetgen.add_energy_networks_to_city(city=city_scen_12,
                                        dict_data=dict_e_net_data)

    #  Generate one feeder with CHP, boiler and TES (plus PV)
    list_esys = [(1005, 1, 1),
                 (1001, 3, 80),
                 (1002, 3, 80),
                 (1003, 3, 80),
                 (1004, 3, 80),
                 (1005, 3, 80),
                 (1006, 3, 80),
                 (1007, 3, 80)
                 ]

    #  Generate energy systems
    esysgen.gen_esys_for_city(city=city_scen_12,
                              list_data=list_esys,
                              dhw_scale=dhw_scale)

    #  Scenario 13: Boilers with PV (over 10 kW peak)
    #  #####################################################################

    city_scen_13 = copy.deepcopy(city)

    #  Connect all building nodes to local heating network
    dict_e_net_data = {1: {'type': 'heating',
                           'method': 2,
                           'nodelist': [1001, 1002, 1003, 1004, 1005, 1006,
                                        1007]}}

    #  Add energy networks to city
    enetgen.add_energy_networks_to_city(city=city_scen_13,
                                        dict_data=dict_e_net_data)

    #  Generate one feeder with CHP, boiler and TES (plus PV)
    list_esys = [(1005, 1, 1),
                 (1001, 3, 100),
                 (1002, 3, 100),
                 (1003, 3, 100),
                 (1004, 3, 100),
                 (1005, 3, 100),
                 (1006, 3, 100),
                 (1007, 3, 100)
                 ]

    #  Generate energy systems
    esysgen.gen_esys_for_city(city=city_scen_13,
                              list_data=list_esys,
                              dhw_scale=dhw_scale)

    #  #####################################################################
    #  Generate object instances
    #  #####################################################################

    #  Generate annuity object instance
    annuity_obj1 = annu.EconomicCalculation()
    annuity_obj2 = annu.EconomicCalculation()
    annuity_obj3 = annu.EconomicCalculation()
    annuity_obj4 = annu.EconomicCalculation()
    annuity_obj5 = annu.EconomicCalculation()
    annuity_obj6 = annu.EconomicCalculation()
    annuity_obj7 = annu.EconomicCalculation()
    annuity_obj8 = annu.EconomicCalculation()
    annuity_obj9 = annu.EconomicCalculation()
    annuity_obj10 = annu.EconomicCalculation()
    annuity_obj11 = annu.EconomicCalculation()
    annuity_obj12 = annu.EconomicCalculation()
    annuity_obj13 = annu.EconomicCalculation()

    #  Generate energy balance object for city
    energy_balance1 = citeb.CityEBCalculator(city=city_scen_1)
    energy_balance2 = citeb.CityEBCalculator(city=city_scen_2)
    energy_balance3 = citeb.CityEBCalculator(city=city_scen_3)
    energy_balance4 = citeb.CityEBCalculator(city=city_scen_4)
    energy_balance5 = citeb.CityEBCalculator(city=city_scen_5)
    energy_balance6 = citeb.CityEBCalculator(city=city_scen_6)
    energy_balance7 = citeb.CityEBCalculator(city=city_scen_7)
    energy_balance8 = citeb.CityEBCalculator(city=city_scen_8)
    energy_balance9 = citeb.CityEBCalculator(city=city_scen_9)
    energy_balance10 = citeb.CityEBCalculator(city=city_scen_10)
    energy_balance11 = citeb.CityEBCalculator(city=city_scen_11)
    energy_balance12 = citeb.CityEBCalculator(city=city_scen_12)
    energy_balance13 = citeb.CityEBCalculator(city=city_scen_13)

    #  Generate city economic calculator instances
    city_eco_calc1 = citecon.CityAnnuityCalc(annuity_obj=annuity_obj1,
                                             energy_balance=energy_balance1)
    city_eco_calc2 = citecon.CityAnnuityCalc(annuity_obj=annuity_obj2,
                                             energy_balance=energy_balance2)
    city_eco_calc3 = citecon.CityAnnuityCalc(annuity_obj=annuity_obj3,
                                             energy_balance=energy_balance3)
    city_eco_calc4 = citecon.CityAnnuityCalc(annuity_obj=annuity_obj4,
                                             energy_balance=energy_balance4)
    city_eco_calc5 = citecon.CityAnnuityCalc(annuity_obj=annuity_obj5,
                                             energy_balance=energy_balance5)
    city_eco_calc6 = citecon.CityAnnuityCalc(annuity_obj=annuity_obj6,
                                             energy_balance=energy_balance6)
    city_eco_calc7 = citecon.CityAnnuityCalc(annuity_obj=annuity_obj7,
                                             energy_balance=energy_balance7)
    city_eco_calc8 = citecon.CityAnnuityCalc(annuity_obj=annuity_obj8,
                                             energy_balance=energy_balance8)
    city_eco_calc9 = citecon.CityAnnuityCalc(annuity_obj=annuity_obj9,
                                             energy_balance=energy_balance9)
    city_eco_calc10 = citecon.CityAnnuityCalc(annuity_obj=annuity_obj10,
                                              energy_balance=energy_balance10)
    city_eco_calc11 = citecon.CityAnnuityCalc(annuity_obj=annuity_obj11,
                                             energy_balance=energy_balance11)
    city_eco_calc12 = citecon.CityAnnuityCalc(annuity_obj=annuity_obj12,
                                              energy_balance=energy_balance12)
    city_eco_calc13 = citecon.CityAnnuityCalc(annuity_obj=annuity_obj13,
                                              energy_balance=energy_balance13)

    list_ann = []
    list_co2 = []

    #  Perform energy balance and annuity calculations for all scenarios
    (total_annuity_1, co2_1) = city_eco_calc1. \
        perform_overall_energy_balance_and_economic_calc(eeg_pv_limit=
                                                         eeg_pv_limit)
    list_ann.append(total_annuity_1)
    list_co2.append(co2_1)

    (total_annuity_2, co2_2) = city_eco_calc2. \
        perform_overall_energy_balance_and_economic_calc(eeg_pv_limit=
                                                         eeg_pv_limit)
    list_ann.append(total_annuity_2)
    list_co2.append(co2_2)

    (total_annuity_3, co2_3) = city_eco_calc3. \
        perform_overall_energy_balance_and_economic_calc(eeg_pv_limit=
                                                         eeg_pv_limit)
    list_ann.append(total_annuity_3)
    list_co2.append(co2_3)

    (total_annuity_4, co2_4) = city_eco_calc4. \
        perform_overall_energy_balance_and_economic_calc(eeg_pv_limit=
                                                         eeg_pv_limit)
    list_ann.append(total_annuity_4)
    list_co2.append(co2_4)

    (total_annuity_5, co2_5) = city_eco_calc5. \
        perform_overall_energy_balance_and_economic_calc(eeg_pv_limit=
                                                         eeg_pv_limit)
    list_ann.append(total_annuity_5)
    list_co2.append(co2_5)

    (total_annuity_6, co2_6) = city_eco_calc6. \
        perform_overall_energy_balance_and_economic_calc(eeg_pv_limit=
                                                         eeg_pv_limit)
    list_ann.append(total_annuity_6)
    list_co2.append(co2_6)

    (total_annuity_7, co2_7) = city_eco_calc7. \
        perform_overall_energy_balance_and_economic_calc(eeg_pv_limit=
                                                         eeg_pv_limit)
    list_ann.append(total_annuity_7)
    list_co2.append(co2_7)

    (total_annuity_8, co2_8) = city_eco_calc8. \
        perform_overall_energy_balance_and_economic_calc(eeg_pv_limit=
                                                         eeg_pv_limit)
    list_ann.append(total_annuity_8)
    list_co2.append(co2_8)

    (total_annuity_9, co2_9) = city_eco_calc9. \
        perform_overall_energy_balance_and_economic_calc(eeg_pv_limit=
                                                         eeg_pv_limit)
    list_ann.append(total_annuity_9)
    list_co2.append(co2_9)

    (total_annuity_10, co2_10) = city_eco_calc10. \
        perform_overall_energy_balance_and_economic_calc(eeg_pv_limit=
                                                         eeg_pv_limit)
    list_ann.append(total_annuity_10)
    list_co2.append(co2_10)

    (total_annuity_11, co2_11) = city_eco_calc11. \
        perform_overall_energy_balance_and_economic_calc(eeg_pv_limit=
                                                         eeg_pv_limit)
    list_ann.append(total_annuity_11)
    list_co2.append(co2_11)

    (total_annuity_12, co2_12) = city_eco_calc12. \
        perform_overall_energy_balance_and_economic_calc(eeg_pv_limit=
                                                         eeg_pv_limit)
    list_ann.append(total_annuity_12)
    list_co2.append(co2_12)

    (total_annuity_13, co2_13) = city_eco_calc13. \
        perform_overall_energy_balance_and_economic_calc(eeg_pv_limit=
                                                         eeg_pv_limit)
    list_ann.append(total_annuity_13)
    list_co2.append(co2_13)

    plt.plot([total_annuity_1], [co2_1], label='Scen. 1 (CHP/LHN)', marker='o')
    plt.plot([total_annuity_2], [co2_2], label='Scen. 2 (dec. CHP)',
             marker='o')
    plt.plot([total_annuity_3], [co2_3], label='Scen. 3 (BOI)', marker='o')
    plt.plot([total_annuity_4], [co2_4], label='Scen. 4 (BOI/TES)', marker='o')
    plt.plot([total_annuity_5], [co2_5], label='Scen. 5 (HP (aw))', marker='o')
    plt.plot([total_annuity_6], [co2_6], label='Scen. 6 (HP (ww))', marker='o')
    plt.plot([total_annuity_7], [co2_7], label='Scen. 7 (BOI/small PV)',
             marker='o')
    plt.plot([total_annuity_8], [co2_8], label='Scen. 8 (BOI/medium PV)',
             marker='o')
    plt.plot([total_annuity_9], [co2_9], label='Scen. 9 (BOI/large PV)',
             marker='o')
    plt.plot([total_annuity_10], [co2_10], label='Scen. 10 (BOI/PV>10 kWp)',
             marker='o')
    plt.plot([total_annuity_11], [co2_11],
             label='Scen. 11 (CHP/LHN/PV 60)',
             marker='*')
    plt.plot([total_annuity_12], [co2_12],
             label='Scen. 12 (CHP/LHN/PV 80)',
             marker='*')
    plt.plot([total_annuity_13], [co2_13], label='Scen. 13 (CHP/LHN/PV 100)',
             marker='*')
    plt.xlabel('Total annualized cost in Euro/a')
    plt.ylabel('Total CO2 emissions in kg/a')
    plt.legend()
    plt.tight_layout()
    plt.show()
    plt.close()

    hp_q_out = city_scen_5.nodes[1006]['entity'].bes.heatpump.totalQOutput
    hp_el_in = city_scen_5.nodes[1006]['entity'].bes.heatpump.array_el_power_in

    cop_array = np.zeros(len(hp_q_out))
    sum_not_zero = 0
    steps_not_zero = 0
    for i in range(len(cop_array)):
        if hp_el_in[i] > 0:
            cop_array[i] = hp_q_out[i] / hp_el_in[i]
            sum_not_zero += cop_array[i]
            steps_not_zero += 1

    cop_average = sum_not_zero / steps_not_zero
    print('COP average (AW): ', cop_average)

    fig = plt.figure()
    ax = fig.add_subplot(2, 1, 1)
    ax.plot(hp_q_out)
    ax.plot(hp_el_in)
    ax2 = fig.add_subplot(2, 1, 2)
    ax2.plot(cop_array)
    plt.show()
    plt.close()

    hp_q_out = city_scen_6.nodes[1006]['entity'].bes.heatpump.totalQOutput
    hp_el_in = city_scen_6.nodes[1006]['entity'].bes.heatpump.array_el_power_in

    cop_array = np.zeros(len(hp_q_out))
    sum_not_zero = 0
    steps_not_zero = 0
    for i in range(len(cop_array)):
        if hp_el_in[i] > 0:
            cop_array[i] = hp_q_out[i] / hp_el_in[i]
            sum_not_zero += cop_array[i]
            steps_not_zero += 1

    cop_average = sum_not_zero / steps_not_zero
    print('COP average (WW): ', cop_average)

    fig = plt.figure()
    ax = fig.add_subplot(2, 1, 1)
    ax.plot(hp_q_out)
    ax.plot(hp_el_in)
    ax2 = fig.add_subplot(2, 1, 2)
    ax2.plot(cop_array)
    plt.show()
    plt.close()


if __name__ == '__main__':
    #  Get workspace path
    #  #############################################################
    this_path = os.path.dirname(os.path.abspath(__file__))
    src_path = os.path.dirname(os.path.dirname(os.path.dirname(this_path)))
    path_workspace = os.path.join(src_path, 'workspace')
    #  #############################################################

    city_name = 'wm_res_east_7_w_street_sh_resc_wm.pkl'

    path_city = os.path.join(path_workspace,
                             'city_objects',
                             'no_esys',
                             city_name)

    city = pickle.load(open(path_city, mode='rb'))

    eeg_pv_limit = True

    do_wm_comp(city=city, eeg_pv_limit=eeg_pv_limit)
