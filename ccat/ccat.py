#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import json

from pygments.lexers.data import JsonLexer
from tabulate import tabulate
import codecs

try:
    from pygments import highlight
    from pygments.lexers import (get_lexer_by_name, get_lexer_for_filename, get_lexer_for_mimetype, guess_lexer)
    from pygments.formatters import TerminalFormatter
except (ValueError, ImportError) as e:
    raise Exception('You may need to run ccat from the root directory (which includes README.md)', e)

try:
    from .config import Configuration
except (ValueError, ImportError) as e:
    raise Exception('You may need to run ccat from the root directory (which includes README.md)', e)


import sys, os
from .util.color import Color


class ColorCat(object):

    def main(self):
        ''' Either performs action based on arguments, or starts attack scanning '''
        Configuration.initialize()

        self.run()

    def run(self):

        try:

            fs = os.path.getsize(Configuration.filename)
            if fs > (1024 * 1024 * 1024):
                Color.pl("\n{!} {R}Error: File is to big. The maxim supported file size is 1GB{W}")
                sys.exit(2)

            try:
                lexer = get_lexer_for_filename(Configuration.filename)
            except:
                lexer = None

            formatter = TerminalFormatter(linenos=False)

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

                data = data.replace('\t', '  ')

                data = highlight(
                    code=data,
                    lexer=lexer,
                    formatter=formatter).strip('\r\n')

                if Configuration.simple:
                    print(data)
                elif Configuration.no_tab:
                    ldata = data.split('\n')
                    mc = len(f'{len(ldata)}') + 2

                    data = [Color.s(' {W}{O}{D}%s{GR}:{W}  ' % i).rjust(mc) + l for i, l in enumerate(ldata)]

                    print('\n'.join(data))
                else:
                    ldata = data.split('\n')
                    mc = len(f'{len(ldata)}') + 2

                    header = ['', 'File: %s' % Configuration.filename]
                    data = [(Color.s(' {W}{O}{D}%s{W} ' % i).rjust(mc), l) for i, l in enumerate(ldata)]

                    print(tabulate(data, header, tablefmt='rounded_outline'))

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
