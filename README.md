gpsd-ais-viewer
===============

Command-line viewer for AIS data through GPSD.


This program just connects to a GPSD daemon, parses the response assuming they're AIS messages, aggregates them and shows them in a text-mode table.

The main target of this software is being able to see what's going on in an AIS receiver in text-mode (by SSHing, etc). It offers no functionality beyond that.

Updates to the user interface only happen when a vessel currently in view changes, making it useful for monitoring AIS streams with thousands of vessels.

The user interface depends on the python-urwid library.



Supports the following command-line options:

    --host (hostname)   Name (or IP address) of the computer running gpsd, default localhost
    --port (port)       TCP port GPSD runs at, default 2947
    --scaled (true|false)   If true, apply scaling factors. Headings will be in degrees instead of tenths of a degree, latitude-longitude wll be in degrees instead of millionths of a degree, speed will be in knots instead of deciknots, etc.




