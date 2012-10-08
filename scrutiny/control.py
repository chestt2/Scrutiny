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


import zipfile
import tarfile
import sys
import os
from scrutiny.comparisons import runCompares
from scrutiny.comparisons import buildMaster
from scrutiny.db import addToDB
from scrutiny.db import removePath
from scrutiny.db import removeAuth
from scrutiny.extract import extractAll



def justAssignments(options, args):
    gathered = []

    gathered = extractAll(args[0], options.path, options)

    master = buildMaster(gathered)
    iprints = []
    if options.instructor:
        iprints = processAssignment(options.instructor, os.path.join(options.path, "Instructor_Code"), options)
            
        for item in iprints:
            if item in master:
                master.pop(item)

    if not options.skip:            
        runCompares(gathered, master, iprints, options)

    if options.add:
        addToDB(master, options.db, options.language)
    

def main(argv):

    from optparse import OptionParser
    cwd = os.getcwd()
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
    parser.add_option("-W", "--window", dest="window", default=5,
                       help="size of the winnowing window", metavar="W")
    parser.add_option("-t", action="store_true", dest="text", default=False,
                       help="consider text when tokenizing")
    parser.add_option("-i", dest="instructor", default=False,
                       help="instructor code to be omitted")
    parser.add_option("-p", "--path", dest="path", default=cwd,
                       help="set output destination", metavar="PATH")
    parser.add_option("-d", dest="db", default=False,
                       help="path to database")
    parser.add_option("-a", action="store_true", dest="add",
                       help="add to database")
    parser.add_option("-A", action="store_true", dest="vsdb",
                       help="run against database")
    parser.add_option("-b", dest="back", default=False,
                       help="run against folder of back asssignments.")
    parser.add_option("-B", dest="backall", default=False,
                       help="run against folder of folders of back assignments.")
    parser.add_option("-S", action="store_true", dest="skip", default=False,
                       help="skip all comparisons")
    parser.add_option("--DP", dest="delpath", default=False,
                       help='delete entries in database whose path is below given')
    parser.add_option("--DA", dest="delauth", default=False,
                       help='delete entries in database by given author')

    (options, args) = parser.parse_args(argv)

    if(options.skip and (options.delpath or options.delauth)):
        if options.delpath:
            removePath(options.language, options.db, options.delpath)
        if options.delauth:
            removeAuth(options.language, options.db, options.delauth)
        sys.exit()
             
    if len(args) != 1:
        #print("Please specify exactly one input file.", file=sys.stderr)
        sys.exit(os.EX_USAGE)
            
    justAssignments(options, args)

if __name__ == '__main__':
    main(sys.argv[1:])

