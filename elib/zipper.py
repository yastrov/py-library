#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import zipfile
from io import BytesIO
import xml.etree.ElementTree as ET
import logging
__doc__ = """Compress all .fb2 files to individual zip archives.
Also test all zip archives in path.
Print output only bad files."""

logger = logging.getLogger(__name__)

class InvalidZipFile(Exception):
    def __init__(self, filename, error):
        """
        filename - file name of zip archive;
        error - file name of first bad file in archive.
        """
        self.filename = filename
        self.error = error
    def __repr__(self):
        return "Bad file '{}' in archieve '{}'!".\
                format(self.error, self.filename)
    def __str__(self):
        return repr(self)


class ZipReader:
    """
    Class for read zip archive and return
    bytes array or BytesIO.
    """
    def __init__(self, filename):
        self.filename = filename
        self.zip = zipfile.ZipFile(self.filename, 'r')
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        if self.zip is not None:
            self.zip.close()
        if exc_type is None:
            pass
    def namelist(self):
        return self.zip.namelist()
    def read(self, filename, raw=False):
        """
        Read data from file in zip archive.
        If raw is True, bytes array would be returned.
        """
        data = self.zip.read(filename)
        if not raw:
            data = BytesIO(data)
        return data
    def testzip(self):
        return self.zip.testzip()
    def close(self):
        if self.zip is not None:
            self.zip.close()


class InvalidXMLFile(Exception): pass

def XMLvalidate(xmlfile, quite=False):
    """
    Validate XML, raise InvalidXMLFile file.
    If quite is True - return False without
    raise Exception.
    In future in here may be anothe validators.
    """
    try:
        xml = ET.parse(xmlfile)
    except ET.ParseError as e:
        if quite:
            return False
        raise InvalidXMLFile(e) from e
    return True

def walk(path):
    """
    Walk on path. Return filename.
    """
    for base, dirs, files in os.walk(path):
        for fname in files:
            yield os.path.join(base, fname)

def ziponefile(filename, zipname=None):
    """
    Zip one file to individual zip archive.
    filename - name of unzipped file;
    zipname - name of zip archive (if None, it be filename+'.zip');
    """
    if not zipname:
        zipname = filename + '.zip'
    with zipfile.ZipFile(zipname, 'w', 
                zipfile.ZIP_DEFLATED) as zip:
        zip.write(filename, os.path.basename(filename))


def testfile(filename):
    """
    Test one file .zip or .fb2
    Return True if file valid, and False in other situation.
    Some invalid zip arhives may be open with other utility.
    """
    try:
        if filename.endswith('.fb2'):
            XMLvalidate(filename)
        elif filename.endswith('.zip'):
            with ZipReader(filename) as reader:
                error = reader.testzip()
                if error:
                    raise InvalidZipFile(filename, error)
                for name in reader.namelist():
                    if name.endswith('.fb2'):
                        datafile = reader.read(name)
                        XMLvalidate(datafile)
        return True
    except InvalidXMLFile as e:
        logger.info("Error in {}: {}".format(filename, e))
    except zipfile.BadZipFile as e:
        logger.info("{}: {} (Need to check manually!)".format(e, filename))
    except InvalidZipFile as e:
        logger.info(e)
    return False

def zippath(path, removeoriginal=False):
    """
    Zip all files in path and subdirectories.
    removeoriginal - delete original .fb2 files in path
    """
    for name in walk(path):
        if not name.endswith('.fb2'):
            continue
        ziponefile(name)
        if removeoriginal and testfile(name):
            os.remove(name)

def testpath(path, removeoriginal=False):
    """
    Test all zip or fb2 files in path and subdirectories.
    """
    for name in walk(path):
        flag = testfile(name)
        if removeoriginal and testfile(name):
            zipname = name + '.zip'
            if os.path.exists(zipname):
                os.remove(name)

def main():
    try:
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("path",
                            help="work path (required)")
        parser.add_argument("-t", "--test",
                            help="test zip and xml files in path",
                            action="store_true")
        parser.add_argument("-r", "--removeoriginal",
                            help="remove duplicate files in path",
                            action="store_true")
        args = parser.parse_args()
        logging.basicConfig(format='%(levelname)s - %(message)s',
                            level=logging.DEBUG)
        if args.test:
            if os.path.isdir(args.path):
                testpath(args.path, args.removeoriginal)
            elif os.path.isfile(args.path):
                testfile(args.path)
        else:
            if os.path.isdir(args.path):
                zippath(args.path, args.removeoriginal)
            elif os.path.isfile(args.path):
                ziponefile(args.path, args.removeoriginal)
    except KeyboardInterrupt:
        logger.info("Process stopped manually.")
    except ImportError:
        logger.info("Please, use Python 2.7+ or use this module as library."
                    "This version of Python have no module argparse.")
    except Exception as e:
        logger.exception(e)

if __name__ == '__main__':
    main()
