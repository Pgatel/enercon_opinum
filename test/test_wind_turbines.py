# -*- coding: latin-1 -*-
"""
Copyright © 2024 Eole-lien SC.
All rights reserved as Copyright owner.

Copyright ©
"""
import logging
import os
import unittest

from wind_turbines import WindTurbines

from tool import per_logging


class TestWindTurbines(unittest.TestCase):
    def setUp(self):
        print()
        per_logging.add_console_handler(">Info Site<")
        per_logging.log_level(logging.DEBUG)
        logging.info(f'Starting test "{self._testMethodName}"')
        self.wt = WindTurbines(test=True)

    def tearDown(self):
        logging.info(f'End test "{self._testMethodName}"')

    def test_init(self):
        l_wt = self.wt.l_wind_turbines
        self.assertEqual(1, len(l_wt))

    def test_ip(self):
        ip = self.wt.get_ip('Temploux')
        logging.info(f'IP for Temploux: {ip}')
        self.assertEqual('172.17.165.178', ip)

    def test_variable_id(self):
        variable_id = self.wt.get_variable_id('Temploux')
        logging.info(f'VariableId for Temploux: {variable_id}')
        self.assertEqual('6126206', variable_id)

    def test_write_last_info(self):
        if os.path.exists(self.wt.last_values):
            os.remove(self.wt.last_values)
        self.wt.write_energy('Temploux', 2525)
        with open(self.wt.last_values, 'r') as f:
            lines = f.readlines()
        self.assertEqual(1, len(lines))
        self.assertEqual("Temploux={'SumEnergy': 2525}\n", lines[0])

        info = "{'SumEnergy': 2526}"
        self.wt.write_last_info('Temploux', info)
        with open(self.wt.last_values, 'r') as f:
            lines = f.readlines()
        self.assertEqual(1, len(lines))
        self.assertEqual("Temploux={'SumEnergy': 2526}\n", lines[0])

        info = "{'SumEnergy': 1426}"
        self.wt.write_last_info('Waimes', info)
        with open(self.wt.last_values, 'r') as f:
            lines = f.readlines()
        self.assertEqual(2, len(lines))
        self.assertEqual("Temploux={'SumEnergy': 2526}\n", lines[0])
        self.assertEqual("Waimes={'SumEnergy': 1426}\n", lines[1])

    def test_read_last_value(self):
        info = "{'SumEnergy': 2525}"
        self.wt.write_last_info('Temploux', info)
        last_value = self.wt.read_last_info('Temploux')
        self.assertEqual("{'SumEnergy': 2525}", last_value)
        info = "{'SumEnergy': 1426}"
        self.wt.write_last_info('Waimes', info)
        last_value = self.wt.read_last_info('Temploux')
        self.assertEqual("{'SumEnergy': 2525}", last_value)

    def test_read_sum_energy(self):
        if os.path.exists(self.wt.last_values):
            os.remove(self.wt.last_values)
        info = "{'SumEnergy': 2525}"
        self.wt.write_last_info('Temploux', info)
        sum_energy = self.wt.get_last_sum_energy('Temploux')
        self.assertEqual(2525, sum_energy)

    def test_get_energy(self):
        if os.path.exists(self.wt.last_values):
            os.remove(self.wt.last_values)
        sum_energy = self.wt.get_energy('Temploux', 2525)
        self.assertEqual(-1, sum_energy)
        info = "{'SumEnergy': 2525}"
        self.wt.write_last_info('Temploux', info)
        sum_energy = self.wt.get_energy('Temploux', 2530)
        self.assertEqual(5, sum_energy)
        info = "{'SumEnergy': 1426}"
        self.wt.write_last_info('Waimes', info)
        sum_energy = self.wt.get_energy('Waimes', 1441)
        self.assertEqual(15, sum_energy)
