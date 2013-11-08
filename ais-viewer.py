#!/usr/bin/env python
"""Text-mode application to view data from AIS streams"""

# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE":
# <ivan@sanchezortega.es> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return.
# ----------------------------------------------------------------------------
#


import gps
import argparse
from collections import OrderedDict
import urwid
import threading


class aiswalker(urwid.SimpleFocusListWalker):
    """ListWalker-compatible list of AIS vessel data"""

    fields = [
        'mmsi',
         'imo',
         ##'ais_version',
         ##'class',
         'lat',
         'lon',
         'course',
         'heading',
         'speed',
         #'turn',
         #'epfd',
         #'accuracy',
         #'destination',
         #'eta',
         'callsign',
         ##'radio',
         #'status',
         #'maneuver',
         ##'reserved',
         ##'scaled',
         ##'second',
         #'shiptype',
         #'cs',
         ##'off_position',
         #'vendorid',
         'type',
         ##'dsc',
         ##'msg22',
         ##'repeat',
         #'draught',
         #'timestamp',
         ##'regional',
         #'raim',
         ##'band',
         #'aid_type',
         #'virtual_aid',
         #'to_port',
         #'to_bow',
         #'to_stern',
         #'to_starboard',
         'shipname',
         'name',
         ##'dte',
         ##'display',
         ##'device',
         ]

    def __init__(self):
        self.d = OrderedDict()
        self.mmsis = []
        #self._focus = 0

        self.emptyrecord = {}
        for i in aiswalker.fields:
            self.emptyrecord[i] = None

        urwid.SimpleFocusListWalker.__init__(self,[])


    def update(self,r):
        """Updates the internal dictionary given an AIS record.

        The AIS record must contain a "mmsi" item."""

        if 'mmsi' not in r:
            return false
        mmsi = r['mmsi']

        if not mmsi in self.d:
            self.d[mmsi] = dict(self.emptyrecord)   # Instantiate a new one, not refer to the existing one
            self.d = OrderedDict( sorted(self.d.items()) )    # Re-do the dict to keep mmsis sorted
            i = self.d.keys().index(mmsi)
            self.mmsis = sorted(self.d.keys())

            self.insert ( i, None )

        self.d[mmsi].update(r)

        columns = []
        for i in aiswalker.fields:
            columns.append( urwid.Text ( str( self.d[mmsi][i] ) ) )

        columns = urwid.Columns( columns, dividechars = 1 )

        i = self.d.keys().index(mmsi)
        self[ i ] = columns

    def get_header_cols(self):
        columns = []
        for i in aiswalker.fields:
            columns.append( urwid.Text ( str( i ) ) )

        return urwid.Columns( columns, dividechars = 1 )


class aislistener(threading.Thread):

    def __init__(self, walker, stream, view):
        threading.Thread.__init__(self)

        self.walker = walker
        self.stream = stream
        self.view   = view

    def run(self):
        count = 0

        for message in self.stream:
            if 'mmsi' in message:   # Skip control messages
                self.walker.update(message)
                count = count + 1

class aisviewer:

    palette = [
        ('header','dark cyan', 'dark blue', 'bold'),
        ('body','default', 'default'),
        ('foot','dark cyan', 'dark blue', 'bold'),
        ('key','light cyan', 'dark blue', 'underline'),
        ]

    footer_text = ('foot', [
        "AIS viewer    ",
        ('key', "Ctrl+C"), " quit",
        ])

    def __init__(self,stream,interval):
        self.stream = stream
        self.walker = aiswalker()
        self.interval = interval


    def refresh(self,_loop,_data):
        _loop.draw_screen()
        _loop.set_alarm_in(self.interval,self.refresh)

    def main(self):
        self.listbox = urwid.ListBox(self.walker)
        self.footer = urwid.AttrWrap(urwid.Text(self.footer_text),"foot")
        self.header = urwid.AttrWrap(self.walker.get_header_cols(),"header")
        self.view = urwid.Frame(urwid.AttrWrap(self.listbox, 'body'), footer=self.footer, header = self.header)

        self.listener = aislistener( self.walker, self.stream, self.view )
        self.listener.setDaemon(True)
        self.listener.start()

        self.loop = urwid.MainLoop(self.view, self.palette)

        self.loop.set_alarm_in(self.interval,self.refresh)
        self.loop.run()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Displays AIS data from GPSD.')
    parser.add_argument('--host', default="localhost",
                    help='Host running gpsd.')
    parser.add_argument('--port', default=2947, type=int,
                    help='Port gpsd is listening to. Defaults to 2947')
    parser.add_argument('--scaled', default=False, type=bool,
                        help='If set, data will be scaled to readable values. If not set (default), the raw numeric values will be shown.')
    parser.add_argument('--interval', default=2, type=int,
                        help='Update interval, in seconds. Defaults to 2.')
    args = parser.parse_args()

    # Load up gpsd connection
    g = gps.gps(host=args.host, port=args.port)

    gpsd_flags = gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE
    if args.scaled:
        gpsd_flags = gpsd_flags | gps.WATCH_SCALED

    g.stream(gpsd_flags)

    v = aisviewer(g, args.interval)
    v.main()


