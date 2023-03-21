#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import errno
import os, sys
from pathlib import Path

from .util.logger import Logger
from .__meta__ import __version__

try:
    from pygments.styles import get_style_by_name
except (ValueError, ImportError) as e:
    Logger.pl('{!} {R}Error: library {O}pygments{R} not found{W}\n     Install with {O}pip3 install Pygments{W} command.')
    sys.exit(3)

_FORMATS = ['jpg', 'jpeg', 'png']


class Configuration(object):
    ''' Stores configuration variables and functions for Tfileindexer. '''
    version = '0.0.0'
    name = ""

    initialized = False # Flag indicating config has been initialized
    verbose = 0
    filename = None
    cmd_line = ''
    simple = False
    no_tab = False
    style = None
    lines = []
    highlight_lines = []
    out_file = None
    format = ''

    @staticmethod
    def initialize():
        '''
            Sets up default initial configuration values.
            Also sets config values based on command-line arguments.
        '''

        Configuration.version = str(__version__)
        Configuration.name = "CCat"

        # Only initialize this class once
        if Configuration.initialized:
            return

        Configuration.initialized = True

        Configuration.verbose = 0 # Verbosity level.
        Configuration.print_stack_traces = True

        # Overwrite config values with arguments (if defined)
        Configuration.load_from_arguments()

    @staticmethod
    def count_file_lines(filename: str):
        def _count_generator(reader):
            b = reader(1024 * 1024)
            while b:
                yield b
                b = reader(1024 * 1024)

        with open(filename, 'rb') as fp:
            c_generator = _count_generator(fp.raw.read)
            # count each \n
            count = sum(buffer.count(b'\n') for buffer in c_generator)
            return count + 1

    def load_from_arguments():
        ''' Sets configuration values based on Argument.args object '''
        from .args import Arguments

        if any(['--version' in word for word in sys.argv]):
            Logger.pl(f' {Configuration.name} v{Configuration.version}\n')
            sys.exit(0)

        args = Arguments()

        a1 = sys.argv
        a1[0] = 'ccat'
        for a in a1:
            Configuration.cmd_line += "%s " % a

        Configuration.verbose = args.args.v
        Configuration.filename = args.args.filename

        if Configuration.filename is None or Configuration.filename.strip() == '':
            Logger.pl('{!} {R}error: filename is invalid {O}%s{R} {W}\r\n' % (
                args.args.config_file))
            exit(1)

        if not os.path.isfile(Configuration.filename):
            Logger.pl('{!} {R}error: filename does not exists {O}%s{R} {W}\r\n' % (
                Configuration.filename))
            exit(1)

        try:
            with open(Configuration.filename, 'r') as f:
                # file opened for writing. write to it here
                pass
        except IOError as x:
            if x.errno == errno.EACCES:
                Logger.pl('{!} {R}Error: could not open file {O}permission denied{R}{W}\r\n')
                sys.exit(1)
            elif x.errno == errno.EISDIR:
                Logger.pl('{!} {R}Error: could not open file {O}it is an directory{R}{W}\r\n')
                sys.exit(1)
            else:
                Logger.pl('{!} {R}Error: could not openfile {W}\r\n')
                sys.exit(1)

        fs = os.path.getsize(Configuration.filename)
        if fs > (1024 * 1024 * 100):
            Logger.pl("\n{!} {R}Error: File is to big. The maxim supported file size is 500MB{W}")
            sys.exit(2)

        lc = Configuration.count_file_lines(Configuration.filename)
        if lc > 1000000:
            Logger.pl("\n{!} {R}Error: File is to big. The maxim supported file lines size is 1.000.000{W}")
            sys.exit(2)

        Configuration.simple = args.args.simple
        Configuration.no_tab = args.args.no_tab

        try:
            Configuration.style = get_style_by_name(args.args.style)
        except Exception as e:
            Logger.pl('{!} {R}Error selecting style {O}%s{R}: {G}%s{W}\n     {W}{D}Check available styles at https://pygments.org/styles/{W}' % (args.args.style, str(e)), out=sys.stderr)
            sys.exit(1)

        if args.args.line_filter != '':
            filter_list = args.args.line_filter.split(",")
            for filter in filter_list:
                filter = filter.strip()
                if ':' in filter:
                    (i_start, i_end) = filter.split(":")
                    end = 0
                    start = 0
                    try:
                        start = int(f'0{i_start}')
                    except:
                        Logger.pl(
                            '{!} {R}error: could not convert {O}%s{R} from {O}%s{R} to an integer value {W}\r\n' % (
                                i_start, filter))
                        sys.exit(1)

                    try:
                        end = int(f'0{i_end}')
                    except:
                        Logger.pl(
                            '{!} {R}error: could not convert {O}%s{R} from {O}%s{R} to an integer value {W}\r\n' % (
                                i_end, filter))
                        sys.exit(1)

                    Configuration.lines += [(start, end)]

            Configuration.lines.sort(key=lambda x: x[0])

        if args.args.highlight_line_filter != '':
            filter_list = args.args.highlight_line_filter.split(",")
            for filter in filter_list:
                filter = filter.strip()
                if ':' in filter:
                    (i_start, i_end) = filter.split(":")
                    end = 0
                    start = 0
                    try:
                        start = int(f'0{i_start}')
                    except:
                        Logger.pl(
                            '{!} {R}error: could not convert {O}%s{R} from {O}%s{R} to an integer value {W}\r\n' % (
                                i_start, filter))
                        sys.exit(1)

                    try:
                        end = int(f'0{i_end}')
                    except:
                        Logger.pl(
                            '{!} {R}error: could not convert {O}%s{R} from {O}%s{R} to an integer value {W}\r\n' % (
                                i_end, filter))
                        sys.exit(1)

                    Configuration.highlight_lines += [(start, end)]

            Configuration.highlight_lines.sort(key=lambda x: x[0])

        if args.args.out_file is not None and args.args.out_file.strip() != '':

            if os.path.isdir(args.args.out_file):
                Logger.pl('{!} {R}error: invalid output filename {O}%s{R} {W}\r\n' % (
                    args.args.out_file))
                exit(1)

            Configuration.out_file = args.args.out_file
            fmt = Path(Configuration.out_file).suffix.strip('. ').lower()

            if fmt is None or fmt not in _FORMATS:
                Logger.pl('{!} {R}error: invalid image format {O}%s{R}. Supported formats: {G}%s{W}\r\n' % (
                    fmt, ', '.join(_FORMATS)))
                exit(1)

            Configuration.format = fmt.lower()
            if Configuration.format == 'jpg':
                Configuration.format = 'jpeg'
