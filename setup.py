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

version = '0.7'

install_requires = ['heka-py>=0.30.3', ]

# Version 5.1-5.4 of Sentry
protocol_v3 = ['raven<3.5']

# We don't support Sentry 6 set
# See bug https://github.com/mozilla-services/heka-py-raven/issues/2
# protocol_v4 = ['raven>=3.5']

setup(name='heka-py-raven',
      version=version,
      description="A heka-py plugin to send exceptions to Sentry",
      classifiers=[
          'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
          ],
      keywords='',
      author='Victor Ng',
      author_email='vng@mozilla.com',
      url='http://github.com/mozilla-services/heka-py-raven',
      license='MPLv2.0',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      extras_require={
          'protocol_v3': install_requires + protocol_v3,
          #'protocol_v4': install_requires + protocol_v4,
          },
      install_requires=install_requires,
      )
