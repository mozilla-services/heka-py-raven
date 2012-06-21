Configuration
=============

Configuration is normally handled through Metlog's configuration
system using INI configuration files. A raven plugin must use the
`metlog_raven.raven_plugin:config_plugin` as the provider of the
plugin.  The suffix of the configuration section name is used to
set the method name on the Metlog client. Any part after
`metlog_plugin_` will be used as the method name.

In the following example, we will bind a method `raven` into the
Metlog client so that we can send stacktrace information to the 
Metlog server. ::

    [metlog_plugin_raven]
    provider=metlog_raven.raven_plugin:config_plugin

Alternatively, if loading Metlog's configuration by means of a
dict, the plugin can be loaded in the example that follows,
which will also bind the method `raven` to the Metlog client. ::

    {
        'sender_class': 'metlog.senders.StdOutSender',
        'plugins' : {
            'raven' : ['metlog_raven.raven_plugin:config_plugin', {}]
        }
    }

You do not need to specify any other options to enable the plugin.
The default settings are probably fine for you.  You may however set 4
options if you choose.

    * logger: The name that metlog will use when logging messages. By
              default this string is empty
    * severity: The default severity of the error.  Default severity
      level is 3 as defined by `metlog.client:SEVERITY.ERROR` 
      <https://github.com/mozilla-services/metlog-py/blob/master/metlog/client.py>

Usage
=====

Obtaining a client should probably be done through your framework.
Please refer to the metlog documentation for complete details.

That said, if you are impatient you can obtain a client using
`get_client`.  We strongly suggest you do not do this though. ::

    from metlog.holder import get_client
    get_client('myapp', {'sender_class': 'metlog.senders.StdOutSender', 'plugins': {'raven' : ['metlog_raven.raven_plugin:config_plugin', {}]}})

Note that the above sender configuration will only route messages to
stdout so that you can verify that logging is happening during
development.

Logging exceptions is passive.   The raven plugin will not rethrow an
exception automatically if you invoke the method on the client
directly.  This prevents you from seeing exceptions raised from within
the plugin code.

If you use the decorator syntax, the plugin will automatically rethrow
the exception for you.  

The raven plugin provides 2 ways to send messages.  You can use
decorator syntax, or access the plugin through the standard client.

Using the example configuration listed above, the following snippet
will log catcha n exception and fire it off to details. ::

    from metlog.holder import get_client

    metlog = get_client('some_client_name', 
                 {
                    'sender_class': 'metlog.senders.StdOutSender',
                    'plugins': {'raven' : ['metlog_raven.raven_plugin:config_plugin', {}]}
                 })
    try:
        do_some_exception_throwing_thing()
    except:
        metlog.raven('something bad happened')

        # re-raise the exception so someone can properly handle
        # the error
        raise


or you can use the decorator syntax ::

    from metlog_raven.raven_plugin import capture_stack

    metlog = get_client('some_client_name', 
                 {
                    'sender_class': 'metlog.senders.StdOutSender',
                    'plugins': {'raven' : ['metlog_raven.raven_plugin:config_plugin', {}]}
                 })

    @capture_stack
    def some_function(foo, bar):
        # Some code here that throws exceptions
        do_some_exception_throwing_thing()

    some_function('foo', 'bar')

Data structure
==============

The raven plugin will send quite a lot of information.  Important keys
to note:

    * The type of the message will be set to 'stacktrace'
    * The severity is set to 3 (SEVERITY.ERROR)

In the context of determining the source of the error, the 'fields'
section of the metlog blob has 2 keys which are of particular
interest.

    * culprit: This is the function name that threw the
      exception
    * frames: This is a list of stackframes captured.  The 
      frames are ordered from inner most to outer most frame. The
      frame that caused the exception will be at the end of the list.

