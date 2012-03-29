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

class capture_stack(MetlogDecorator):
    def metlog_call(self, *args, **kwargs):
        if self.kwargs is None:
            self.kwargs = {}
        str_length = self.kwargs.pop('str_length', 200)
        list_length = self.kwargs.pop('list_length', 50)

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
                    fields=metlog_blob)

            # re-raise the exception so that callers up the call stack
            # have a chance to do the right thing
            raise

def config_plugin(config):

    default_str_length = config.pop('str_length', 200)
    default_list_length = config.pop('list_length', 50)
    default_logger = config.pop('logger', None)
    default_msg = config.pop('msg', None)

    def metlog_exceptor(self, logger=default_str_length, msg=default_msg,
            str_length=default_str_length,
            list_length=default_list_length,
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
                fields=metlog_blob)

    return metlog_exceptor


