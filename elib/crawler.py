#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from elib.models import Book, Author, Genre
from elib.manager import BookManager
from elib.zipper import InvalidZipFile, ZipReader
try:
    from lxml import etree
except ImportError:
    print("Failed to import lxml module.")
from sqlalchemy.orm.exc import NoResultFound
import logging

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
    def __init__(self, path=None, logger=None):
        self.path = path
        self.logger = logger or logging.getLogger(__name__)
    
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
            self.logger.warning("{}: {}".\
                        format(e, filename))
        except InvalidZipFile as e:
            self.logger.warning(e)
        except Exception as e:
            self.logger.exception("{}: {}".format(e, filename))


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
    def __init__(self,  manager, path=None, logger=None):
        """Crawler or path for indexing"""
        self.manager = manager
        self.path = path
        self.logger = logger or logging.getLogger(__name__)
        self.session = self.manager.getsession()

    def registerbook(self, dict_):
        """Register one book info in database.
        dict_ - dictionary with book information"""
        a_list = []
        for element in dict_.authors:
            try:
                a = Author.get(self.session,
                                element["lastname"],
                                element["firstname"])
            except NoResultFound:
                a = Author(element["lastname"],
                           element["firstname"])
            self.session.add(a)
            a_list.append(a)

        genre_list = []
        genres = dict_.genres
        for name in genres:
            try:
                g = Genre.get(self.session, name)
            except NoResultFound:
                g = Genre(name)
            self.session.add(g)
            genre_list.append(g)
        try:
            b = Book.get(self.session, 
                        dict_.title,dict_.lang, 
                        a_list, genre_list, dict_.path)
        except NoResultFound:
            b = Book(dict_.title,dict_.lang, 
                     a_list, genre_list, dict_.path)
        self.session.add(b)
        self.session.commit()
    
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
        try:
            genre_list = tree.xpath('//n:genre',
                                    namespaces=ns)
        except:
            genre_list = []
        self.genres = []
        for element in genre_list:
            self.genres.append(element.text)

        #lang
        try:
            self.lang = tree.xpath('//n:title-info/n:lang',
                                    namespaces=ns)[0].text
        except:
            self.lang = 'ru'
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
        with ZipReader(fname) as reader:
            error = reader.testzip()
            if error:
                raise InvalidZipFile(zipname, error)
            for name in reader.namelist():
                if name.endswith('.fb2'):
                    datafile = reader.read(name)
        return self.__xml_to_dict(datafile, fname)

    def __fromepub(self, fname):
        with ZipReader(fname) as reader:
            error = reader.testzip()
            if error:
                raise InvalidZipFile(zipname, error)
            datafile = reader.read('META-INF/container.xml')
            tree = etree.parse(datafile)
            root = tree.getroot()
            ns = {'ns':'http://www.idpf.org/2007/opf',
                  'dc':'http://purl.org/dc/elements/1.1/',
                  'n':'urn:oasis:names:tc:opendocument:xmlns:container',
                  'xsi':"http://www.w3.org/2001/XMLSchema-instance"}
            fullpath = tree.xpath('//n:rootfile',namespaces=ns)[0].get('full-path')
            datafile = reader.read(fullpath)
            tree = etree.parse(datafile)
            root = tree.getroot()
            self.title = tree.xpath('//dc:title',namespaces=ns)[0].text
            author =tree.xpath('//dc:creator',namespaces=ns)[0].text
            try:
                firstname, lastname = author.split()
            except ValueError:
                firstname, lastname = author, author
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
    FORMAT = '%(levelname)s - %(message)s'
    logging.basicConfig(format=FORMAT)
    logger = logging.getLogger('Crawler.py')
    cm = CrawlerManager(manager, logger=logger)
    cm.run(args.path)

if __name__ == '__main__':
    main()
