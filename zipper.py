#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import zipfile
from io import BytesIO
import xml.etree.ElementTree as ET
__doc__ = """Compress all .fb2 files to individual zip archieves.
Also test all zip archieves in path."""

def ziponefile(filename, zipname=None, removeoriginal=False):
    """
    Zip one file to individual zip archieve.
    filename - name of unzipped file;
    zipname - name of zip archieve (if None, it be filename+'.zip');
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
                    print("Bad file '%s' in archieve '%s'!"
                            %(error, zipname) )
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
    """
    if filename.endswith('.fb2'):
       try:
            xml = ET.parse(filename)
       except ET.ParseError as e:
            print("Error in '%s': %s" %(filename, e))
    elif filename.endswith('.zip'):
        with zipfile.ZipFile(filename, 'r') as zip:
            error = zip.testzip()
            if error:
                print("Bad file '%s' in archieve '%s'!"
                        %(error, filename) )
                return
            for name in zip.namelist():
                if name.endswith('.fb2'):
                    try:
                        data = zip.read(name)
                        datafile = BytesIO(data)
                        xml = ET.parse(datafile)
                    except ET.ParseError as e:
                        print("Error in '%s': %s" %(filename, e))

def testpath(path, removeoriginal=None):
    """
    Test all zip or fb2 files in path and subdirectories.
    """
    for base, dirs, files in os.walk(path):
        for file in files:
            name = os.path.join(base, file)
            testfile(name)
            if removeoriginal:
                zipname = filename + '.zip'
                if os.path.exists(zipname):
                    os.remove(name)

if __name__ == '__main__':
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
        