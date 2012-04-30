# ***** BEGIN LICENSE BLOCK *****
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
# ***** END LICENSE BLOCK *****

from metlog.client import SEVERITY
from metlog.holder import CLIENT_HOLDER
from metlog.holder import get_client
from metlog_raven.raven_plugin import RavenClient
from metlog_raven.raven_plugin import capture_stack
from nose.tools import eq_
import json


def exception_call2(a, b, c):
    return a + b + c / (a - b)


@capture_stack
def exception_call1(x, y):
    return exception_call2(y, x, 42)


@capture_stack
def clean_exception_call(x, y):
    return x * y


class DecoratorTestBase(object):
    def setUp(self):
        self.orig_client = get_client('test', \
                {'sender_class': 'metlog.senders.DebugCaptureSender'})

        # Clobber the sentry plugin
        CLIENT_HOLDER._clients['metlog.sentry'] = self.orig_client


class TestCannedDecorators(DecoratorTestBase):
    def test_capture_stack(self):
        msgs = []
        try:
            exception_call1(5, 5)
        except:
            msgs = [json.loads(m) for m in self.orig_client.sender.msgs]

        # There should be 1 exception
        eq_(len(msgs), 1)

        # We should have a culprit of exception_call2
        event = msgs[0]

        rc = RavenClient()
        sentry_fields = rc.decode(event['payload'])

        eq_(sentry_fields['culprit'],
            'test_metlog.exception_call2')
        frames = sentry_fields['sentry.interfaces.Stacktrace']['frames']
        culprit_frame = [f for f in frames \
                            if f['function'] == 'exception_call2'][0]
        # Check for the variables that cause the divide by zero
        eq_(culprit_frame['vars']['a'],
            culprit_frame['vars']['b'],
            5)

        eq_(event['severity'], SEVERITY.ERROR)

    def test_capture_stack_passing(self):
        eq_(25, clean_exception_call(5, 5))


def test_plugins_config():
    cfg_txt = """
    [metlog]
    sender_class = metlog.senders.DebugCaptureSender

    [metlog_plugin_raven]
    provider=metlog_raven.raven_plugin:config_plugin
    """
    from metlog.config import client_from_text_config
    import json

    client = client_from_text_config(cfg_txt, 'metlog')

    def exception_call2(a, b, c):
        return a + b + c / (a - b)

    def exception_call1(x, y):
        return exception_call2(y, x, 42)

    try:
        exception_call1(5, 5)
    except:
        client.raven('some_logger_name')

    eq_(1, len(client.sender.msgs))

    msg = json.loads(client.sender.msgs[0])

    rc = RavenClient()
    sentry_fields = rc.decode(msg['payload'])
    eq_(sentry_fields['culprit'], 'test_metlog.exception_call2')
    eq_(len(sentry_fields['sentry.interfaces.Stacktrace']['frames']), 3)

    eq_(msg['logger'], 'some_logger_name')
    eq_(msg['type'], 'sentry')
    eq_(msg['severity'], SEVERITY.ERROR)
