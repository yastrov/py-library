#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import configparser
import os

config_filename = os.path.join(
        os.path.expanduser("~"),
        ".config",
        "elib.ini"
        )
db_name = os.path.join(
        os.path.expanduser("~"),
        ".elib.db")

config = configparser.ConfigParser()

def getSQLCommand():
    return config.get('dbase', 'command',
            fallback='sqlite:///{}'.format(db_name))

def setSQLCommand(command):
    config['dbase']['command'] = command

def saveconfig():
    with open(config_filename, 'w') as configfile:
        config.write(configfile)

def createconfig():
    config['dbase'] = {'command': 'sqlite:///{}'.format(db_name),}
    saveconfig()

if os.path.exists(config_filename):
    config.read(config_filename)