Each frame is represented as a dictionary with the keys:

    abs_path: Absolute path to the current module
    context_line: source code of the function where the exception passed through
    filename: relative path filename of the current module
    function: function name that the exception passed through
    lineno: line number in the source module where the exception passed through
    module: module name
    pre_context: 2 source lines prior to the exception in the current module
    post_context: 2 source lines after the exception in the current module:
    vars: local variables at the time immediately after the exception has been caught


A sample of the JSON emitted is provided below to illustrate all the
details that are captured.  This sample below is generated by the
included test suite.  ::

    {u'env_version': u'0.8',
     u'fields': {u'epoch_timestamp': 1336490211.8597479, 'msg': ''},
     u'logger': u'myapp',
     u'payload': u'eJzFVm1v2zYQ/iuEvtjBbL0rtY22QNd2n1ZgQNp+aBsIFEUpbGhSICnPWuH/viMppbFTLwXWbgYk66jnjnf3PEf7S9Ap+ZkSE2xQskCBpsKoIWTCUNVgQnX4ek9oZ5gUgPgSmKGj8BB8oEq+Yjum4cVrpaQKwHmHee/eWveWKlSPCCQV2sq65xJVA/oLfC3crTg8nfbQwQFekJ53itmUAkO1KbfUcNmGd6iSYM7TwKWrdlSVAm9dnPeMGKn08g0mv0p5u3zBVMgloC2W0x3lgMpjMOBZmJLV1ovgVZZVOCmKJs0z/GRNSJLEOKFZTRLaZNaZ3FByq/utw5M6z+kar3OSNDRfFXFWZau6XherYk3WhcXTvVHYduxwV6ieTM2MzVb0nINl2JaWuoN0jte0wdvObpfGSbqMi2W8epsUm+RyUyThqrgsiuJD8E3Grgwmt7A9oY6yRkF37OYf4bkXZOTSt7bjfcuELokUDWttPFzpssPmxkKid9BgHe1cW0Ub1XQXeTKWCkMHR6P0hg2oo/uMdYON2Clq4xvoic0iQONHUdMrgU5onQ8LtF+gPL2wvvayWChxE1w7jSnXyIA0bWlcxOCTsJCPftNrb0FbalAG4Vhr9AyNCflVHb6iVd++xB0kQK/c2idxFGVsjK9sDAmTsmMAfXa/6tDdR/jGt3G0vJdXw7FyIeenExWn9SNsULxP4iQmuCni5w/9k3/yT77613lSrZz/Z+0pf+qViGZ2YYYaJbdoFl0N2tBt9DurFFZD9JvVy59S3eroj8HcSBE200r0HppnxzRKw8uIsyrqHMJaNmRUlkwwU5bAPJm5rQlnXtqwuefAr4RvnPXSGUhW9gy6V3pGxtI9urSpllZBk1KPWnAGNMWL6WWOMcQ7HJ0695Rqd2oYp9NBclbKUpsHWvYEbCap2s9Yo9PGfKYljDgEacejanbhpDzGKTkTbtPJ+YTQebFAhRsGCxQSoOsMKjme5lOJ/B+TjNEvqIKLoAjNMVqi6miGa9o8qA0mfbg4mewB7lBzsB+//9X0/HjKHxxJ53j8nvPtK6XxI5Sm/x2lXr1wap6Zq/l49i7QzMeaPcJzOscLVC0QOaUajxQT+7ucwkNlF34eZ49I8BEmz+j7jsPVk8O1y51qjdtv/0/aoO/4c3T4G3lXIHI=',
     u'severity': 3,
     u'timestamp': u'2012-05-08T15:16:51.859750',
     u'type': u'sentry'}

Metlog adds two keys into the fields dictionary.  One is the
'epoch_timestamp' key into the 'fields' dictionary so that logstash
can properly record the time that the exception event occured.
Although raven already captures the timestamp, it's encoded in a
binary blob that logstash can't read.

