# Library Manage Utility

Package of utilities for managing home library.
It uses SQLAlchemy for work with index of ebooks.
Also using lxml for parsing ebook information.

## Installation

Run

    sudo python3 setup.py install

## Contain

### elib.py

Main command line module provides features from other modules.
Only elib available from comandline after installation.

Using:

    python3 elib.py [options]

After install use for help:

    elib -h

### zipper.py

Script for zip all files in directories.
Also may test exist zip archives and fb2 files as valid xml (FictionBook based at XML) document.

Using:

    python3 zipper.py [options] path

Use option -h or --help for help.
path - path with ebooks.

### crawler.py

Script for indexing books and save information to database.

Using:

    python3 crawler.py [options] path

Use option -h or --help for help.
path - path with ebooks.

## P.S.

It may work with Python 2.7.4, but other version may have not argparse library module.