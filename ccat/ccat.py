#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import json
import re

from ansi2image.ansi2image import Ansi2Image
from pygments.formatters.terminal256 import Terminal256Formatter
from pygments.lexers.data import JsonLexer
from tabulate import _table_formats, tabulate, TableFormat, Line, DataRow
import codecs

try:
    from pygments import highlight
    from pygments.lexers import (get_lexer_by_name, get_lexer_for_filename, get_lexer_for_mimetype, guess_lexer)
    from pygments.formatters import TerminalFormatter
    from pygments.styles import get_style_by_name
except (ValueError, ImportError) as e:
    raise Exception('You may need to run ccat from the root directory (which includes README.md)', e)

try:
    from .config import Configuration
except (ValueError, ImportError) as e:
    raise Exception('You may need to run ccat from the root directory (which includes README.md)', e)


import sys, os
from .util.color import Color


class ColorCat(object):

    def __init__(self):
        _table_formats["ccat"] = TableFormat(
                lineabove=Line("", Color.s("{GR}─{W}"), Color.s("{GR}┬{W}"), ""),
                linebelowheader=Line("", Color.s("{GR}─{W}"), Color.s("{GR}┼{W}"), ""),
                linebetweenrows=None,
                linebelow=Line("", Color.s("{GR}─{W}"), Color.s("{GR}┴{W}"), ""),
                headerrow=DataRow("", Color.s("{GR}│{W}"), ""),
                datarow=DataRow("", Color.s("{GR}│{W}"), ""),
                padding=1,
                with_header_hide=None,
            )

    def main(self):
        ''' Either performs action based on arguments, or starts attack scanning '''
        Configuration.initialize()

        self.run()

    @staticmethod
    def is_valid(line):
        if len(Configuration.lines) == 0:
            return True

        return any([
            x for x in Configuration.lines
            if line >= x[0] and (x[1] == 0 or line <= x[1])
        ])

    @staticmethod
    def is_highlight(line):
        if len(Configuration.highlight_lines) == 0:
            return True

        return any([
            x for x in Configuration.highlight_lines
            if line >= x[0] and (x[1] == 0 or line <= x[1])
        ])
    @staticmethod
    def is_dot(line):
        if len(Configuration.lines) == 0:
            return False

        if ColorCat.is_valid(line):
            return False

        return any([
            x for x in Configuration.lines
            if x[0] != 0 and line == x[0] - 1
        ])

    @staticmethod
    def format_line_number(line, max_line):
        max_line = max_line if max_line > 3 else 3

        if str(line) == '...':
            return '{GR}%s' % (f'{line}'.rjust(max_line))
        else:
            return '{O}{D}%s' % (f'{line}'.rjust(max_line))

    @staticmethod
    def escape_ansi(line):
        #pattern = re.compile(r'\x1B\[\d+(;\d+){0,2}m')
        pattern = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]')
        return pattern.sub('', line)

    @classmethod
    def output(cls, text):
        print(text)
        if Configuration.out_file is not None:
            o = Ansi2Image(0, 0, font_name=Ansi2Image.get_default_font_name(), font_size=13)
            o.loads(text)
            o.calc_size()
            o.save_image(Configuration.out_file, format=Configuration.format)

    def run(self):

        try:

            try:
                lexer = get_lexer_for_filename(Configuration.filename)
            except:
                lexer = None

            formatter = Terminal256Formatter(linenos=False, style=Configuration.style)

            with open(Configuration.filename, 'rb') as f:
                data = f.read()

            if data is not None:
                if lexer is None:
                    try:
                        lexer = guess_lexer(data)
                    except:
                        lexer = get_lexer_by_name('text')

                # try to read
                try:
                    data = data.decode('utf-8')
                except:
                    data = data.decode('latin-1')

                if data.strip(' \r\n') == '':
                    Color.pl("\n{!} {R}Error: File is empty{W}")
                    sys.exit(2)

                #try parse json
                try:
                    tmp = json.loads(data)
                    data = json.dumps(tmp, sort_keys=False, indent=2)
                    data = data.strip('\r\n')
                    lexer = JsonLexer()
                except:
                    pass

                data = data.replace('\t', '  ').replace('\r', '')
                ldata = highlight(
                    code=data,
                    lexer=lexer,
                    formatter=formatter).replace('\t', '  ').strip('\n').split('\n')

                ldata = [
                    l
                    if ColorCat.is_highlight(i + 1) else Color.s('{GR}{D}%s{W}' % ColorCat.escape_ansi(l))
                    for i, l in enumerate(ldata)
                ]

                if Configuration.simple:
                    self.output('\n'.join(ldata))
                elif Configuration.no_tab:
                    mc = len(f'{len(ldata)}')
                    dot_line = Color.s('  {W}%s{W}  ' % ColorCat.format_line_number('...', mc))

                    data = [
                        (Color.s(' {W}%s{GR}:{W}  ' % ColorCat.format_line_number(i + 1, mc)) + l)
                        if ColorCat.is_valid(i + 1) else dot_line
                        for i, l in enumerate(ldata)
                        if ColorCat.is_valid(i + 1) or ColorCat.is_dot(i + 1)
                    ]

                    if not ColorCat.is_valid(len(ldata)):
                        data += [dot_line]

                    self.output('\n'.join(data))
                else:
                    mc = len(f'{len(ldata)}')
                    dot_line = (Color.s('  {W}%s{W} ' % ColorCat.format_line_number('...', mc)), '')
                    try:
                        size = os.get_terminal_size().columns
                    except:
                        size = 300
                    max_c2_size = size - 10 - mc

                    header = ['', 'File: %s' % Configuration.filename]
                    data = [
                        (Color.s(' {W}{O}{D}%s{W} ' % ColorCat.format_line_number(i + 1, mc)), l)
                        if ColorCat.is_valid(i + 1) else dot_line
                        for i, l in enumerate(ldata)
                        if ColorCat.is_valid(i + 1) or ColorCat.is_dot(i + 1)
                    ]

                    if not ColorCat.is_valid(len(ldata)):
                        data += [dot_line]

                    cols = {}

                    # Available only at v0.9.0 and upper
                    try:
                        from tabulate.version import __version_tuple__ as tabv
                        if tabv[0] > 0 and tabv[1] >= 9:
                            cols = dict(
                                maxcolwidths=[None, max_c2_size]
                            )
                    except:
                        pass

                    self.output(tabulate(data, header, tablefmt='ccat', **cols))

        except Exception as e:
            Color.pl("\n{!} {R}Error: {O}%s" % str(e))
            if Configuration.verbose > 0 or True:
                Color.pl('\n{!} {O}Full stack trace below')
                from traceback import format_exc
                Color.p('\n{!}    ')
                err = format_exc().strip()
                err = err.replace('\n', '\n{W}{!} {W}   ')
                err = err.replace('  File', '{W}{D}File')
                err = err.replace('  Exception: ', '{R}Exception: {O}')
                Color.pl(err)
        except KeyboardInterrupt as e:
            raise e

        print(' ')


def run():
    # Explicitly changing the stdout encoding format
    if sys.stdout.encoding is None:
        # Output is redirected to a file
        sys.stdout = codecs.getwriter('latin-1')(sys.stdout)

    o = ColorCat()

    try:
        o.main()

    except Exception as e:
        Color.pl('\n{!} {R}Error:{O} %s{W}' % str(e))

        if Configuration.verbose > 0 or True:
            Color.pl('\n{!} {O}Full stack trace below')
            from traceback import format_exc
            Color.p('\n{!}    ')
            err = format_exc().strip()
            err = err.replace('\n', '\n{W}{!} {W}   ')
            err = err.replace('  File', '{W}{D}File')
            err = err.replace('  Exception: ', '{R}Exception: {O}')
            Color.pl(err)

        Color.pl('\n{!} {R}Exiting{W}\n')

    except KeyboardInterrupt:
        Color.pl('\n{!} {O}interrupted, shutting down...{W}')

    sys.exit(0)
