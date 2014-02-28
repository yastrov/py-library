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
        db_name = os.path.join(
                                self.path,
                                "elib.db")
        self.raw_sql = 'sqlite:///{}'.format(db_name)
        self.config = configparser.ConfigParser()
        if os.path.exists(self.fname):
            self.config.read(self.fname)
        else:
            self.create()

    def save(self):
        if not os.path.exists(self.path):
            os.mkdir(self.path)
        with open(self.fname, 'w') as configfile:
            self.config.write(configfile)

    def create(self):
        self.config['dbase'] = {'command': self.raw_sql}
        self.config['logging'] = {'config': 'None.ini'}
        self.save()

    def getSQLCommand(self):
        return self.config.get('dbase', 'command',
                            fallback = self.raw_sql)

    def setSQLCommand(self, command):
        self.config['dbase']['command'] = command

    def getLogConfigName(self):
        r = self.config.get('logging', 'config',
                                fallback = 'None.ini')
        if r is not 'None.ini':
            return r
        else:
            return None

    def setLogConfigName(self, fname):
        self.config['logging']['config'] = fname