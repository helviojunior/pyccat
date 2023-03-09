#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import errno
import os, sys
from .util.logger import Logger
from .__meta__ import __version__


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

    @staticmethod
    def initialize():
        '''
            Sets up default initial configuration values.
            Also sets config values based on command-line arguments.
        '''

        Configuration.version = str(__version__)
        Configuration.name = str(__name__)

        # Only initialize this class once
        if Configuration.initialized:
            return

        Configuration.initialized = True

        Configuration.verbose = 0 # Verbosity level.
        Configuration.print_stack_traces = True

        # Overwrite config values with arguments (if defined)
        Configuration.load_from_arguments()


    @staticmethod
    def load_from_arguments():
        ''' Sets configuration values based on Argument.args object '''
        from .args import Arguments

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
                args.args.config_file))
            exit(1)

        try:
            with open(Configuration.filename, 'r') as f:
                # file opened for writing. write to it here
                pass
        except IOError as x:
            if x.errno == errno.EACCES:
                Logger.pl('{!} {R}error: could not open file {O}permission denied{R}{W}\r\n')
                sys.exit(1)
            elif x.errno == errno.EISDIR:
                Logger.pl('{!} {R}error: could not open file {O}it is an directory{R}{W}\r\n')
                sys.exit(1)
            else:
                Logger.pl('{!} {R}error: could not openfile {W}\r\n')
                sys.exit(1)

        Configuration.simple = args.args.simple
        Configuration.no_tab = args.args.no_tab
