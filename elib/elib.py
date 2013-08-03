#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from elib.manager import BookManager
from elib.models import Book, Author, Genre
from sqlalchemy.orm.exc import NoResultFound
from elib.config import Config
import argparse
import os
import logging

__version__ = '0.1.1'
__doc__ = """Main module of library package."""

class Counterman:
    """Сlass extends the functionality of BookManager.
    Counterman could inherit from the BookManager, but you can
    use one object manager, instead of creating a variety of others."""

    def __init__(self, manager):
        self.manager = manager
        self.session = manager.getsession()

    #Authors
    def get_all_authors(self):
        """All Authors"""
        return self.session.query(Author).\
                order_by(Author.lastname).all()

    def get_author_by_id(self, id_):
        """Get author by id"""
        return self.session.query(Author).\
                filter(Author.id == id_).one()

    def get_authors_by_name(self, lastname, firstname=None):
        """Get authors by name (lastname and/or firstname)"""
        obj = self.session.query(Author).filter(
                        Author.lastname == lastname)
        if firstname:
            obj = obj.filter(Author.firstname == firstname)
        obj = obj.order_by(Author.lastname)
        obj = obj.all()
        return obj

    #Genres
    def get_all_genres(self):
        """All Genres"""
        return self.session.query(Genre).\
                    order_by(Genre.name).all()

    def get_genre_by_name(self, name):
        """Get genre by name"""
        return self.session.query(Genre).\
                    filter(Genre.name == name).one()

    def get_genre_by_id(self, id_):
        """Get genre by id"""
        return self.session.query(Genre).\
                    filter(Genre.id == id_).one()

    #Books
    def get_all_books(self):
        """All Books"""
        return self.session.query(Book).\
                    order_by(Book.title).all()

    def get_book_by_id(self, id_):
        """Get book by id"""
        return self.session.query(Book).\
                    filter(Book.id == id_).one()

    def get_books_by_title(self, title):
        """Get books by title"""
        return self.session.query(Book).\
                    filter(Book.title == title).\
                    order_by(Book.title).all()
    def get_books_by_lang(self, lang):
        """Get books by language"""
        return self.session.query(Book).\
                    filter(Book.lang == lang).\
                    order_by(Book.title).all()
    def get_books_by_author_id(self, id_):
        """Get books by author id"""
        return self.session.query(Book).\
                    filter(Book.authors.any(id=id_)).\
                    order_by(Book.title).all()

    def get_books_by_genre(self, genre):
        """Get book by genre name"""
        return self.session.query(Book).\
                    filter(Book.genres.any(name=genre)).\
                    order_by(Book.title).all()
    def get_book_by_path(self, path):
        """Get book by path"""
        return self.session.query(Book).\
                    filter(Book.path == path).one()

    def info_for_options(self):
        """Info about class features.
        For auto create menu."""
        cls_dict = type(self).__dict__
        list_ = []
        n = 1
        for key in cls_dict.keys():
            if key.startswith("get"):
                d = {"func": cls_dict[key],
                    "doc": cls_dict[key].__doc__,
                    "fname": key,
                    }
                list_.append(d)
            list_ = sorted(list_, key=lambda x: x["doc"])
        d = {}
        for i in list_:
            d[n] = i
            n +=1
        return d


def indexing(manager, path, logger=None):
    """Indexing path and add books to database.
    CrawlerManager using"""
    import elib.crawler as crawler
    cm = crawler.CrawlerManager(manager, logger=logger)
    if os.path.isdir(path):
        cm.run(path)
    else:
        cm.addfile(path)
    del cm

def humaninterface(manager):
    """Human menu console interface"""
    print_del = lambda: print("{:-^30}".format('-'))
    c = Counterman(manager)
    d = c.info_for_options()
    #Create main menu
    lst = []
    lst.append("{:-^30}".format('Menu:'))
    lst.append("Change item:")
    lst.append("{:4d}| {}".format(0, "Exit"))
    for i, dict_ in d.items():
        lst.append("{:4d}: {}".format(i, dict_["doc"]))
    mainmenu = "\n".join(lst)
    del lst
    #End for main menu creation
    while True:
        try:
            print(mainmenu)
            i = input("->_ ")
            if i == "q":
                break
            i = int(i)
            if i == 0:
                break
            foo = d[i]["func"]
            if "by" in d[i]["fname"]:
                arg = input("Enter data: ")
                if "id" in d[i]["fname"]:
                    arg = int(arg)
                result = foo(c, arg)
            else:
                result = foo(c)
            print("{:-^30}".format('Result:'))
            print("{:4s}| {}".format("id", "object"))
            print_del()
            if type(result) == list:
                for obj in result:
                    print("{:4d}: {}".format(obj.id, str(obj)))
            else:
                print("{:4d}: {}".format(result.id, str(result)))
            print_del()
            i = input("Type (q) to exit or (n)ext: ")
            if i == "q":
                break
        except KeyError:
            print("You enter invalid data. Please, try again.")
        except ValueError:
            print("You enter invalid data. Please, try again.")
        except NoResultFound:
            print("No results found")

def zip_(zipper, path, removeoriginal):
    """Zipping with zipper module.
    zipper - pre imported module"""
    if os.path.isdir(path):
        zipper.zippath(path,
                        removeoriginal)
    else:
        zipper.ziponefile(path,
                        removeoriginal=removeoriginal)

def test_(zipper, path):
    """Test with zipper module.
    zipper - pre imported module"""
    if os.path.isdir(path):
        zipper.testpath(path)
    else:
        zipper.testfile(path)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p","--path",
                        help="path with ebooks")
    parser.add_argument("-d", "--dbase",
                        help="database path for sqlite")
    parser.add_argument("-c", "--sqlcommand",
                        help="raw sql command for connect to database")
    parser.add_argument("-t", "--test",
                        action="store_true",
                        help="test all files")
    parser.add_argument("-z", "--zip",
                        action="store_true",
                        help="zip all files")
    parser.add_argument("-i", "--indexing",
                        action="store_true",
                        help="indexing to database")
    parser.add_argument("-r", "--removeoriginal",
                        action="store_true",
                        help="indexing to database")
    parser.add_argument("-q", "--quiet",
                        action="store_true",
                        help="quiet mode (not show menu)")
    args = parser.parse_args()
    conf = Config()
    f = conf.getLogConfigName()
    if f is not None:
        logging.config.fileConfig(f)
    else:
        FORMAT = '%(levelname)s - %(message)s'
        logging.basicConfig(format=FORMAT)
    logger = logging.getLogger('elib.py')
    try:
        if args.test or args.zip:
            import elib.zipper as zz
            if args.test:
                test_(zz, args.path, )
            if args.zip:
                zip_(zz, args.path, args.removeoriginal)

        command = conf.getSQLCommand()
        if args.dbase:
            command = 'sqlite:///{}'.format(args.dbase)
        elif args.sqlcommand:
            command = args.sqlcommand
        m = BookManager(command)
        with BookManager(command) as manager:
            if args.indexing:
                indexing(manager, args.path, logger)
            if args.quiet:
                from sys import exit
                exit()
            humaninterface(manager)
    except KeyboardInterrupt:
        print("Process stopped manually.")
    except Exception as e:
        logger.exception(e)

if __name__ == '__main__':
    main()