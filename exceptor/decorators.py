# Code to reconstruct the frame as a JSON serializable 
from exceptor.stacks import get_culprit, get_stack_info
from exceptor.utils import varmap
from exceptor.stacks import iter_traceback_frames
from exceptor.encoding import shorten

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
