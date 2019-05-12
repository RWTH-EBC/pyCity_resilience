#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

"""
from __future__ import division

import copy

import shapely.geometry.point as point

import pycity_base.classes.Weather as Weather
import pycity_base.classes.supply.BES as BES
import pycity_base.classes.supply.PV as PV
import pycity_base.classes.demand.SpaceHeating as SpaceHeating
import pycity_base.classes.demand.ElectricalDemand as ElectricalDemand
import pycity_base.classes.demand.Apartment as Apartment

import pycity_calc.buildings.building as build_ex
import pycity_calc.cities.city as city
import pycity_calc.environments.co2emissions as co2
import pycity_calc.environments.environment as env
import pycity_calc.environments.germanmarket as germarkt
import pycity_calc.environments.timer as time
import pycity_calc.energysystems.boiler as boi
import pycity_calc.energysystems.chp as chpsys
import pycity_calc.energysystems.thermalEnergyStorage as sto
import pycity_calc.energysystems.heatPumpSimple as hpsys
import pycity_calc.energysystems.electricalHeater as ehsys
import pycity_calc.energysystems.battery as batt
import pycity_calc.simulation.energy_balance.check_eb_requ as checkeb

import pycity_resilience.ga.parser.parse_ind_to_city as parse_ind_to_city
import pycity_resilience.ga.parser.parse_city_to_ind as parse_city_to_ind
import pycity_resilience.ga.preprocess.add_bes as addbes


class TestParser():
    def test_parse_city_to_ind(self):
        #  Generate city object
        #  Create extended environment of pycity_calc
        year = 2010
        timestep = 900  # Timestep in seconds
        location = (51.529086, 6.944689)  # (latitude, longitute) of Bottrop
        altitude = 55  # Altitude of Bottrop

        #  Generate timer object
        timer = time.TimerExtended(timestep=timestep, year=year)

        #  Generate weather object
        weather = Weather.Weather(timer, useTRY=True, location=location,
                                  altitude=altitude)

        #  Generate market object
        market = germarkt.GermanMarket()

        #  Generate co2 emissions object
        co2em = co2.Emissions(year=year)

        #  Generate environment
        environment = env.EnvironmentExtended(timer, weather, prices=market,
                                              location=location, co2em=co2em)

        #  Generate city object
        city_object = city.City(environment=environment)

        extended_building1 = build_ex.BuildingExtended(environment,
                                                       build_year=1990,
                                                       mod_year=2003,
                                                       build_type=0,
                                                       roof_usabl_pv_area=30,
                                                       net_floor_area=150,
                                                       height_of_floors=3,
                                                       nb_of_floors=2,
                                                       neighbour_buildings=0,
                                                       residential_layout=0,
                                                       attic=0, cellar=1,
                                                       construction_type='heavy',
                                                       dormer=0)

        extended_building2 = build_ex.BuildingExtended(environment,
                                                       build_year=1990,
                                                       mod_year=2003,
                                                       build_type=0,
                                                       roof_usabl_pv_area=30,
                                                       net_floor_area=150,
                                                       height_of_floors=3,
                                                       nb_of_floors=2,
                                                       neighbour_buildings=0,
                                                       residential_layout=0,
                                                       attic=0, cellar=1,
                                                       construction_type='heavy',
                                                       dormer=0)

        bes1 = BES.BES(environment=environment)
        bes2 = BES.BES(environment=environment)

        lower_activation_limit = 0.5
        chp_q_nom = 10000
        t_max = 86
        p_nominal = 4500
        eta_total = 0.87

        chp = chpsys.ChpExtended(environment=environment,
                                 p_nominal=p_nominal,
                                 q_nominal=chp_q_nom,
                                 eta_total=eta_total,
                                 t_max=t_max,
                                 lower_activation_limit=lower_activation_limit,
                                 thermal_operation_mode=True)

        # Create Boiler
        boi_q_nom = 10000
        eta = 0.9
        boiler = boi.BoilerExtended(environment, q_nominal=boi_q_nom, eta=eta)

        # Create thermal storage 1
        t_init = 55  # °C
        tes_kg_nom = 300  # kg
        t_max = 60  # °C
        t_min = 20  # °C
        cp = 4186  # J/kgK
        rho = 1000  # kg / m³
        tes1 = sto.thermalEnergyStorageExtended(environment=environment,
                                                t_init=t_init,
                                                c_p=cp,
                                                capacity=tes_kg_nom,
                                                t_max=t_max,
                                                t_min=t_min,
                                                rho=rho)

        # Create thermal storage 2
        t_init = 40  # °C
        tes_kg_nom_2 = 200  # kg
        t_max = 45  # °C
        t_min = 20  # °C
        cp = 4186  # J/kgK
        rho = 1000  # kg / m³
        tes2 = sto.thermalEnergyStorageExtended(environment=environment,
                                                t_init=t_init,
                                                c_p=cp,
                                                capacity=tes_kg_nom_2,
                                                t_max=t_max,
                                                t_min=t_min,
                                                rho=rho)

        #  Create HP
        hp_q_nom = 10000  # W
        tMax = 45  # °C
        hpType = 'aw'  # air water hp
        tSink = 45  # °C

        heatpump = hpsys.heatPumpSimple(environment=environment,
                                        q_nominal=hp_q_nom,
                                        t_max=tMax,
                                        hp_type=hpType,
                                        t_sink=tSink)

        # Create Electrical Heater
        eh_q_nom = 10000
        eheater = ehsys.ElectricalHeaterExtended(environment=environment,
                                                 q_nominal=eh_q_nom)

        # create the battery
        soc_init_ratio = 0.5
        bat_capacity_kwh = 20  # kWh
        battery = batt.BatteryExtended(environment, soc_init_ratio,
                                       bat_capacity_kwh)

        #  Create PV
        pv_area = 30
        pv_simple = PV.PV(environment, area=pv_area, eta=0.1275, beta=35)

        #  Add to bes1
        bes1.addMultipleDevices([chp, boiler, tes1])

        #  Add to bes2
        bes2.addMultipleDevices([heatpump, eheater, tes2, pv_simple, battery])

        #  Add bes1 to building1
        extended_building1.addEntity(entity=bes1)

        #  Add bes2 to bulding2
        extended_building2.addEntity(entity=bes2)

        #  Add buildings to city_object
        city_object.add_extended_building(extended_building1,
                                          position=point.Point(0, 0))
        city_object.add_extended_building(extended_building2,
                                          position=point.Point(50, 0))

        ind = parse_city_to_ind.parse_city_to_ind_dict(city=city_object)

        #  No LHN in ind
        assert ind['lhn'] == []

        ind[1001]['chp'] = chp_q_nom
        ind[1001]['boi'] = boi_q_nom
        ind[1001]['tes'] = tes_kg_nom
        ind[1001]['hp_aw'] = 0
        ind[1001]['hp_ww'] = 0
        ind[1001]['eh'] = 0
        ind[1001]['pv'] = 0
        ind[1001]['bat'] = 0

        ind[1002]['chp'] = 0
        ind[1002]['boi'] = 0
        ind[1002]['tes'] = tes_kg_nom_2
        ind[1002]['hp_aw'] = hp_q_nom
        ind[1002]['hp_ww'] = 0
        ind[1002]['eh'] = eh_q_nom
        ind[1002]['pv'] = pv_area
        ind[1002]['bat'] = bat_capacity_kwh

        #  Add LHN
        city_object.add_edge(1001, 1002, network_type='heating')

        ind = parse_city_to_ind.parse_city_to_ind_dict(city=city_object)

        #  No LHN in ind
        assert ind['lhn'] == [[1001, 1002]]

        ind[1001]['chp'] = chp_q_nom
        ind[1001]['boi'] = boi_q_nom
        ind[1001]['tes'] = tes_kg_nom
        ind[1001]['hp_aw'] = 0
        ind[1001]['hp_ww'] = 0
        ind[1001]['eh'] = 0
        ind[1001]['pv'] = 0
        ind[1001]['bat'] = 0

    def test_parse_ind_dict_to_city(self):
        #  Generate city object
        #  Create extended environment of pycity_calc
        year = 2010
        timestep = 900  # Timestep in seconds
        location = (51.529086, 6.944689)  # (latitude, longitute) of Bottrop
        altitude = 55  # Altitude of Bottrop

        #  Generate timer object
        timer = time.TimerExtended(timestep=timestep, year=year)

        #  Generate weather object
        weather = Weather.Weather(timer, useTRY=True, location=location,
                                  altitude=altitude)

        #  Generate market object
        market = germarkt.GermanMarket()

        #  Generate co2 emissions object
        co2em = co2.Emissions(year=year)

        #  Generate environment
        environment = env.EnvironmentExtended(timer, weather, prices=market,
                                              location=location, co2em=co2em)

        #  Generate city object
        city_object = city.City(environment=environment)

        extended_building1 = build_ex.BuildingExtended(environment,
                                                       build_year=1990,
                                                       mod_year=2003,
                                                       build_type=0,
                                                       roof_usabl_pv_area=30,
                                                       net_floor_area=150,
                                                       height_of_floors=3,
                                                       nb_of_floors=2,
                                                       neighbour_buildings=0,
                                                       residential_layout=0,
                                                       attic=0, cellar=1,
                                                       construction_type='heavy',
                                                       dormer=0)

        extended_building2 = build_ex.BuildingExtended(environment,
                                                       build_year=1990,
                                                       mod_year=2003,
                                                       build_type=0,
                                                       roof_usabl_pv_area=30,
                                                       net_floor_area=150,
                                                       height_of_floors=3,
                                                       nb_of_floors=2,
                                                       neighbour_buildings=0,
                                                       residential_layout=0,
                                                       attic=0, cellar=1,
                                                       construction_type='heavy',
                                                       dormer=0)

        for i in range(2):
            #  Create demands (with standardized load profiles (method=1))
            heat_demand = SpaceHeating.SpaceHeating(environment,
                                                    method=1,
                                                    profile_type='HEF',
                                                    livingArea=100,
                                                    specificDemand=130)

            el_demand = ElectricalDemand.ElectricalDemand(environment,
                                                          method=1,
                                                          annualDemand=3000,
                                                          profileType="H0")

            #  Create apartment
            apartment = Apartment.Apartment(environment)

            #  Add demands to apartment
            apartment.addMultipleEntities([heat_demand, el_demand])

            if i == 0:
                #  Add apartment to extended building
                extended_building1.addEntity(entity=apartment)
            else:
                #  Add apartment to extended building
                extended_building2.addEntity(entity=apartment)

        #  Add buildings to city_object
        city_object.add_extended_building(extended_building1,
                                          position=point.Point(0, 0))
        city_object.add_extended_building(extended_building2,
                                          position=point.Point(50, 0))

        addbes.add_bes_to_city(city=city_object)

        chp_size = 10000
        boi_size = 30000
        tes_size = 500
        pv_area = 30

        dict_b1 = {'chp': chp_size, 'boi': boi_size, 'tes':tes_size,
                   'eh': 0, 'hp_aw': 0, 'hp_ww': 0, 'pv': pv_area,
                   'bat': 0}

        pv_area2 = 50
        bat_size = 12

        dict_b2 = {'chp': 0, 'boi': 0, 'tes':0,
                   'eh': 0, 'hp_aw': 0, 'hp_ww': 0, 'pv': pv_area2,
                   'bat': bat_size}

        ind = {1001: dict_b1, 1002: dict_b2, 'lhn': [[1001, 1002]]}

        city_obj = parse_ind_to_city.parse_ind_dict_to_city(dict_ind=ind,
                                                            city=city_object)

        assert city_obj.nodes[1001]['entity'].bes.chp.qNominal == chp_size
        assert city_obj.nodes[1001]['entity'].bes.boiler.qNominal == boi_size
        assert city_obj.nodes[1001]['entity'].bes.tes.capacity == tes_size

        assert city_obj.edges[1001, 1002]['network_type'] == 'heating'

        assert city_obj.nodes[1002]['entity'].bes.pv.area == pv_area2
        assert city_obj.nodes[1002]['entity'].bes.battery.capacity == bat_size

    def test_parse_ind_dict_to_city2(self):
        #  Generate city object
        #  Create extended environment of pycity_calc
        year = 2010
        timestep = 900  # Timestep in seconds
        location = (51.529086, 6.944689)  # (latitude, longitute) of Bottrop
        altitude = 55  # Altitude of Bottrop

        #  Generate timer object
        timer = time.TimerExtended(timestep=timestep, year=year)

        #  Generate weather object
        weather = Weather.Weather(timer, useTRY=True, location=location,
                                  altitude=altitude)

        #  Generate market object
        market = germarkt.GermanMarket()

        #  Generate co2 emissions object
        co2em = co2.Emissions(year=year)

        #  Generate environment
        environment = env.EnvironmentExtended(timer, weather, prices=market,
                                              location=location, co2em=co2em)

        #  Generate city object
        city_object = city.City(environment=environment)

        for i in range(7):
            extended_building = build_ex.BuildingExtended(environment,
                                                           build_year=1990,
                                                           mod_year=2003,
                                                           build_type=0,
                                                           roof_usabl_pv_area=30,
                                                           net_floor_area=150,
                                                           height_of_floors=3,
                                                           nb_of_floors=2,
                                                           neighbour_buildings=0,
                                                           residential_layout=0,
                                                           attic=0, cellar=1,
                                                           construction_type='heavy',
                                                           dormer=0)

            #  Create demands (with standardized load profiles (method=1))
            heat_demand = SpaceHeating.SpaceHeating(environment,
                                                    method=1,
                                                    profile_type='HEF',
                                                    livingArea=300,
                                                    specificDemand=100)

            el_demand = ElectricalDemand.ElectricalDemand(environment,
                                                          method=1,
                                                          annualDemand=3000,
                                                          profileType="H0")

            #  Create apartment
            apartment = Apartment.Apartment(environment)

            #  Add demands to apartment
            apartment.addMultipleEntities([heat_demand, el_demand])

            #  Add apartment to extended building
            extended_building.addEntity(entity=apartment)

            #  Add buildings to city_object
            city_object.add_extended_building(extended_building,
                                              position=point.Point(0, i * 10))

        addbes.add_bes_to_city(city=city_object)

        chp_size = 10000
        boi_size = 30000
        tes_size = 500
        pv_area = 30

        dict_b1 = {'chp': chp_size, 'boi': boi_size, 'tes':tes_size,
                   'eh': 0, 'hp_aw': 0, 'hp_ww': 0, 'pv': pv_area,
                   'bat': 0}

        dict_b2 = {'chp': chp_size, 'boi': boi_size, 'tes':tes_size,
                   'eh': 0, 'hp_aw': 0, 'hp_ww': 0, 'pv': pv_area,
                   'bat': 0}

        dict_no = {'chp': 0, 'boi': 0, 'tes': 0,
                   'eh': 0, 'hp_aw': 0, 'hp_ww': 0, 'pv': 0,
                   'bat': 0}

        ind = {1001: dict_b1,
               1002: dict_no,
               1003: dict_b2,
               1004: copy.copy(dict_no),
               1005: copy.copy(dict_no),
               1006: copy.copy(dict_no),
               1007: copy.copy(dict_no),
               'lhn': [[1001, 1002],
                       [1003, 1004,
                        1005, 1006,
                        1007]]}

        city_obj = parse_ind_to_city.parse_ind_dict_to_city(dict_ind=ind,
                                                            city=city_object)

        assert city_obj.nodes[1001]['entity'].bes.chp.qNominal == chp_size
        assert city_obj.nodes[1001]['entity'].bes.boiler.qNominal == boi_size
        assert city_obj.nodes[1001]['entity'].bes.tes.capacity == tes_size

        assert city_obj.nodes[1003]['entity'].bes.chp.qNominal == chp_size
        assert city_obj.nodes[1003]['entity'].bes.boiler.qNominal == boi_size
        assert city_obj.nodes[1003]['entity'].bes.tes.capacity == tes_size

        assert city_obj.edges[1001, 1002]['network_type'] == 'heating'
        assert city_obj.edges[1003, 1004]['network_type'] == 'heating'
        assert city_obj.edges[1004, 1005]['network_type'] == 'heating'
        assert city_obj.edges[1005, 1006]['network_type'] == 'heating'
        assert city_obj.edges[1006, 1007]['network_type'] == 'heating'

        checkeb.check_eb_requirements(city=city_obj)
