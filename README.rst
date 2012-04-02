============
metlog-raven
============

metlog-raven is a plugin extension for `Metlog 
<http://github.com/mozilla-services/metlog-py>`.  metlog-raven
provides logging extensions to capture stacktraces and some frame
information such as local variables to faciliate debugging.

The plugin acts as a thin wrapper around the Raven
<https://github.com/dcramer/raven> library for Sentry.

More information about how Mozilla Services is using Metlog (including what is
being used for a router and what endpoints are in use / planning to be used)
can be found on the relevant `spec page
<https://wiki.mozilla.org/Services/Sagrada/Metlog>`_.
