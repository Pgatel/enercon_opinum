# -*- coding: latin-1 -*-
"""
Copyright © 2024 Eole-lien SC.
All rights reserved as Copyright owner.

Copyright ©
"""
import json
import logging
from datetime import time, timezone, timedelta

import pytz
import requests
from pytz.exceptions import AmbiguousTimeError, NonExistentTimeError


class OpinumPush(object):
    def __init__(self):
        self.url = 'https://push.opinum.com/api/data'
        self.authorization = 'Basic cGFzY2FsLmdhdGVsbGllckB0ZW1wbG91eC5iZTpUZW1wbG91eF81MDIwMjhvcGk='
        self.headers = {'Content-Type': 'application/json',
                        'Authorization': self.authorization, }
        self.tz = pytz.timezone("Europe/Brussels")
        self.tz_utc = timezone.utc
        self.ambiguous = None
        self.zone_ambiguous = False
        self.utc = 0
        self.offset_ambiguous = 0
        self.date_utc = None


    @staticmethod
    def date_10min(date):
        minute = int(date.minute / 10) * 10
        hour1 = time(hour=date.hour, minute=minute)
        _day = date.timetuple().tm_yday
        s_hour = hour1.strftime("%H:%M:%S")
        s_hour_now = f'{date.strftime("%Y-%m-%d")} {s_hour}'
        return s_hour_now

    def get_utc(self, naive_date):
        """
        Détermine l'utc UTC pour une date donnée dans une zone horaire spécifique.

        :param naive_date: La date au format 'YYYY-MM-DD HH:MM:SS'
        :return: L'utc UTC en heures (exemple : 1 pour +1:00, 2 pour +2:00)
        """
        try:
            localized_date = self.tz.localize(naive_date)  # Ajouter les informations de fuseau horaire
            self.tz.localize(naive_date, is_dst=None)  # Permet de lever une erreur si ambiguë
            date_offset = localized_date.utcoffset() # Calculer le décalage UTC, il peut y avoir l'exception Ambiguous
            self.utc = int(date_offset.total_seconds() / 3600)
            self.date_utc = naive_date - date_offset
            self.ambiguous = False
            if self.zone_ambiguous: # on était dans la zone ambiguë, on en sort, mais on doit toujours en tenir compte
                ret_offset = self.offset_ambiguous
                self.date_utc = naive_date - timedelta(hours=ret_offset)
                self.offset_ambiguous = self.utc
                self.zone_ambiguous = False
                return self.date_utc

        except AmbiguousTimeError as e: # la zone ambiguë est le passage été - hiver : on recule dans les heures
            self.ambiguous = True
            if not self.zone_ambiguous: # on entre dans la zone ambiguë
                self.zone_ambiguous = True
                self.offset_ambiguous = self.utc
            # tant que l'on est dans la zone ambiguë, on garde l'utc d'entrée de zone ambiguë
            self.date_utc = naive_date - timedelta(hours=self.offset_ambiguous)
        except NonExistentTimeError: # on reçoit une date interdite, c'est le passage à l'heure d'été
            self.date_utc = naive_date - timedelta(hours=1)
            self.zone_ambiguous = False
        return self.date_utc

    def push(self, variable_id, l_values=None):
        if l_values is None or len(l_values) == 0:
            logging.debug('ERR: Pas de valeur')
            return
        l_payload = []
        for r_value in l_values:
            value = r_value['value']
            date = r_value['date']
            payload = {"VariableId": str(variable_id),
                       "data": [{'date': date, 'value': value}]
                       }
            l_payload.append(payload)
        s_payload = json.dumps(l_payload)
        logging.debug(s_payload)
        response = requests.request("POST", self.url, headers=self.headers, data=s_payload)
        if response.status_code != 200:
            logging.debug(f'ERR: [{response.status_code}] {response.text}')

    def push_simple(self, variable_id, date=None, value=None ):
        if date is None or value is None:
            return
        value = {'VariableId': str(variable_id), "data": [{'date': date, 'value': value}]}
        payload = json.dumps([value])
        logging.debug(payload)
        response = requests.request("POST", self.url, headers=self.headers, data=payload)
        if response.status_code != 200:
            logging.debug(f'ERR: [{response.status_code}] {response.text}')
