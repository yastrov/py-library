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
    lastname = Column(String)

    def __init__(self, lastname, firstname):
        self.firstname = firstname
        self.lastname = lastname

    @staticmethod
    def get(dbsession, lastname, firstname=None):
        obj = dbsession.query(Author).filter(
                        Author.lastname == lastname)
        if firstname:
            obj = obj.filter(Author.firstname == firstname)
        obj = obj.first()
        return obj

    def __repr__(self):
        return "<Author(id={},'{}','{}')>".\
                format(self.id, self.lastname, self.firstname)

    def __repr__(self):
        return "{} {}".\
                format(self.lastname,
                        self.firstname)


class Book(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    lang = Column(String, nullable=False)
    genres = relationship('Genre', secondary=book_genres,
                          backref=backref('books', order_by=title))
    authors = relationship('Author', secondary=author_books,
                          backref=backref('books', order_by=title))
    path = Column(String, nullable=False, unique=True)

    def __init__(self, title, lang, authors, genres, path):
        self.title = title
        self.lang = lang
        self.authors = authors
        self.genres = genres
        self.path = path

    def __repr__(self):
        return "<Book(id={}, '{}', '{}')>".\
                    format(self.id, self.title,
                    self.authors)

    def __str__(self):
        au = ','.join(map(lambda x: str(x), self.authors))
        return "{}: {}".\
                    format(au,
                            self.title,
                            )

    @staticmethod
    def get(dbsession, title, lang, authors, genres, path):
        obj = dbsession.query(Book).filter(
                        Book.path == path).one()
        return obj


class Genre(Base):
    __tablename__ = 'genres'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)

    @staticmethod
    def get(dbsession, name):
        obj = dbsession.query(Genre).\
                        filter(Genre.name == name).first()
        return obj

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<Genre('{}')>".format(self.name)

    def __str__(self):
        return "{} {}".format(self.name,
                                genre_table.get(self.name,
                                                'unknown'))