# -*- coding: latin-1 -*-
"""
Copyright © 2024 Eole-lien SC.
All rights reserved as Copyright owner.

Copyright ©

Lecture des données SCADA grâce à la librairie OPC via le VPN
"""

# Attention: opc_labs_quickopc is necessary
import opclabs_quickopc
from OpcLabs.EasyOpc import *
from OpcLabs.EasyOpc.DataAccess import *
from OpcLabs.EasyOpc.DataAccess.OperationModel import *
from OpcLabs.EasyOpc.OperationModel import *


class EnerconOPCEnergy(object):
    def __init__(self, ip, port=6010):
        self.client = EasyDAClient()
        self.server = ServerDescriptor(f'http://{ip}:{port}/')
        self.prefix = 'Loc/Wec/Plant1/'
        self._power = 0
        self._wind_speed = 0
        self._n_rotor = 0
        self._sum_energy = 0
        self._wind_energy = 0
        self._position = 0
        self._active = False

    def build_item(self, s_item):
        da_item = DAReadItemArguments()
        item_desc = DAItemDescriptor(s_item)
        da_item.set_ItemDescriptor(item_desc)
        da_item.set_ServerDescriptor(self.server)
        return da_item

    @property
    def sum_energy(self):
        return self._sum_energy

    @property
    def power(self):
        return self._power

    @property
    def active(self):
        return self._active

    @property
    def n_rotor(self):
        return self._n_rotor

    @property
    def wind_speed(self):
        return self._wind_speed

    @property
    def wind_energy(self):
        return self._wind_energy

    def read_instant_values(self, prefix=None):
        try:
            if prefix is None:
                prefix = self.prefix
            ls_items = ['P', 'Vwind', 'NRotor', 'Wexp', 'PavaVWind', 'GoPos', 'Activ' ]
            l_instant_item = [self.build_item(f'{prefix}{s}') for s in ls_items]
            l_vtq = self.client.ReadMultipleItems(l_instant_item)
            self._power = l_vtq.GetValue(0).Vtq.Value
            self._wind_speed = l_vtq.GetValue(1).Vtq.Value
            self._n_rotor = l_vtq.GetValue(2).Vtq.Value
            self._sum_energy = l_vtq.GetValue(3).Vtq.Value
            self._wind_energy = l_vtq.GetValue(4).Vtq.Value
            self._position = l_vtq.GetValue(5).Vtq.Value
            self._active = l_vtq.GetValue(6).Vtq.Value
        except AttributeError as e:
            raise e

    def read_array_values(self, ls_items):
        try:
            l_item = [self.build_item(f'{self.prefix}{s}') for s in ls_items]
            l_vtq = self.client.ReadMultipleItems(l_item)
            _array = []
            for i in range(0, len(l_vtq)):
                time_stamp = l_vtq.GetValue(i).Vtq.TimestampLocal
                array_length = l_vtq.GetValue(i).Vtq.Value.Length
                l_element = [l_vtq.GetValue(i).Vtq.Value.GetValue(j) for j in range(array_length)]
                _array.append((time_stamp, l_element))
                if l_element[2] != 0:
                    continue

            return _array
        except AttributeError as e:
            print(f'read_array_value {e}')
            raise e

    def close(self):
        self.client.Dispose()
        del self.client
        del self.server
