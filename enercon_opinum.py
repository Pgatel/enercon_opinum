# -*- coding: latin-1 -*-
"""
Copyright © 2024 Eole-lien SC.
All rights reserved as Copyright owner.

Copyright ©

Lecture des données SCADA grâce à la librairie OPC via le VPN
"""
from datetime import datetime

from opinum.enercon_opc_energy import EnerconOPCEnergy
from opinum.opinum_push import Opinum
from wind_turbines import WindTurbines

if __name__ == "__main__":
    opinum = Opinum()
    now = datetime.now()
    s_now = opinum.date_10min(opinum.get_utc(now))
    try:
        opc = EnerconOPCEnergy('172.17.165.178')
        wt = WindTurbines()
        opc.read_instant_values()
        if opc.active:
            print(f'{s_now} Eolienne opérationnelle')
        else:
            print(f'{s_now} Eolienne arrêtée')
        print(f'{s_now} Power:{opc.power} kW, Wind speed:{opc.wind_speed:4.1f} m/s,'
              f' Rotor:{opc.n_rotor:3.1f} t/min, Wind Energy {opc.wind_energy} kWh, Sum Energy {opc.sum_energy} kWh')

        energy = wt.get_energy('Temploux', opc.sum_energy)
        print(f'{s_now} Produced Energy = {energy}')
        formatted_date = s_now.replace(' ', 'T') + '+00:00'
        opinum.push_simple('Energy', formatted_date, energy)
        opc.close()
    except Exception as e:
        print(f'{s_now} Exception {e}')
