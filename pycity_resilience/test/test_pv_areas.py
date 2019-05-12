#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

"""
from __future__ import division

import shapely.geometry.point as point

import pycity_base.classes.Weather as Weather

import pycity_calc.buildings.building as build_ex
import pycity_calc.cities.city as city
import pycity_calc.environments.co2emissions as co2
import pycity_calc.environments.environment as env
import pycity_calc.environments.germanmarket as germarkt
import pycity_calc.environments.timer as time

import pycity_resilience.ga.preprocess.pv_areas as pvareas


class TestPVAreas():
    def test_get_dict_usable_pv_areas(self):
        #  Create extended environment of pycity_calc
        year = 2010
        timestep = 3600  # Timestep in seconds
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

        use_pv_area_1 = 30

        extended_building = build_ex. \
            BuildingExtended(environment,
                             build_year=1962,
                             mod_year=2003,
                             build_type=0,
                             roof_usabl_pv_area=use_pv_area_1,
                             net_floor_area=150,
                             height_of_floors=3,
                             nb_of_floors=2,
                             neighbour_buildings=0,
                             residential_layout=0,
                             attic=0, cellar=1,
                             construction_type='heavy',
                             dormer=0)

        position = point.Point(0, 0)

        city_object.add_extended_building(extended_building=extended_building,
                                          position=position)

        use_pv_area_2 = 0

        extended_building2 = build_ex. \
            BuildingExtended(environment,
                             build_year=1962,
                             mod_year=2003,
                             build_type=0,
                             roof_usabl_pv_area=use_pv_area_2,
                             net_floor_area=150,
                             height_of_floors=3,
                             nb_of_floors=2,
                             neighbour_buildings=0,
                             residential_layout=0,
                             attic=0, cellar=1,
                             construction_type='heavy',
                             dormer=0)

        position2 = point.Point(0, 50)

        city_object.add_extended_building(extended_building=extended_building2,
                                          position=position2)

        dict_use_pv_area = pvareas.get_dict_usable_pv_areas(city=city_object)

        assert sorted(dict_use_pv_area.keys()) == [1001, 1002]

        assert dict_use_pv_area[1001] == use_pv_area_1
        assert dict_use_pv_area[1002] == use_pv_area_2
