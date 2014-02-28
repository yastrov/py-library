#!/usr/bin/env python3
# -*- coding: utf-8 -*-
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
import elib.elib
import os

setup(name='elib',
        version=elib.elib.__version__,
        description=('Scripts for managing home ebook (fb2, epub) library:'
                     ' Indexing and search, test zip archives or test xml'
                     ' to valid. '
                     'Main script: elib.py (and elib after installation)'),
        author='Yuri Astrov',
        author_email='yuriastrov@gmail.com',
        url='https://github.com/yastrov/py-library',
        packages=['elib',],
        include_package_data=True,
        install_requires=['lxml>=3.1.0', 
                            'SQLAlchemy>=0.8.0'],
        license = 'MIT',
        entry_points = {
                        'console_scripts': [
                            'elib = elib.elib:main',
                        ],}
        )

text = ('--------------------------------\n'
        'After installation:\n'
        '--------------------------------\n'
        'You may set database command and logging options in config file:\n{}'
       )
fname = os.path.join(
                    os.path.expanduser("~"),
                    ".elib", "config.ini"
                    )
print(text.format(fname))