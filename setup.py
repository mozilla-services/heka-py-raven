from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='metlog-raven',
      version=version,
      description="Adapter for the Raven Sentry client to play nice with Metlog",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Victor Ng',
      author_email='vng@mozilla.com',
      url='http://github.com/mozilla-services/metlog-raven',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'raven'
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
