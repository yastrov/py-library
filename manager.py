#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from models import Base, Book, Author, Genre
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

__doc__ = """Use class BookManager for managing 
database with ebooks collection."""

SQLCOMMAND = 'sqlite:///:memory:'

def singleton(cls):
    """Singleton takes from PEP-0318.
    http://www.python.org/dev/peps/pep-0318/#examples"""
    instances = {}
    def getinstance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return getinstance

@singleton
class BookManager:
    """docstring for ClassName"""
    #def __init__(self, *args, **kwargs):
    def __init__(self, command=None, echo=False):
        if not command:
            command = SQLCOMMAND
        self.engine = create_engine(command, echo=echo)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        Base.metadata.create_all(self.engine)

    #Interface for Crawler
    def add(self, obj):
        """Add object to session."""
        self.session.add(obj)

    def commit(self):
        self.session.commit()

    def getsession(self):
        return self.session

    def query(self, *args, **kwargs):
        """Return Query object. After user may do what he want.
        See more at SQLAlchemy manual."""
        return self.session.query(*args, **kwargs)

    def __del__(self):
        if self.session:
            self.session.close()