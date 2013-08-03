#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import configparser
import os

class Config:
    def __init__(self):
        self.path = os.path.join(
                        os.path.expanduser("~"),
                        ".elib")
        self.fname = os.path.join(self.path,
                                  "config.ini")
        self.config = configparser.ConfigParser()
        if os.path.exists(self.fname):
            self.config.read(self.fname)
        else:
            self.create()

    def save(self):
        with open(self.fname, 'w') as configfile:
            config.write(configfile)
    def create(self):
        db_name = os.path.join(
                                self.path,
                                "elib.db")
        self.config['dbase'] = {'command': 'sqlite:///{}'.format(db_name)}
        self.config['logging'] = {'config': 'None.ini'}
        self.save()

    def getSQLCommand(self):
        return self.config.get('dbase', 'command',
                            fallback='sqlite:///{}'.\
                            format(db_name))

    def setSQLCommand(self, command):
        self.config['dbase']['command'] = command

    def getLogConfigName(self):
        r = self.config.get('logging', 'config',
                                fallback='None.ini')
        if r is not 'None.ini':
            return r
        else:
            return None

    def setLogConfigName(self, fname):
        self.config['logging']['config'] = fname