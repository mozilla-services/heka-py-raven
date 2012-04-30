# ***** BEGIN LICENSE BLOCK *****
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
# ***** END LICENSE BLOCK *****

# Code to reconstruct the frame as a JSON serializable
from raven import Client

import sys

from metlog.decorators.base import MetlogDecorator
from metlog.holder import get_client
from metlog.client import SEVERITY


class RavenClient(Client):
    def send(self, **data):
        """ Sends messages into metlog """
        self._metlog_msg = self.encode(data)


class capture_stack(MetlogDecorator):
    """
    This decorator provides the ability to catch exceptions, log
    stacktrace data to the metlog backend. After logging, the
    exception will be re-raised.  It is *still* the responsibility of
    callers to handle exceptions properly.

    :param severity: The default severity of the error.  Default is 3 as
      defined by `metlog.client:SEVERITY.ERROR`
      <https://github.com/mozilla-services/metlog-py/blob/master/metlog/client.py> # NOQA

    The logger name will automatically be set the the fully qualified
    name of the decorated function.

    """

    def metlog_call(self, *args, **kwargs):
        if self.kwargs is None:
            self.kwargs = {}
        severity = self.kwargs.pop('severity', SEVERITY.ERROR)

        try:
            result = self._fn(*args, **kwargs)
            return result
        except:

            rc = RavenClient()
            rc.captureException(sys.exc_info())
            payload = rc._metlog_msg

            get_client('metlog.sentry').metlog(type='sentry',
                    logger=self._fn_fq_name,
                    payload=payload,
                    severity=severity)

            # re-raise the exception so that callers up the call stack
            # have a chance to do the right thing
            raise


def config_plugin(config):
    """
    Configure the metlog plugin prior to binding it to the
    metlog client.

    :param str_length: This is the maximum length of each traceback string.
                  Default is 200 characters
    :param list_length: The number of stack frames which will be captured
                   by the logger. Default is 50 frames.
    :param logger: The name that metlog will use when logging messages. By
                    default this string is empty
    :param payload: The default message that will be sent with each stacktrace.
           By default this string is empty
    :param severity: The default severity of the error.  Default is 3 as
      defined by `metlog.client:SEVERITY.ERROR`
      <https://github.com/mozilla-services/metlog-py/blob/master/metlog/client.py> # NOQA

    """

    default_logger = config.pop('logger', None)
    default_severity = config.pop('severity', SEVERITY.ERROR)
    rc = RavenClient()

    def metlog_exceptor(self, logger=default_logger, severity=default_severity,
                exc_info=None):

        if exc_info is None:
            exc_info = sys.exc_info()

        rc.captureException(exc_info)
        payload = rc._metlog_msg

        self.metlog(type='sentry',
                logger=logger,
                payload=payload,
                severity=severity)

    return metlog_exceptor
