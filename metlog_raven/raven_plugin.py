# ***** BEGIN LICENSE BLOCK *****
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
# ***** END LICENSE BLOCK *****

# Code to reconstruct the frame as a JSON serializable 
from raven.utils import varmap
from raven.utils.encoding import shorten
from raven.utils.stacks import get_culprit
from raven.utils.stacks import get_stack_info
from raven.utils.stacks import iter_traceback_frames

import sys

from metlog.decorators.base import MetlogDecorator
from metlog.decorators.base import CLIENT_WRAPPER
from metlog.client import SEVERITY

class capture_stack(MetlogDecorator):
    def metlog_call(self, *args, **kwargs):
        if self.kwargs is None:
            self.kwargs = {}
        str_length = self.kwargs.pop('str_length', 200)
        list_length = self.kwargs.pop('list_length', 50)
        severity = self.kwargs.pop('severity', SEVERITY.ERROR)

        try:
            result = self._fn(*args, **kwargs)
            return result
        except Exception, e:
            exc_info = sys.exc_info()
            exc_type, exc_value, exc_traceback = exc_info

            frames = varmap(lambda k, v: shorten(v,
                string_length=str_length,
                list_length=list_length),
                get_stack_info(iter_traceback_frames(exc_traceback)))

            culprit = get_culprit(frames)

            metlog_blob = {'culprit': culprit,
                    'frames': frames}

            CLIENT_WRAPPER.client.metlog('stacktrace',
                    logger=self._fn_fq_name,
                    severity=severity,
                    fields=metlog_blob)

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
    :param msg: The default message that will be sent with each stacktrace.
           By default this string is empty
    :param severity: The default severity of the error.  Default is 3 as
      defined by `metlog.client:SEVERITY.ERROR` 
      <https://github.com/mozilla-services/metlog-py/blob/master/metlog/client.py>

    """

    default_str_length = config.pop('str_length', 200)
    default_list_length = config.pop('list_length', 50)
    default_logger = config.pop('logger', None)
    default_msg = config.pop('msg', None)
    default_severity = config.pop('severity', SEVERITY.ERROR)

    def metlog_exceptor(self, logger=default_str_length, msg=default_msg,
            str_length=default_str_length,
            list_length=default_list_length,
            severity=default_severity,
            exc_info=None):
        if exc_info is None:
            exc_info = sys.exc_info()

        exc_type, exc_value, exc_traceback = exc_info

        frames = varmap(lambda k, v: shorten(v,
            string_length=str_length,
            list_length=list_length),
            get_stack_info(iter_traceback_frames(exc_traceback)))

        culprit = get_culprit(frames)

        metlog_blob = {'culprit': culprit,
                'frames': frames}

        self.metlog(type='stacktrace',
                logger=logger,
                payload=msg,
                severity=severity,
                fields=metlog_blob)

    return metlog_exceptor


