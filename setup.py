#!/usr/bin/env python3
# -*- coding: utf-8 -*-
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
 
import elib.config as config
import elib.elib as elib

setup(name='elib',
        version=elib.__version__,
        description=('Scripts for managing home ebook (fb2, epub) library:'
                     ' Indexing and search, test zip archives or test xml'
                     ' to valid. '
                     'Main script: elib.py (and elib after installation)'),
        author='Yuri Astrov',
        author_email='yuriastrov@gmail.com',
        url='https://bitbucket.org/yrain/py-library/src',
        #scripts=['elib/elib.py',],
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

config.createconfig()
text = ('--------------------------------\n'
        'After installation:\n'
        '--------------------------------\n'
        'You may set database command in config file:\n{}'
       )
print(text.format(config.config_filename))