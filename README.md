Scrutiny simplifies the task of comparing source code for similarities.

In particular, scrutiny is designed to detect when small portions of code occur
in multiple files that are assumed to be independent.

INSTALLATION:
    Scrutiny is written in python3 and is not backwards compatible with python 2.x.
    Scrutiny requires a python library called pygments to run. http://pygments.org/download/
        Installing it should be as easy as 'easy_install-3 pygments'.
        Note: On some systems easy_install may be easy_install3, or easy_install-3.2. Just make sure its installing for python3.

USAGE:
    python3 -m scrutiny.control [options] [inputfile]

    OPTIONS:
        -h, --help                              displays a simple help message.
        -l Lang, --language=LANG                Specify the language of the input files.
                                                Defaults to C.
        -c                                      Consider comments when processing.
        -e                                      Consider endlines when processing.
        -w                                      Consider whitespace when processing.
        -t                                      Consider text when tokenizing.
        -s N, --size=N                          Set the size of each kgram.
                                                Defaults to 5.
        -W W, --window=W                        Set the size of the winnowing window. 
                                                Defaults to 5.
        -i INSTRUCTOR                           Instructor code file to be ommitted. 
        -p PATH, --path=PATH                    Set destination path when extracting files and output files.
        -d DB                                   Path to database to use.
        -a                                      Add the input files to the database.
        -A                                      Run input files gainst the database.
        -S                                      Skip all comparisons. Useful for just adding files to database.
