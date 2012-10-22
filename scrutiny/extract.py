import multiprocessing
import os
import tarfile
import zipfile

from scrutiny.examine import Entry
from scrutiny.examine import examine
from scrutiny.util import createOrAppend

def extractFromArchive( filename, path ):
    if not os.path.isdir(path):
        os.mkdir(path)
    targets = None

    if tarfile.is_tarfile(filename):
        tar = tarfile.open(filename)
        tar.extractall(path)
        targets = tar.getnames()
    elif zipfile.is_zipfile(filename):
        zipped = zipfile.ZipFile(filename)
        zipped.extractall(path)
        targets = zipped.namelist()
    else:
        #print("Error: Unrecognized compression type", file=sys.std.err)
        sys.exit(os.EX_USAGE)
    return targets

def extractAll( archive, path, options):
    targets = extractFromArchive(archive, path)
    gathered = []
    current = os.getcwd()
    os.chdir(path)

    for filename in targets:
        extentionless = os.path.splitext(filename)[0]
        gathered.append(processAssignment(filename, os.path.join(path, extentionless), options))

    os.chdir(current)
    return gathered

def untup( val ):
    filename, path, options = val
    return processAssignment(filename, path, options)

def processAssignment(archive, path, options):
    targets = extractFromArchive(archive, path)
    author = os.path.split(path)[1]
    current = os.getcwd()
    os.chdir(path)
    master = {}
    for filename in targets:
        if os.path.isdir(os.path.join(path, filename)):
            pass
        else:
            temp = examine(filename, options)
            for tup in temp:
                entry = Entry(*tup, auth=author, loc=os.path.abspath(filename))
                createOrAppend(master, tup.hash, entry)
                             
    os.chdir(current)
    return master


def main(argv):
    from optparse import OptionParser
    from util import add_common_options

    parser = OptionParser()
    add_common_options(parser)
    parser.add_option("-s", "--size", dest="size", default=5,
                       help="size of each kgram", metavar="N")
    parser.add_option("-W", "--window", dest="window", default=5,
                       help="size of the winnowing window", metavar="W")
    (options, args) = parser.parse_args(argv)
    archive = args[0]
    path = args[1]
    processAssignment(archive, path, options)

if __name__ == '__main__':
    import sys
    main(sys.argv[1:])

