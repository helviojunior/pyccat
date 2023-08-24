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
                    data = data.decode('utf-8-sig')
                except:
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
                except Exception as e:
                    Color.pl("\n{!} {R}Error: {O}%s" % str(e))
                    if Configuration.verbose > 3 or True:
                        Color.pl('\n{!} {O}Full stack trace below')
                        from traceback import format_exc
                        Color.p('\n{!}    ')
                        err = format_exc().strip()
                        err = err.replace('\n', '\n{W}{!} {W}   ')
                        err = err.replace('  File', '{W}{D}File')
                        err = err.replace('  Exception: ', '{R}Exception: {O}')
                        Color.pl(err)
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
                    c1_len = len(ColorCat.escape_ansi(dot_line))
                    size = ColorCat.get_columns()

                    data = [
                        (
                                Color.s(' {W}%s{GR}:{W}  ' % ColorCat.format_line_number(i + 1, mc)) +
                                ColorCat.format_line(l, c1_len, size)
                        )
                        if ColorCat.is_valid(i + 1) else dot_line
                        for i, l in enumerate(ldata)
                        if ColorCat.is_valid(i + 1) or ColorCat.is_dot(i + 1)
                    ]

                    if not ColorCat.is_valid(len(ldata)):
                        data += [dot_line]

                    text = Color.s(' \033[38;5;52m=\033[38;5;88m=\033[38;5;124m=\033[38;5;160m=\033[38;5;196m> ' + '{W}{O}File: {G}%s{W}\n' % Configuration.filename)

                    text += ''.join([
                        '%s-' % c for k, c in sorted(Color.gray_scale.items(), key=lambda x: x[0], reverse=True)
                    ]) + Color.s('{W}\n')

                    self.output(text + '\n'.join(data))
                else:
                    mc = len(f'{len(ldata)}')
                    dot_line = (Color.s('  {W}%s{W} ' % ColorCat.format_line_number('...', mc)), '')
                    size = ColorCat.get_columns()
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

    @staticmethod
    def get_columns():
        if Configuration.out_file is not None:
            return 120

        try:
            size = os.get_terminal_size().columns
        except:
            size = 200

        return size


    @staticmethod
    def format_line(text: str, number_line: int, max_cols: int = 200) -> str:
        tab = 2
        if max_cols < 120:
            max_cols = 120
        if len(ColorCat.escape_ansi(text)) < max_cols:
            return text

        text = text.replace('\t', ' ' * tab)
        try:
            parts = []
            escaped_text = ColorCat.escape_ansi(text)
            diff = (len(escaped_text) - len(escaped_text.lstrip()))
            start = text.index(escaped_text.lstrip()[0]) - diff

            if start > 0:
                parts.append(text[0:start])

            pattern = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]')
            ansi_codes = [
                (m.start(), m.end())
                for m in pattern.finditer(text)
            ]

            c = max_cols
            o = start
            size = max_cols
            first_line = True
            while c <= len(text):
                p = text[o:c]
                while len(ColorCat.escape_ansi(p)) < size:
                    c += 1
                    p = text[o:c]
                    if o + c >= len(text):
                        break
                (idxs, idxe) = next((
                    a for a in ansi_codes
                    if a[0] <= c <= a[1]
                ), (None, None))
                if idxs is not None:
                    c = idxe
                p = text[o:c]
                if first_line:
                    size = max_cols - diff - tab
                    first_line = False
                else:
                    parts.append(' \n' + (' ' * (number_line + diff + tab)))
                o = c
                c += size - 4
                parts.append(p)

            if o < len(text):
                parts.append(' \n' + (' ' * (number_line + diff + tab)))
                parts.append(text[o:])

            return ''.join(parts)
        except:
            return text


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
