#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to add bes with all possible device types to all buildings, if not
already existent. Necessary to enable GA usage. All newly added devices are
saved on bes, but set to False (e.g. hasChp == False)
"""
from __future__ import division

import warnings

import pycity_base.classes.supply.BES as BES
import pycity_calc.energysystems.boiler as Boiler
import pycity_calc.energysystems.electricalHeater as EH
import pycity_calc.energysystems.heatPumpSimple as HP
import pycity_calc.energysystems.thermalEnergyStorage as TES
import pycity_calc.energysystems.chp as CHP
import pycity_calc.energysystems.battery as Battery
import pycity_base.classes.supply.PV as PV
import pycity_calc.toolbox.dimensioning.dim_functions as dimfunc
import pycity_calc.energysystems.Input.chp_asue_2015 as asue


def add_bes_to_city(city, add_init_boi=False, eta_boi=0.95, eta_pv=0.1275):
    """
    Add bes to every building in city, if not already existent on building.
    All possible types of energy systems are added. However, they can be
    deactivated before energy balance is called by setting corresponding
    hasEsys attributes on bes (such as bes.hasChp) to False.

    Per default, all newly added energy systems are set to False

    Parameters
    ----------
    city : object
        City object of pyCity_calc
    add_init_boi : bool, optional
        Defines, if boilers and tes should be added to all buildings as initial
        configuration (default: False).
        Required to pass EnergySupply when adding city to energy balance #29
    eta_boi : float, optional
        Initial boiler efficiency (default: 0.95)
    eta_pv : float, optional
        Efficiency of PV system (default: 0.1275)
    """

    assert eta_pv > 0
    assert eta_pv <= 1
    assert eta_boi > 0
    assert eta_boi <= 1

    for n in city.nodes():
        if 'node_type' in city.nodes[n]:
            if city.nodes[n]['node_type'] == 'building':
                if 'entity' in city.nodes[n]:
                    if city.nodes[n]['entity']._kind == 'building':

                        #  Define building pointer
                        build = city.nodes[n]['entity']

                        #  Check if building has BES
                        if build.hasBes is False:

                            #  Generate BES and add to building
                            bes = BES.BES(environment=city.environment)

                            build.addEntity(bes)

                        else:
                            #  Define pointer to bes
                            bes = build.bes

                        if bes.hasBattery is False:
                            bat = Battery.BatteryExtended(environment=
                                                          city.environment,
                                                          soc_init_ratio=0.1,
                                                          capacity_kwh=2)

                            bes.addDevice(bat)

                            #  Set GA start value to False
                            bes.hasBattery = False

                        if bes.hasBoiler is False or add_init_boi:
                            q_nom = dimfunc.get_max_power_of_building(
                                build,
                                with_dhw=True) * 2

                            boil = Boiler.BoilerExtended(environment=
                                                         city.environment,
                                                         q_nominal=q_nom,
                                                         eta=eta_boi)

                            bes.addDevice(boil)

                            if add_init_boi:
                                bes.hasBoiler = True
                            else:
                                bes.hasBoiler = False

                        if bes.hasChp is False:
                            q_nom = dimfunc.get_max_power_of_building(
                                build,
                                with_dhw=False) / 5

                            p_el = asue.calc_asue_el_th_ratio(q_nom) * q_nom

                            chp = CHP.ChpExtended(environment=
                                                  city.environment,
                                                  q_nominal=q_nom,
                                                  p_nominal=p_el)

                            bes.addDevice(chp)

                            #  Set GA start value to False
                            bes.hasChp = False

                        if bes.hasElectricalHeater is False:
                            q_nom = dimfunc.get_max_power_of_building(
                                build,
                                with_dhw=True) * 2

                            eh = EH.ElectricalHeaterExtended(environment=
                                                             city.environment,
                                                             q_nominal=q_nom)

                            bes.addDevice(eh)

                            #  Set GA start value to False
                            bes.hasElectricalHeater = False

                        if bes.hasHeatpump is False:
                            q_nom = dimfunc.get_max_power_of_building(
                                build,
                                with_dhw=False)

                            hp = HP.heatPumpSimple(environment=
                                                   city.environment,
                                                   q_nominal=q_nom)

                            bes.addDevice(hp)

                            #  Set GA start value to False
                            bes.hasHeatpump = False

                        if bes.hasPv is False:
                            #  TODO: Max PV limitation

                            photovoltaic = PV.PV(environment=city.environment,
                                                 area=20, eta=eta_pv)

                            bes.addDevice(photovoltaic)

                            #  Set GA start value to False
                            bes.hasPv = False

                        if bes.hasTes is False or add_init_boi:
                            tes = TES. \
                                thermalEnergyStorageExtended(environment=
                                                             city.environment,
                                                             t_init=0.8 * (
                                                                     60 - 20),
                                                             capacity=200)
                            bes.addDevice(tes)

                            if add_init_boi:
                                bes.hasTes = True
                            else:
                                bes.hasTes = False


def del_existing_esys(city):
    """
    Delete all esys on bes on each building
    
    Parameters
    ----------
    city : object
        City object instance of pyCity_calc
    """

    for n in city.nodes():
        if 'node_type' in city.nodes[n]:
            if city.nodes[n]['node_type'] == 'building':
                if 'entity' in city.nodes[n]:
                    if city.nodes[n]['entity']._kind == 'building':

                        #  Define building pointer
                        build = city.nodes[n]['entity']

                        if build.hasBes:
                            bes = build.bes

                            #  Reset values
                            bes.battery = []
                            bes.boiler = []
                            bes.chp = []
                            bes.electricalHeater = []
                            bes.heatpump = []
                            bes.inverterAcdc = []
                            bes.inverterDcac = []
                            bes.pv = []
                            bes.tes = []

                            # The new BES is still empty
                            bes.hasBattery = False
                            bes.hasBoiler = False
                            bes.hasChp = False
                            bes.hasElectricalHeater = False
                            bes.hasHeatpump = False
                            bes.hasInverterAcdc = False
                            bes.hasInverterDcac = False
                            bes.hasPv = False
                            bes.hasTes = False


def gen_boiler_ref_scenario(city, boi_resc=4, eta_boi=0.95):
    """
    Deletes all existing energy systems in city and adds boilers as reference
    scenario.
    Boiler size is defined by thermal peak of reference scenario *
    boi_resc factor (default: 4) to ensure thermal coverage in all scenarios

    Parameters
    ----------
    city : object
        City object of pyCity_calc
    boi_resc : float, optional
        Rescaling factors for boilers (default: 4)
    eta_boi : float, optional
        Initial boiler efficiency (default: 0.95)
    """

    assert boi_resc > 0
    if boi_resc < 1:
        msg = 'Boiler rescaling factor is smaller than 1. Check if this has' \
              ' been done intentionally!'
        warnings.warn(msg)

    #  Delete all existing energy systems (if existent)
    del_existing_esys(city=city)

    list_build_ids = city.get_list_build_entity_node_ids()

    for n in list_build_ids:
        build = city.nodes[n]['entity']
        q_dot_max = \
            dimfunc.get_max_power_of_building(building=build, get_therm=True,
                                              with_dhw=True)

        if build.hasBes is False:
            #  Generate BES and add to building
            bes = BES.BES(environment=build.environment)
            build.addEntity(bes)

        boiler = Boiler.BoilerExtended(environment=build.environment,
                                       q_nominal=q_dot_max * boi_resc,
                                       eta=eta_boi)

        #  Add boiler to bes
        build.bes.addDevice(boiler)
