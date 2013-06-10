#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Table
from genretable import genre_table

Base = declarative_base()

# association table
book_genres = Table('book_genres', Base.metadata,
    Column('book_id', Integer, ForeignKey('books.id')),
    Column('genre_id', Integer, ForeignKey('genres.id'))
)
author_books = Table('author_books', Base.metadata,
    Column('book_id', Integer, ForeignKey('books.id')),
    Column('author_id', Integer, ForeignKey('authors.id'))
)

class Author(Base):
    __tablename__ = 'authors'
    
    id = Column(Integer, primary_key=True)
    firstname = Column(String)
    secondname = Column(String)

    def __init__(self, secondname, firstname):
        self.firstname = firstname
        self.secondname = secondname

    @staticmethod
    def get(dbsession, secondname, firstname=None):
        obj = dbsession.query(Author).filter(Author.secondname == secondname)
        if firstname:
            obj = obj.filter(Author.firstname == firstname)
        obj = obj.first()
        if not obj:
            obj = Author(secondname, firstname)
        return obj

    def __repr__(self):
        return "<Author('{}', '{}','{}')>".\
                format(self.id, self.firstname, self.secondname)


class Book(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    lang = Column(String, nullable=False)
    genres = relationship('Genre', secondary=book_genres, backref=backref('books', order_by=title))
    authors = relationship('Author', secondary=author_books, backref=backref('books', order_by=title))
    path = Column(String, nullable=False)

    def __init__(self, title, lang, authors, genres, path):
        self.title = title
        self.lang = lang
        self.authors = authors
        self.genres = genres
        self.path = path

    def __repr__(self):
        return "<Book('{}', '{}', '{}',)>".\
                    format(self.id, self.title, 
                    self.authors)


class Genre(Base):
    __tablename__ = 'genres'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    title = Column(String)

    @staticmethod
    def get(dbsession, name):
        obj = dbsession.query(Genre).filter(Genre.name == name).first()
        if not obj:
            obj = Genre(name)
        return obj

    def __init__(self, name):
        self.name = name
        self.title = genre_table[name]

    def __repr__(self):
        return "<Genre('{}')>".format(self.name)