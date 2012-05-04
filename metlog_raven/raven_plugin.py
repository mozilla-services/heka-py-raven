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
import time


class RavenClient(Client):
    """
    Customized raven client that doesn't actuall send anything
    """
    def capture(self, event_type, data=None, date=None, time_spent=None,
                extra=None, stack=None, **kwargs):
        """
        Captures and processes an event and pipes it off to SentryClient.send.

        To use structured data (interfaces) with capture:

        >>> capture('Message', message='foo', data={
        >>>     'sentry.interfaces.Http': {
        >>>         'url': '...',
        >>>         'data': {},
        >>>         'query_string': '...',
        >>>         'method': 'POST',
        >>>     },
        >>>     'logger': 'logger.name',
        >>>     'site': 'site.name',
        >>> }, extra={
        >>>     'key': 'value',
        >>> })

        The finalized ``data`` structure contains the following (some optional)
        builtin values:

        >>> {
        >>>     # the culprit and version information
        >>>     'culprit': 'full.module.name', # or /arbitrary/path
        >>>
        >>>     # all detectable installed modules
        >>>     'modules': {
        >>>         'full.module.name': 'version string',
        >>>     },
        >>>
        >>>     # arbitrary data provided by user
        >>>     'extra': {
        >>>         'key': 'value',
        >>>     }
        >>> }

        :param event_type: the module path to the Event class. Builtins can use
                           shorthand class notation and exclude the full module
                           path.
        :param data: the data base, useful for specifying structured data
                           interfaces. Any key which contains a '.' will be
                           assumed to be a data interface.
        :param date: the datetime of this event
        :param time_spent: a float value representing the duration of the event
        :param event_id: a 32-length unique string identifying this event
        :param extra: a dictionary of additional standard metadata
        :param culprit: a string representing the cause of this event
                        (generally a path to a function)
        :return: a 32-length string identifying this event
        """

        data = self.build_msg(event_type, data, date, time_spent,
                extra, stack, **kwargs)

        message = self.encode(data)

        return message


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
            payload = rc.captureException(sys.exc_info())

            get_client('metlog.sentry').metlog(type='sentry',
                    logger=self._fn_fq_name,
                    payload=payload,
                    fields={'epoch_timestamp': time.time()},
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

        # TODO: this isnt' threadsafe
        # the capture and the extraction of the metlog_msg can
        # be caught in a race with 2 threads
        payload = rc.captureException(exc_info)

        self.metlog(type='sentry',
                logger=logger,
                payload=payload,
                fields={'epoch_timestamp': time.time()},
                severity=severity)

    return metlog_exceptor
