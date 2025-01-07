# -*- coding: latin-1 -*-
"""
Copyright © 2024 Eole-lien SC.
All rights reserved as Copyright owner.

Copyright ©

Lecture des données SCADA grâce à la librairie OPC via le VPN
"""
import logging
from datetime import datetime


from opinum.opinum_push import OpinumPush
from opinum.enercon_opc_energy import EnerconOPCEnergy

from tool import per_logging
from tool.wind_turbines import WindTurbines

if __name__ == "__main__":
    per_logging.add_console_handler(">Enercon Opinum<")
    per_logging.log_level(logging.DEBUG)

    opinum = OpinumPush()
    now = datetime.now()
    s_now = opinum.date_10min(opinum.get_utc(now))
    logging.info(f'{s_now} (UTC) Starting update of wind turbine energy')
    wt = WindTurbines()
    for site in wt.l_wind_turbines:
        try:
            ip = wt.get_ip(site)
            variable_id = wt.get_variable_id(site)
            opc = EnerconOPCEnergy(ip=ip)
            opc.read_instant_values()
            if opc.active:
                logging.info(f'{s_now} Eolienne {site} opérationnelle : ')
            else:
                logging.info(f'{s_now} Eolienne {site} arrêtée : ')
            logging.info(f'{s_now}    Power:{opc.power} kW, Wind speed:{opc.wind_speed:4.1f} m/s,'
                         f' Rotor:{opc.n_rotor:3.1f} t/min, Wind Energy {opc.wind_energy} kWh, Sum Energy {opc.sum_energy} kWh')

            energy = wt.get_energy(site, opc.sum_energy)
            logging.info(f'{s_now}    Energie produite les 10 dernières minutes = {energy} kWh')
            if energy >= 0:
                formatted_date = s_now.replace(' ', 'T') + '+00:00'
                i = 0
                while i < 5:
                    try:
                        i += 1
                        opinum.push_simple(variable_id, formatted_date, energy)
                        break
                    except Exception as e:
                        logging.error(f'{s_now} ({i}) Exception {e}')
            opc.close()
            logging.info(f'{s_now} (UTC) Ending update of wind turbine energy')
        except Exception as e:
            logging.error(f'{s_now} Exception {e}')
