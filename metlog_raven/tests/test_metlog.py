# ***** BEGIN LICENSE BLOCK *****
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
# ***** END LICENSE BLOCK *****

from metlog.client import SEVERITY
from metlog.holder import CLIENT_HOLDER
from metlog_raven.raven_plugin import RavenClient
from metlog_raven.raven_plugin import InvalidArgumentError
from metlog_raven.raven_plugin import capture_stack
from metlog.config import client_from_dict_config
from nose.tools import eq_
from nose.tools import assert_raises
import json


class TestCannedDecorators(object):

    client_name = '_default_client'

    def setUp(self):
        self.orig_default_client = CLIENT_HOLDER.global_config.get('default')

        client = CLIENT_HOLDER.get_client(self.client_name)

        client_config = {'sender_class': 'metlog.senders.DebugCaptureSender',
                'plugins': {'plugin_section_name':
                    ('metlog_raven.raven_plugin:config_plugin',
                        {'dsn': 'udp://someuser:somepass@somehost.com:5000/2'})}
                    }
        self.client = client_from_dict_config(client_config, client)
        CLIENT_HOLDER.set_default_client_name(self.client_name)

    def tearDown(self):
        del CLIENT_HOLDER._clients[self.client_name]
        CLIENT_HOLDER.set_default_client_name(self.orig_default_client)

    def test_capture_stack(self):

        ###
        def exception_call2(a, b, c):
            return a + b + c / (a - b)

        @capture_stack
        def exception_call1(x, y):
            return exception_call2(y, x, 42)
        ###

        msgs = []
        try:
            exception_call1(5, 5)
        except:
            msgs = [json.loads(m) for m in self.client.sender.msgs]

        # There should be 1 exception
        eq_(len(msgs), 1)

        # We should have a culprit of exception_call2
        event = msgs[0]

        rc = RavenClient()
        sentry_fields = rc.decode(event['payload'])

        eq_(sentry_fields['culprit'],
            'test_metlog in exception_call2')

        frames = sentry_fields['sentry.interfaces.Stacktrace']['frames']
        culprit_frame = [f for f in frames \
                            if f['function'] == 'exception_call2'][0]
        # Check for the variables that cause the divide by zero
        eq_(culprit_frame['vars']['a'],
            culprit_frame['vars']['b'],
            5)

        eq_(event['severity'], SEVERITY.ERROR)

    def test_capture_stack_passing(self):

        @capture_stack
        def clean_exception_call(x, y):
            return x * y

        eq_(25, clean_exception_call(5, 5))


class TestPluginMethod(object):

    client_name = '_default_client'

    def setUp(self):
        self.dsn = "udp://username:password@somehost.com:9000/2"
        self.orig_default_client = CLIENT_HOLDER.global_config.get('default')

        client = CLIENT_HOLDER.get_client(self.client_name)

        client_config = {'sender_class': 'metlog.senders.DebugCaptureSender',
                'plugins': {'plugin_section_name':
                    ['metlog_raven.raven_plugin:config_plugin',
                        {'dsn': self.dsn}]
                    }}
        self.client = client_from_dict_config(client_config, client)
        CLIENT_HOLDER.set_default_client_name(self.client_name)

    def tearDown(self):
        del CLIENT_HOLDER._clients[self.client_name]
        CLIENT_HOLDER.set_default_client_name(self.orig_default_client)

    def test_raven_method(self):
        def exception_call2(a, b, c):
            return a + b + c / (a - b)

        def exception_call1(x, y):
            return exception_call2(y, x, 42)

        try:
            exception_call1(5, 5)
        except:
            self.client.raven('some message')

        eq_(1, len(self.client.sender.msgs))

        msg = json.loads(self.client.sender.msgs[0])

        rc = RavenClient()
        sentry_fields = rc.decode(msg['payload'])
        eq_(sentry_fields['culprit'], 'test_metlog in exception_call2')
        eq_(len(sentry_fields['sentry.interfaces.Stacktrace']['frames']), 3)
        eq_(sentry_fields['extra']['msg'], 'some message')

        eq_(msg['logger'], '')
        eq_(msg['fields']['msg'], 'some message')
        eq_(msg['type'], 'sentry')
        eq_(msg['severity'], SEVERITY.ERROR)
        eq_(msg['fields']['dsn'], self.dsn)


def test_invalid_config():
    dsn = "udp://username:password@somehost.com:9000/2"
    client_config = {'sender_class': 'metlog.senders.DebugCaptureSender',
            'plugins': {'metlog_raven':
                       ['metlog_raven.raven_plugin:config_plugin',
                       {'sentry_dsn': dsn}]
                }}
    assert_raises(InvalidArgumentError, client_from_dict_config, client_config)


class TestDSNConfiguration(object):

    client_name = '_default_client'

    def setUp(self):
        self.orig_default_client = CLIENT_HOLDER.global_config.get('default')

        client = CLIENT_HOLDER.get_client(self.client_name)

        self.dsn = "udp://username:password@somehost.com:9000/2"
        client_config = {'sender_class': 'metlog.senders.DebugCaptureSender',
                'plugins': {'plugin_section_name':
                    ['metlog_raven.raven_plugin:config_plugin',
                        {'dsn': self.dsn}]
                    }}
        self.client = client_from_dict_config(client_config, client)
        CLIENT_HOLDER.set_default_client_name(self.client_name)

    def tearDown(self):
        del CLIENT_HOLDER._clients[self.client_name]
        CLIENT_HOLDER.set_default_client_name(self.orig_default_client)

    def test_raven_method(self):
        def exception_call2(a, b, c):
            return a + b + c / (a - b)

        def exception_call1(x, y):
            return exception_call2(y, x, 42)

        try:
            exception_call1(5, 5)
        except:
            self.client.raven('some message')

        eq_(1, len(self.client.sender.msgs))

        msg = json.loads(self.client.sender.msgs[0])

        rc = RavenClient()
        sentry_fields = rc.decode(msg['payload'])
        eq_(sentry_fields['culprit'], 'test_metlog in exception_call2')
        eq_(len(sentry_fields['sentry.interfaces.Stacktrace']['frames']), 3)
        eq_(sentry_fields['extra']['msg'], 'some message')

        eq_(msg['logger'], '')
        eq_(msg['fields']['msg'], 'some message')
        eq_(msg['type'], 'sentry')
        eq_(msg['severity'], SEVERITY.ERROR)
        eq_(msg['fields']['dsn'], self.dsn)

    def test_explicit_payloads(self):
        expected_payload="some payload data"
        self.client.raven(payload=expected_payload)
        eq_(1, len(self.client.sender.msgs))
        msg = json.loads(self.client.sender.msgs[0])
        eq_(msg['payload'], expected_payload)

    def test_no_sentry_message(self):
        self.client.raven()
        eq_(0, len(self.client.sender.msgs))
