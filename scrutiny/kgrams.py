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


'''Generate k-grams from the input.
'''


import itertools
import math
from collections import namedtuple

import pygments.token
from pygments.lexers import get_lexer_by_name
from pygments.token import STANDARD_TYPES

from scrutiny.tokenize import tokenize


KGRAM = namedtuple('KGRAM', 'identity sline scol eline ecol')


def _matches(tok, toktype):
    return tok == toktype or tok in toktype.subtypes


def token_prep(codebit):
    if '\n' in codebit.string:
        return 'ENDL'
    elif _matches(codebit.type, pygments.token.Keyword):
        return codebit.string
    elif _matches(codebit.type, pygments.token.Operator):
        return codebit.string
    elif _matches(codebit.type, pygments.token.Punctuation):
        return codebit.string
    elif _matches(codebit.type, pygments.token.Literal):
        return codebit.string
    elif _matches(codebit.type, pygments.token.Name):
        i = len(codebit.string)
        return STANDARD_TYPES[codebit.type] + str(int(math.log(i) / math.log(2)))
    else:
        return STANDARD_TYPES[codebit.type]


def kgrams(token_generator, length):
    gens = [itertools.islice(gen, i, None) for i, gen in
            enumerate(itertools.tee(token_generator, length))]
    for kgram in zip(*gens):
        first = kgram[0]
        last = kgram[-1]
        string = '-'.join([token_prep(k) for k in kgram])
        yield KGRAM(string, first.line, first.column, last.line, last.column + len(last.string) )


def main(argv):
    import os
    import sys
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option("-l", "--language", dest="language", default="c",
                      help="tokenize using lexer for language", metavar="LANG")
    parser.add_option("-s", "--size", dest="size", default=5,
                      help="size of each kgram", metavar="N")
    parser.add_option("-c", action="store_true", dest="comments", default=False,
                      help="consider comments when tokenizing")
    parser.add_option("-e", action="store_true", dest="endlines", default=False,
                      help="consider endlines when tokenizing")
    parser.add_option("-w", action="store_true", dest="whitespace", default=False,
                      help="consider whitespace when tokenizing")
    parser.add_option("-t", action="store_true", dest="text", default=False,
                      help="consider text when tokenizing")
    (options, args) = parser.parse_args(argv)

    if len(args) != 1:
        print("Please specify exactly one input file.", file=sys.stderr)
        sys.exit(os.EX_USAGE)

    with open(args[0], 'rb') as fin:
        data = fin.read()
    for kgram in kgrams(tokenize(options.language, data, options.comments,
                                                         options.endlines,
                                                         options.whitespace,
                                                         options.text),
                        int(options.size)):
        print(kgram)


if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
