#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from elib.models import Base, Book, Author, Genre
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

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
    """Book Manager provides features of database,
    and hides some trivial operations.
    Support with statement."""

    #def __init__(self, *args, **kwargs):
    def __init__(self, command=None, echo=False):
        if not command:
            command = SQLCOMMAND
        self.engine = create_engine(command, echo=echo)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        Base.metadata.create_all(self.engine)

    # Nearest code for work with session object
    # valid only for single-thread version.
    def getsession(self):
        return self.session

    def closesession(self):
        """Close current session.
        Also it must be called in with statement realisation."""
        if self.session:
            self.session.close()

    def __del__(self):
        self.closesession()

    #For with statement
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            self.session.commit()
        if hasattr(self, "closesession"):
            self.closesession()