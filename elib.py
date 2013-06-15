#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from manager import BookManager
from models import Book, Author, Genre
from sqlalchemy.orm.exc import NoResultFound
import config
import argparse
import os
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import subqueryload
import traceback

__doc__ = """Main module of library package."""

class Counterman:
    """docstring for Counterman"""
    def __init__(self, manager):
        self.manager = manager

    def get_all_authors(self):
        """All Authors"""
        return self.manager.query(Author).order_by(Author.lastname).all()
    def get_author_by_id(self, id_):
        """Get author by id"""
        return self.manager.query(Author).filter(Author.id == id_).one()
    def get_authors_by_name(self, lastname, firstname=None):
        """Get authors by name (lastname and/or firstname)"""
        obj = self.manager.query(Author).filter(
                        Author.lastname == lastname)
        if firstname:
            obj = obj.filter(Author.firstname == firstname)
        obj = obj.order_by(Author.lastname)
        obj = obj.all()
        return obj

    def get_all_genres(self):
        """All Genres"""
        return self.manager.query(Genre).order_by(Genre.name).all()
    def get_genre_by_name(self, name):
        """Get genre by name"""
        return self.manager.query(Genre).filter(Genre.name == name).one()
    def get_genre_by_id(self, id_):
        """Get genre by id"""
        return self.manager.query(Genre).filter(Genre.id == id_).one()


    def get_all_books(self):
        """All Books"""
        return self.manager.query(Book).order_by(Book.title).all()
    def get_book_by_id(self, id_):
        """Get book by id"""
        return self.manager.query(Book).filter(Book.id == id_).one()
    def get_books_by_title(self, title):
        """Get books by title"""
        return self.manager.query(Book).filter(Book.title == title).order_by(Book.title).all()
    def get_books_by_lang(self, lang):
        """Get books by language"""
        return self.manager.query(Book).filter(Book.lang == lang).order_by(Book.title).all()
    def get_books_by_author_id(self, id_):
        """Get books by author id"""
        return self.manager.query(Book).filter(Book.authors.any(id=id_)).order_by(Book.title).all()
    def get_books_by_genre(self, genre):
        """Get book by genre name"""
        return self.manager.query(Book).filter(Book.genres.any(name=genre)).order_by(Book.title).all()
    def get_book_by_path(self, path):
        """Get book by path"""
        return self.manager.query(Book).filter(
                        Book.path == path).one()
    def info_for_options(self):
        """Info about class features"""
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


def main():
    try:
        command = config.getSQLCommand()
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

        args = parser.parse_args()
        if args.dbase:
            command = 'sqlite:///{}'.format(args.dbase)
        elif args.sqlcommand:
            command = args.sqlcommand
        manager = BookManager(command)

        if args.test or args.zip:
            import zipper
            if args.test:
                if os.path.isdir(args.path):
                    zipper.testpath(args.path)
                else:
                    zipper.testfile(args.path)
            if args.zip:
                if os.path.isdir(args.path):
                    zipper.zippath(args.path,
                                    args.removeoriginal)
                else:
                    zipper.ziponefile(args.path,
                                    removeoriginal=args.removeoriginal)
        if args.indexing:
            import crawler
            cm = CrawlerManager(manager)
            if os.path.isdir(args.path):
                cm.run(args.path)
            else:
                cm.addfile(args.path)
            del cm

        c = Counterman(manager)
        d = c.info_for_options()
        while True:
            try:
                print("---Menu:---")
                print("Change item:")
                print("{}| {}".format("0", "Exit"))
                for i, dict_ in d.items():
                    print("{}:   {}".format(i, dict_["doc"]))
                i = int(input("->_ "))
                if i == 0 or i == "q":
                    break
                foo = d[i]["func"]
                if "by" in d[i]["fname"]:
                    arg = input("Enter data: ")
                    if "id" in d[i]["fname"]:
                        arg = int(arg)
                    result = foo(c, arg)
                else:
                    result = foo(c)
                print("---Result:---")
                print("{}| {}".format("id", "object"))
                print("-------------")
                if type(result) == list:
                    for obj in result:
                        print("{}: {}".format(obj.id, str(obj)))
                else:
                    print("{}: {}".format(result.id, str(result)))
                i = input("Type (q) to exit or (n)ext: ")
                if i == "q":
                    break
            except NoResultFound:
                print("No results found")
    except KeyboardInterrupt:
        print("Process stopped manually.")
    except Exception as e:
        print(e)
        traceback.print_exc()


if __name__ == '__main__':
    main()