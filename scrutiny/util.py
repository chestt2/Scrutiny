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
def createOrAppend(container, key, el):
    if key in container:
        container[key].append(el)
        return
    container[key] = [el]
    
def normalizeFileLines(filename):
    """Cleans up a file removing unwanted newlines and carriage returns.
    Removes '\r's and extra newline characters. Necessary so analysis is consistent
    """

    with open(filename, 'rb') as fin:
        data = fin.read()
    #TODO: Would regex be quicker?
    while data.count(b'\r'):
        idx = data.index(b'\r')
        data = data[:idx] + data[idx + 1:]
    while data.startswith(b'\n'):
        data = data[1:]
    while data.endswith(b'\n\n'):
        data = data[:-1]
    if not data.endswith(b'\n'):
        data += b'\n'
    return data

def add_common_options(parser):
    parser.add_option("-l", "--language", dest="language", default="c",
                      help="tokenize using lexer for language", metavar="LANG")
    parser.add_option("-c", action="store_true", dest="comments", default=False,
                      help="consider comments when tokenizing")
    parser.add_option("-e", action="store_true", dest="endlines", default=False,
                      help="consider endlines when tokenizing")
    parser.add_option("-w", action="store_true", dest="whitespace",
                      default=False,
                      help="consider whitespace (not endlines) when tokenizing")
    parser.add_option("-t", action="store_true", dest="text", default=False,
                      help="consider text when tokenizing")
