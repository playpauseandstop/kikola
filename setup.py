#!/usr/bin/env python

import os

from distutils.core import setup


DIRNAME = os.path.dirname(__file__)

readme = open(os.path.join(DIRNAME, 'README.rst'), 'r')
README = readme.read()
readme.close()

version = __import__('kikola').get_version()


setup(
    name='kikola',
    version=version,
    description="Kikola is collection of Django's custom form fields and " \
                "widgets, model fields and reusable apps.",
    long_description=README,
    author='Igor Davydenko',
    author_email='playpauseandstop@gmail.com',
    url='http://github.com/playpauseandstop/kikola/',
    download_url='https://github.com/playpauseandstop/kikola/tarball/%s' % \
                 version,
    packages=[
        'kikola',
        'kikola.contrib',
        'kikola.contrib.basicsearch',
        'kikola.core',
        'kikola.db',
        'kikola.forms',
        'kikola.middleware',
        'kikola.shortcuts',
        'kikola.templatetags',
        'kikola.utils',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'License :: OSI Approved :: BSD License',
    ],
    keywords='django context_processors forms fields middleware reusable ' \
             'apps templatetags widgets',
    license='BSD License',
)
