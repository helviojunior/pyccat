#!/usr/bin/python3
# -*- coding: UTF-8 -*-
from argparse import _ArgumentGroup, Namespace
from .util.color import Color

import argparse, sys, os


class Arguments(object):
    ''' Holds arguments used by the ccat '''
    modules = {}
    verbose = False
    args = None

    def __init__(self):
        self.verbose = any(['-v' in word for word in sys.argv])
        self.args = self.get_arguments()

    def _verbose(self, msg):
        if self.verbose:
            Color.pl(msg)

    def get_arguments(self) -> Namespace:
        ''' Returns parser.args() containing all program arguments '''

        parser = argparse.ArgumentParser(
            usage=argparse.SUPPRESS,
            prog="ccat",
            add_help=False,
            formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=80, width=180))

        parser.add_argument('filename',
                            action='store',
                            metavar='[filename]',
                            type=str,
                            help=Color.s('Filename'))

        flags = parser.add_argument_group('Options')
        self._add_flags_args(flags)

        return parser.parse_args()

    def _add_flags_args(self, flags: _ArgumentGroup):
        flags.add_argument('-s', '--simple',
                           action='store_true',
                           default=False,
                           dest=f'simple',
                           help=Color.s('just colorize the file content'))

        flags.add_argument('-nt', '--no-tabulated',
                           action='store_true',
                           default=False,
                           dest=f'no_tab',
                           help=Color.s('do not show tab'))

        flags.add_argument('--style',
                           action='store',
                           metavar='[style name]',
                           type=str,
                           default='gruvbox-dark',
                           dest=f'style',
                           help=Color.s('pygments lib style name. (default: {G}gruvbox-dark{W}). See more at: https://pygments.org/styles/'))

        flags.add_argument('-l', '--lines',
                           action='store',
                           metavar='[filter]',
                           type=str,
                           default='',
                           dest=f'line_filter',
                           help=Color.s('return only selected lines ({W}{D}ex1:{G} 5:13 {W}{D}or ex2: {G}50: {W}{D}or ex3: {G}:100{W})'))

        flags.add_argument('-hl', '--highlight-lines',
                           action='store',
                           metavar='[filter]',
                           type=str,
                           default='',
                           dest=f'highlight_line_filter',
                           help=Color.s('highlight only selected lines ({W}{D}ex1:{W}{G} 5:13 {W}{D}or ex2: {W}{G}50: {W}{D}or ex3: {W}{G}:100{W})'))

        flags.add_argument('--output-img',
                           action='store',
                           metavar='[filename]',
                           type=str,
                           dest=f'out_file',
                           help=Color.s('image output file.'))

        flags.add_argument('-h', '--help',
                           action='help',
                           help=Color.s('show help message and exit'))

        flags.add_argument('-v',
                           action='count',
                           default=0,
                           help=Color.s(
                               'Specify verbosity level (default: {G}0{W}). Example: {G}-v{W}, {G}-vv{W}, {G}-vvv{W}'
                           ))

        flags.add_argument('--version',
                           action='store_true',
                           default=False,
                           dest=f'version',
                           help=Color.s('show current version'))
