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


import sys
from scrutiny.kgrams import kgrams
from scrutiny.tokenize import tokenize
from scrutiny.winnowing import Fingerprint
from scrutiny.winnowing import winnowing
from collections import namedtuple
from scrutiny.util import normalizeFileLines
Entry = namedtuple('Entry', 'hash sline scol eline ecol auth loc')

def examine(filename, options):
    fingerprints  = list()
    
    data = normalizeFileLines(filename)
    for fprint in winnowing(kgrams(tokenize(options.language, data,
                                                  options.comments,
                                                  options.endlines,
                                                  options.whitespace,
                                                  options.text),
                                                  int(options.size)),
                                                  int(options.window)):
        # Add all the fingerprints to a list and return it.
        fingerprints.append( fprint) 
    return fingerprints        





def main(argv):
    from optparse import OptionParser
    from scrutiny.util import add_common_options

    parser = OptionParser()
    add_common_options(parser)
    parser.add_option("-s", "--size", dest="size", default=5,
                      help="size of each kgram", metavar="N")
    parser.add_option("-W", "--window", dest="window", default=5,
                      help="size of the winnowing window", metavar="W")
    (options, args) = parser.parse_args(argv)

    if len(args) != 1:
        print("Expected one file")
    filename = args[0]
    print( len(examine(filename, options)) )

    
if __name__ == '__main__':
    main(sys.argv[1:])
       

