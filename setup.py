# ***** BEGIN LICENSE BLOCK *****
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

# The Initial Developer of the Original Code is the Mozilla Foundation.
# Portions created by the Initial Developer are Copyright (C) 2012
# the Initial Developer. All Rights Reserved.
#
# Contributor(s):
#   Rob Miller (rmiller@mozilla.com)
#   Victor Ng (vng@mozilla.com)
#
# ***** END LICENSE BLOCK *****
from setuptools import setup, find_packages

version = '0.5'

setup(name='metlog-raven',
      version=version,
      description="A Metlog plugin to send exceptions to Sentry",
      classifiers=[
          'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
          ],
      keywords='',
      author='Victor Ng',
      author_email='vng@mozilla.com',
      url='http://github.com/mozilla-services/metlog-raven',
      license='MPLv2.0',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'metlog-py>=0.9.4',
          'raven==3.1.16'
      ],
      entry_points={
          }
      )
