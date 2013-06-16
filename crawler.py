#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from models import Book, Author, Genre
from manager import BookManager
from io import BytesIO
import zipfile
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
from sqlalchemy.orm.exc import NoResultFound
import traceback

__doc__ = """Module for walking in library and makes indexing files

Example:
    command = 'sqlite:///{}'.format(args.dbase)
    manager = BookManager(command)
    cm = CrawlerManager(manager)
    cm.run(args.path)
    #or
    cm.addfile(args.path)
    q = manager.query(Book)
    for row in q.all():
        print(row)"""

class Crawler:
    """Crawler class for indexing ebooks."""
    def __init__(self, path=None):
        self.path = path
    
    def registerbook(self, dict_):
        """Register book info in database."""
        pass

    def addfile(self, filename):
        """Register single file to index."""
        binfo = BookInfo()
        try:
            info = binfo.parsefile(filename)
            if info:
                self.registerbook(info)
        except etree.XMLSyntaxError as e:
            print("{}: {}".format(e, filename))
        except InvalidZipFile as e:
            print(e)
        except Exception as e:
            print("{}: {}".format(e, filename))
            traceback.print_exc()

    def walk(self, path=None):
        """Main function for indexing path."""
        binfo = BookInfo()
        if path:
            self.path = path
        for base, dirs, files in os.walk(self.path):
            for file in files:
                name = os.path.join(base, file)
                self.addfile(name)


class CrawlerManager(Crawler):
    def __init__(self,  manager, path=None):
        """Crawler or path for indexing"""
        self.manager = manager
        self.path = path

    def registerbook(self, dict_):
        """Register one book info in database.
        dict_ - dictionary with book information"""
        session = self.manager.getsession()
        a_list = []
        for element in dict_.authors:
            try:
                a = Author.get(session,
                                element["lastname"],
                                element["firstname"])
            except NoResultFound:
                a = Author(element["lastname"],
                           element["firstname"])
            self.manager.add(a)
            a_list.append(a)

        genre_list = []
        genres = dict_.genres
        for name in genres:
            try:
                g = Genre.get(session, name)
            except NoResultFound:
                g = Genre(name)
            self.manager.add(g)
            genre_list.append(g)
        try:
            b = Book.get(session, 
                        dict_.title,dict_.lang, 
                        a_list, genre_list, dict_.path)
        except NoResultFound:
            b = Book(dict_.title,dict_.lang, 
                     a_list, genre_list, dict_.path)
        self.manager.add(b)
        self.manager.commit()
    
    def run(self, path=None):
        """Register path"""
        if path:
            self.path = path
        self.walk()


class BookInfo(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __xml_to_dict(self, file, path):
        """Take information from raw fb2 file."""
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

    def __fromfb2(self, fname):
        return self.__xml_to_dict(fname, fname)

    def __fromfb2zip(self, fname):
        data = None
        with zipfile.ZipFile(fname, "r") as zip:
            error = zip.testzip()
            if error:
                #print("Bad file '%s' in archieve '%s'!"
                #        %(error, zipname) )
                #raise Exception("Bad file '%s' in archieve '%s'!".format(error, zipname))
                raise InvalidZipFile(zipname,error)
            name = zip.namelist()[0]
            data = zip.read(name)
        datafile = BytesIO(data)
        return self.__xml_to_dict(datafile, fname)

    def __fromepub(self, fname):
        with zipfile.ZipFile(fname, "r") as zip:
            error = zip.testzip()
            if error:
                raise InvalidZipFile(zipname,error)
            data = zip.read('META-INF/container.xml')
            datafile = BytesIO(data)
            tree = etree.parse(datafile)
            root = tree.getroot()
            ns = {'ns':'http://www.idpf.org/2007/opf',
                  'dc':'http://purl.org/dc/elements/1.1/',
                  'n':'urn:oasis:names:tc:opendocument:xmlns:container',
                  'xsi':"http://www.w3.org/2001/XMLSchema-instance"}
            fullpath = tree.xpath('//n:rootfile',namespaces=ns)[0].get('full-path')
            data = zip.read(fullpath)
            datafile = BytesIO(data)
            tree = etree.parse(datafile)
            root = tree.getroot()
            self.title = tree.xpath('//dc:title',namespaces=ns)[0].text
            author =tree.xpath('//dc:creator',namespaces=ns)[0].text
            firstname, lastname = author.split()
            self.authors = []
            d = {}
            d["firstname"] = firstname
            d["lastname"] = lastname
            self.authors.append(d)
            self.lang = tree.xpath('//dc:language',namespaces=ns)[0].text
            genre_list = tree.xpath('//dc:subject',namespaces=ns)
            self.genres = []
            for element in genre_list:
              self.genres.append(element.text)
            self.path = fname
        return self

    def parsefile(self, filename):
        """Return None if ebook type is unknown
           or book information"""
        if filename.endswith(".fb2"):
            return self.__fromfb2(filename)
        elif filename.endswith(".fb2.zip"):
            return self.__fromfb2zip(filename)
        elif filename.endswith(".epub"):
            return self.__fromepub(filename)
        else:
            return None


class InvalidZipFile(Exception):
    def __init__(self, filename, error):
        """filename - file name of zip archive;
        error - file name of first bad file in archive."""
        self.filename = filename
        self.error = error
    def __repr__(self):
        return "Bad file '{}' in archieve '{}'!".format(error, filename)
    def __str__(self):
        return repr(self)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("path",
                        help="path with ebooks")
    parser.add_argument("-d", "--dbase",
                        help="database path for sqlite")
    parser.add_argument("-c", "--sqlcommand",
                        help="raw sql command for connect to database")
    args = parser.parse_args()
    if args.dbase:
        command = 'sqlite:///{}'.format(args.dbase)
    elif args.sqlcommand:
        command = args.sqlcommand
    else:
        import config
        command = config.getSQLCommand()
    manager = BookManager(command)
    cm = CrawlerManager(manager)
    cm.run(args.path)

if __name__ == '__main__':
    main()