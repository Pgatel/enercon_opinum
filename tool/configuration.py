# -*- coding: latin-1 -*-
"""
Copyright © 2024 Eole-lien SC.
All rights reserved as Copyright owner.

Copyright ©

Outil de base pour les fichier de configuration
"""

import configparser


class EmptyObject(object):
    """
    Base object used when new attributes have to be added to an object.
    """
    pass


config = EmptyObject()


class ConfigurationFactory(object):
    """
    USAGE;
        config = ConfigurationFactory().load_configuration("my_configuration_file_path")
        config.my_section.my_property_id()
    """
    def __init__(self):
        self.parser = configparser.ConfigParser()

    def load_configuration(self, configuration_file_path, configuration):
        self.parser.read(configuration_file_path)
        raw_configuration = self._load_section(self.parser)

        for key in raw_configuration.keys():
            item = self._load_config(key, raw_configuration[key])
            setattr(configuration, item.item_id, item)
        return configuration

    def _load_section(self, section):
        data = {}
        for sub_section in section.keys():
            if isinstance(section[sub_section], configparser.SectionProxy):
                data[sub_section] = self._load_section(section[sub_section])
            else:
                data[sub_section] = section[sub_section]
        return data

    def _load_config(self, config_id, raw_config):
        item = ConfigurationItem(config_id)
        if isinstance(raw_config, str):
            item.value = raw_config
            return item
        else:
            for key in raw_config.keys():
                sub_item = self._load_config(key, raw_config[key])
                setattr(item, sub_item.item_id, sub_item)
        return item


class ConfigurationItem(object):
    """Model object that represents a key-value configuration element."""
    def __init__(self, item_id, item_value=None):
        self.item_id = self._format_id(item_id)
        self.item_value = item_value

    def id(self):
        return self.item_id

    @staticmethod
    def _format_id(id_to_format):
        """
        Converts the identifier into a pythonic one.
        ' ', '-' and '.' are replaces by '_'.
        Args:
            id_to_format: the identifier to format.

        Returns:
            the converted identifier
        """
        formatted_id = id_to_format.replace(".", "_")
        formatted_id = formatted_id.replace("-", "_")
        formatted_id = formatted_id.replace(" ", "_")
        formatted_id = formatted_id.lower()
        return formatted_id

    def get_value(self):
        return self.item_value

    def set_value(self, value):
        self.item_value = value

    def __call__(self, *args, **kwargs):
        return self.get_value()

    value = property(get_value, set_value)
