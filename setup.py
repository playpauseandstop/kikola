#!/usr/bin/env python

from distutils.core import setup
import os


DIRNAME = os.path.dirname(__file__)

readme = open(os.path.join(DIRNAME, 'README.rst'), 'r')
README = readme.read()
readme.close()

VERSION = __import__('kikola').VERSION
if VERSION[2] != None:
    if isinstance(VERSION[2], int):
        version = '%d.%d.%d' % VERSION
    else:
        version = '%d.%d_%s' % VERSION
else:
    version = '%d.%d' % VERSION[:2]

setup(
    name='kikola',
    version=version,
    description="Kikola is collection of Django's custom form fields and " \
                "widgets, model fields and reusable apps.",
    long_description=README,
    author='Igor Davydenko',
    author_email='playpauseandstop@gmail.com',
    url='http://github.com/playpauseandstop/kikola/',
    download_url='http://github.com/playpauseandstop/kikola/files/' \
                 'kikola-%s.zip' % version,
    packages=['kikola', 'kikola.core', 'kikola.db', 'kikola.forms',
              'kikola.middleware', 'kikola.templatetags'],
    classifiers=['Development Status :: 4 - Beta',
                 'Environment :: Web Environment',
                 'Framework :: Django',
                 'License :: OSI Approved :: GNU General Public License (GPL)',
                 'Topic :: Internet :: WWW/HTTP :: Site Management',
    ],
    keywords='django context_processors forms fields middleware reusable ' \
             'apps templatetags widgets',
    license='GNU General Public License (GPL) ver. 3.0',
)
