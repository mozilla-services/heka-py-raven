=============
heka-py-raven
=============

.. image:: https://secure.travis-ci.org/mozilla-services/heka-py-raven.png

heka-py-raven is a plugin extension for `heka-py
<http://github.com/mozilla-services/heka-py>`.  heka-py-raven
provides logging extensions to capture stacktraces and some frame
information such as local variables to faciliate debugging.

The plugin acts as a thin wrapper around the Raven
<https://github.com/dcramer/raven> library for Sentry.

More information about how Mozilla Services is using heka (including what is
being used for a router and what endpoints are in use / planning to be used)
can be found on the `Read The Docs page 
<https://heka-docs.readthedocs.org>`_.

This version of heka-py-raven is compatible with version 3 of the
Sentry protocol.  This should make it compatible with Sentry 5.1->5.4
and Raven clients upto, but not including Raven 3.5.

To install heka-py-raven use::

    pip install heka-py-rave[protocol_v3]
