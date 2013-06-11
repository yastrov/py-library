#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from models import Book, Author, Genre
from manager import BookManager
from io import BytesIO
import zipfile
from pprint import pprint
try:
  from lxml import etree
except ImportError:
  try:
    # Python 2.5
    import xml.etree.cElementTree as etree
  except ImportError:
    try:
      # Python 2.5
      import xml.etree.ElementTree as etree
    except ImportError:
      try:
        # normal cElementTree install
        import cElementTree as etree
      except ImportError:
        try:
          # normal ElementTree install
          import elementtree.ElementTree as etree
        except ImportError:
          print("Failed to import ElementTree from any known place")

__doc__ = """Module for walking in library and makes indexing files

Example:
    command = 'sqlite:///{}'.format(args.dbase)
    manager = BookManager(command)
    cm = CrawlerManager(manager)
    cm.run(args.path)
    q = manager.query(Book)
    for row in q.all():
        print(row)"""

class Crawler:
    """Crawler class for indexing ebooks."""
    def __init__(self, path=None):
        self.path = path
    
    def run(self, path=None):
        binfo = BookInfo()
        if path:
            self.path = path
        for base, dirs, files in os.walk(self.path):
            for file in files:
                name = os.path.join(base, file)
                try:
                    if name.endswith(".fb2"):
                        info = binfo.fromfb2(name)
                        yield info
                    elif name.endswith(".fb2.zip"):
                        info = binfo.fromfb2zip(name)
                        yield info
                except etree.XMLSyntaxError as e:
                    print("{}: {}".format(e, name))
                except InvalidZipFile as e:
                    print(e)
                except Exception as e:
                    print("{}: {}".format(e, name))


class CrawlerManager:
    def __init__(self,  manager, crawler=None, path=None):
        """Crawler or path for indexing"""
        self.manager = manager
        self.path = path
        if not crawler:
            self.crawler = Crawler()

    def __registerbook(self, dict_):
        """Register one book in database.
        dict_ - dictionary with book information"""
        session = self.manager.getsession()
        a_list = []
        for element in dict_.authors:
            a = Author.get(session,
                            element["lastname"],
                            element["firstname"])
            self.manager.add(a)
            a_list.append(a)

        genre_list = []
        genres = dict_.genres
        for name in genres:
            g = Genre.get(session, name)
            self.manager.add(g)
            genre_list.append(g)
        b = Book(dict_.title,dict_.lang, a_list, genre_list, dict_.path)
        self.manager.add(b)
        self.manager.commit()
    
    def run(self, path=None):
        if path:
            self.path = path
        for info in self.crawler.run(self.path):
            self.__registerbook(info)


class BookInfo(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __xml_to_dict(self, file, path):
        self.path = path
        ns = {'n':'http://www.gribuser.ru/xml/fictionbook/2.0'}
        
        tree = etree.parse(file)
        root = tree.getroot()
        #Title
        self.title = tree.xpath('//n:book-title',
                                namespaces=ns)[0].text
        #Genres
        
        genre_list = tree.xpath('//n:genre',
                                namespaces=ns)
        self.genres = []
        for element in genre_list:
            self.genres.append(element.text)

        #lang
        self.lang = tree.xpath('//n:title-info/n:lang',
                                namespaces=ns)[0].text
        #Author
        self.authors = []
        auth_list =  tree.xpath('//n:title-info/n:author',
                                namespaces=ns)
        for element in auth_list:
            d = {}
            d["firstname"] = element.xpath('//n:first-name',
                                namespaces=ns)[0].text
            d["lastname"] = element.xpath('//n:last-name',
                                namespaces=ns)[0].text
            self.authors.append(d)
        return self

    def fromfb2(self, fname):
        return self.__xml_to_dict(fname, fname)

    def fromfb2zip(self, fname):
        data = None
        with zipfile.ZipFile(fname, "r") as zip:
            error = zip.testzip()
            if error:
                #print("Bad file '%s' in archieve '%s'!"
                #        %(error, zipname) )
                #raise Exception("Bad file '%s' in archieve '%s'!".format(error, zipname))
                raise InvalidZipFile(zipname,error,)
            name = zip.namelist()[0]
            data = zip.read(name)
        datafile = BytesIO(data)
        return self.__xml_to_dict(datafile, fname)


class InvalidZipFile(Exception):
    def __init__(self, filename, error):
        """filename - file name of zip archive;
        error - file name of first bad file in archive."""
        self.filename = filename
        self.error = error
    def __repr__(self):
        return "Bad file '%s' in archieve '%s'!".format(error, filename)
    def __str__(self):
        return repr(self)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("path", default=os.getcwd(),
                        help="work path")
    parser.add_argument("-d", "--dbase",
                        help="database path")
    args = parser.parse_args()
    command = 'sqlite:///{}'.format(args.dbase)
    manager = BookManager(command)
    cm = CrawlerManager(manager)
    cm.run(args.path)
    q = manager.query(Book)
    for row in q.all():
        print(row)