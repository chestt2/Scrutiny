# Copyright (c) 2010, Robert Escriva
# Copyright (c) 2011, Thomas Chestna
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of Scrutiny nor the names of its contributors may be
#       used to endorse or promote products derived from this software without
#       specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.


'''Turn source code into a stream of tokens.
'''


from collections import namedtuple

import pygments.token
from pygments.lexers import get_lexer_by_name


CodeBit = namedtuple('CodeBit', 'type, string line column')


def tokenize(lang, data, comments=False, endlines=True, whitespace=False, text=True):
    line = 0
    oldline = 0
    col = 0
    oldcol = 0
    remain = data.decode()
    lexer = get_lexer_by_name(lang)
    for tok, string in lexer.get_tokens(data):
        # Somewhat wasteful, but I'm not sure if the lexer will ever skip
        # characters.
        assert(remain[:remain.index(string)] == '')
        # I assume no token ever contains more than one newline.
        #assert(string.count('\n') < 2)
        remain = remain[remain.index(string) + len(string):]
        oldline = line
        line += string.count('\n')
        oldcol = col
        if '\n' in string:
            _, rhs = string.rsplit('\n', 1)
            col = len(rhs)
        else:
            col += len(string)

        # Skip comments
        if not comments and (tok == pygments.token.Comment or
                             tok in pygments.token.Comment.subtypes):
            continue
        # Skip endlines
        if not endlines and tok == pygments.token.Text \
                        and '\n' in string:
            continue
        # Skip whitespace
        if not whitespace and tok == pygments.token.Text \
                          and string.strip() == '':
            continue
        # Skip text (not whitespace)
        if not text and tok == pygments.token.Text \
                    and string.strip() != '':
            continue
        yield CodeBit(tok, string, oldline, oldcol)


def main(argv):
    import os
    from optparse import OptionParser
    from scrutiny.util import add_common_options

    parser = OptionParser()
    add_common_options(parser)
    (options, args) = parser.parse_args(argv)

    if len(args) != 1:
#        print("Please specify exactly one input file.", file=sys.stderr)
        sys.exit(os.EX_USAGE)

    with open(args[0], 'rb') as fin:
        data = fin.read()
    for codebit in tokenize(options.language, data, options.comments,
                                                    options.endlines,
                                                    options.whitespace,
                                                    options.text):
        print(codebit)


if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
