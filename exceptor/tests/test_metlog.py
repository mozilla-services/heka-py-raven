from exceptor.decorators import capture_stack
from metlog.decorators.base import CLIENT_WRAPPER
from nose.tools import eq_
import json

def exception_call2(a, b, c):
    return a + b + c / (a-b)

@capture_stack
def exception_call1(x, y):
    return exception_call2(y, x, 42)

@capture_stack
def clean_exception_call(x, y):
    return x * y


class DecoratorTestBase(object):
    def setUp(self):
        self.orig_client = CLIENT_WRAPPER.client
        client_config = {
            'sender_class': 'metlog.senders.DebugCaptureSender',
            }
        CLIENT_WRAPPER.activate(client_config)

    def tearDown(self):
        CLIENT_WRAPPER.client = self.orig_client

class TestCannedDecorators(DecoratorTestBase):

    def test_capture_stack(self):
        msgs = []
        try:
            result = exception_call1(5, 5)
        except Exception, e:
            msgs = [json.loads(m) for m in CLIENT_WRAPPER.client.sender.msgs]

        # There should be 1 exception
        eq_(len(msgs), 1)

        # We should have a culprit of exception_call2
        event = msgs[0]
        eq_(event['fields']['culprit'],
            'test_metlog.exception_call2')
        culprit_frame = [f for f in event['fields']['frames'] \
                            if f['function'] == 'exception_call2'][0]
        # Check for the variables that cause the divide by zero
        eq_(culprit_frame['vars']['a'],
            culprit_frame['vars']['b'],
            5)

    def test_capture_stack_passing(self):
        eq_(25, clean_exception_call(5, 5))