The other key is 'msg' which is an optional string argument to attach
to the stacktrace.  The message string is included in both the Metlog
'fields' dictionary as well as within the Raven binary blob in the
'extra' key.

The sentry data is packed into the payload in it's native zlib/base64
encoded format for simplicity. Unpacked, the raven encodes the
following information.  ::

    {'checksum': 'ccd44e9a94c1fe48503b38dd95859c95',
     'culprit': 'test_metlog.exception_call2',
     'event_id': '443e20a669b04ba38711f29e74376392',
     'extra': {'msg': ''},
     'level': 40,
     'message': 'ZeroDivisionError: integer division or modulo by zero',
     'modules': {},
     'project': 1,
     'sentry.interfaces.Exception': {'module': 'exceptions',
                                     'type': 'ZeroDivisionError',
                                     'value': 'integer division or modulo by zero'},
     'sentry.interfaces.Stacktrace': {'frames': [{'abs_path': '/Users/victorng/dev/metlog-raven/metlog_raven/tests/test_metlog.py',
                                                  'context_line': '        exception_call1(5, 5)',
                                                  'filename': 'tests/test_metlog.py',
                                                  'function': 'test_plugins_config',
                                                  'lineno': 93,
                                                  'module': 'test_metlog',
                                                  'post_context': ['    except:',
                                                                   "        client.raven('some_logger_name')"],
                                                  'pre_context': ['        return exception_call2(y, x, 42)',
                                                                  '',
                                                                  '    try:'],
                                                  'vars': {'cfg_txt': '\n    [metlog]\n    sender_class = metlog.senders.DebugCaptureSender\n\n    [metlog_plugin_raven]\n    provider=metlog_raven.raven_plugin:config_plugin\n    ',
                                                           'client': '<metlog.client.MetlogClient object at 0x100f1fc50>',
                                                           'client_from_text_config': '<function client_from_text_config at 0x100cc0aa0>',
                                                           'exception_call1': '<function exception_call1 at 0x100f301b8>',
                                                           'exception_call2': '<function exception_call2 at 0x100f27f50>',
                                                           'json': "<module 'json' from '/System/Library/Frameworks/Python.framework/Versions/2.6/lib/python2.6/json/__init__.pyc'>"}},
                                                 {'abs_path': '/Users/victorng/dev/metlog-raven/metlog_raven/tests/test_metlog.py',
                                                  'context_line': '        return exception_call2(y, x, 42)',
                                                  'filename': 'tests/test_metlog.py',
                                                  'function': 'exception_call1',
                                                  'lineno': 90,
                                                  'module': 'test_metlog',
                                                  'post_context': ['',
                                                                   '    try:'],
                                                  'pre_context': ['        return a + b + c / (a - b)',
                                                                  '',
                                                                  '    def exception_call1(x, y):'],
                                                  'vars': {'exception_call2': '<function exception_call2 at 0x100f27f50>',
                                                           'x': 5,
                                                           'y': 5}},
                                                 {'abs_path': '/Users/victorng/dev/metlog-raven/metlog_raven/tests/test_metlog.py',
                                                  'context_line': '        return a + b + c / (a - b)',
                                                  'filename': 'tests/test_metlog.py',
                                                  'function': 'exception_call2',
                                                  'lineno': 87,
                                                  'module': 'test_metlog',
                                                  'post_context': ['',
                                                                   '    def exception_call1(x, y):'],
                                                  'pre_context': ["    client = client_from_text_config(cfg_txt, 'metlog')",
                                                                  '',
                                                                  '    def exception_call2(a, b, c):'],
                                                  'vars': {'a': 5,
                                                           'b': 5,
                                                           'c': 42}}]},
     'server_name': 'Victors-MacBook-Air.local',
     'site': None,
     'time_spent': None,
     'timestamp': '2012-05-08T15:08:38.657850Z'}

Raven allows extension of the data by adding new keys to the sentry
data through the 'extra' key, but this is not currently supported.
