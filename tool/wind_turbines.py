# -*- coding: latin-1 -*-
"""
Copyright © 2024 Eole-lien SC.
All rights reserved as Copyright owner.

Copyright ©

Informations sur les éoliennes surveillées

"""
import ast
import configparser
import logging
import os
import platform


class WindTurbines(object):
    def __init__(self, path=None, test=False):
        self._l_wind_s_wts = []
        self._lwt_ip = []
        match platform.node():
            case 'VINEA64' | 'MSI':
                self.path = 'P:/Eole-Lien/Eolienne1/Exploitation/Enercon/opinum'
                self.home = True
            case _:
                self.path = '.'
                self.home = False
        self.wt_path = os.path.join(self.path, 'wind_turbines.ini')
        self.last_values = os.path.join(self.path, 'last_values.ini')
        if test:
            self.last_values = os.path.join(self.path, 'last_values_test.ini')
        self.config = configparser.ConfigParser()
        self.config.read(self.wt_path)
        self._l_wind_turbines = self.config.get("WT", "list").split(",")

    @property
    def l_wind_turbines(self):
        return self._l_wind_turbines

    def get_ip(self, s_wt):
        s_wt = s_wt.strip()  # Supprime les espaces éventuels
        if s_wt in self.config.sections():
            ip = self.config.get(s_wt, "IP")
            return ip
        raise Exception(f'ERR: IP not found for {s_wt}')

    def get_variable_id(self, s_wt):
        s_wt = s_wt.strip()  # Supprime les espaces éventuels
        if s_wt in self.config.sections():
            variable_id = self.config.get(s_wt, "variableId")
            return variable_id
        raise Exception(f'ERR: variableId not found for {s_wt}')

    def write_last_info(self, s_wt, info):
        try:
            with open(self.last_values, 'r') as f:
                lines = f.readlines()
        except FileNotFoundError:
            lines = []

        new_lines = [line for line in lines if line.find(s_wt) < 0]
        s_new_info = f"{s_wt}={info}\n"
        new_lines.append(s_new_info)

        with open(self.last_values, 'w') as f:
            f.writelines(new_lines)

    def read_last_info(self, s_wt):
        try:
            with open(self.last_values, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    i = line.find(s_wt)
                    if i < 0:
                        continue
                    last_info = line[i + len(s_wt) + 1:-1]
                    return last_info
        except FileNotFoundError:
            return ''
        except Exception as e:
            logging.warning(f'ERR: {e}')
            return ''

    def get_last_sum_energy(self, s_wt):
        try:
            info = self.read_last_info(s_wt)
            if info == '':
                return
            d_info = ast.literal_eval(info)
            return d_info.get('SumEnergy')
        except Exception as e:
            logging.warning(f'ERR: {e}')

    def get_energy(self, s_wt, new_sum_energy):
        last_sum_energy = self.get_last_sum_energy(s_wt)
        if last_sum_energy is None:
            return -1
        energy = new_sum_energy - last_sum_energy

        # écrire la nouvelle valeur dans le fichier
        new_info = str({"SumEnergy": new_sum_energy})
        self.write_last_info(s_wt, new_info)
        return energy

    def write_energy(self, s_wt, sum_energy):
        info = "{'SumEnergy': " + f'{sum_energy}' + "}"
        self.write_last_info(s_wt, info)
