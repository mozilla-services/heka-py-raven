==========
heka-raven
==========

.. image:: https://secure.travis-ci.org/mozilla-services/heka-raven.png

heka-raven is a plugin extension for `heka
<http://github.com/mozilla-services/heka-py>`.  heka-raven
provides logging extensions to capture stacktraces and some frame
information such as local variables to faciliate debugging.

The plugin acts as a thin wrapper around the Raven
<https://github.com/dcramer/raven> library for Sentry.

More information about how Mozilla Services is using heka (including what is
being used for a router and what endpoints are in use / planning to be used)
can be found on the `Read The Docs page 
<https://heka-docs.readthedocs.org>`_.

This version of heka-raven must be used with :

  * Raven client version 3.1.16
  * Sentry server 5.4.2

Other versions may work, but they have not been tested.
