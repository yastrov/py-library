#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import zipfile
from io import BytesIO
import xml.etree.ElementTree as ET
__doc__ = """Compress all .fb2 files to individual zip archives.
Also test all zip archives in path.
Print output only bad files."""

def ziponefile(filename, zipname=None, removeoriginal=False):
    """
    Zip one file to individual zip archive.
    filename - name of unzipped file;
    zipname - name of zip archive (if None, it be filename+'.zip');
    removeoriginal - delete original .fb2 files in path.
    """
    if not zipname:
        zipname = filename + '.zip'
    with zipfile.ZipFile(zipname, 'w', 
                zipfile.ZIP_DEFLATED) as zip:
        zip.write(filename, os.path.basename(filename))
        if removeoriginal:
            with zipfile.ZipFile(zipname, 'w') as zip:
                error = zip.testzip()
                if error:
                    print("Bad file '{}' in archieve '{}'!"
                          .format(error, filename) )
                else:
                    os.remove(filename)


def zippath(path, removeoriginal=False):
    """
    Zip all files in path and subdirectories.
    removeoriginal - delete original .fb2 files in path
    """
    for base, dirs, files in os.walk(path):
        for file in files:
            if not file.endswith('.fb2'):
                continue
            fname = os.path.join(base, file)
            ziponefile(fname, removeoriginal=removeoriginal)

def testfile(filename):
    """
    Test one file .zip or .fb2
    Return True if file valid, and False in other situation.
    Some invalid zip arhives may be open with other utility.
    """
    try:
        if filename.endswith('.fb2'):
            xml = ET.parse(filename)
        elif filename.endswith('.zip'):
            with zipfile.ZipFile(filename, 'r') as zip:
                error = zip.testzip()
                if error:
                    print("Bad file '{}' in archieve '{}'!"
                          .format(error, filename) )
                    return False
                for name in zip.namelist():
                    if name.endswith('.fb2'):
                        data = zip.read(name)
                        datafile = BytesIO(data)
                        xml = ET.parse(datafile)
        return True
    except ET.ParseError as e:
        print("Error in {}: {}".format(filename, e))
        return False
    except zipfile.BadZipFile as e:
        print("{}: {} (Need to check manually!)".format(e, filename))
        return False
    except Exception as e:
        print("Invalid zipfile: {}".format(filename))
        return False

def testpath(path, removeoriginal=None):
    """
    Test all zip or fb2 files in path and subdirectories.
    """
    for base, dirs, files in os.walk(path):
        for file in files:
            name = os.path.join(base, file)
            flag = testfile(name)
            if removeoriginal and flag:
                zipname = filename + '.zip'
                if os.path.exists(zipname):
                    os.remove(name)

def main():
    try:
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("path", default=os.getcwd(),
                            help="work path")
        parser.add_argument("-t", "--test",
                            help="test zip and xml files in path",
                            action="store_true")
        parser.add_argument("-r", "--removeoriginal",
                            help="remove duplicate files in path",
                            action="store_true")
        args = parser.parse_args()
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
        print("Process stopped manually.")
    except ImportError:
        print("Please, use Python 2.7+ or use this module as library.")
        print("This version of Python have no module argparse.")

if __name__ == '__main__':
    main()