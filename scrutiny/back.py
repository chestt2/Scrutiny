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


import os
import os.path
import sys
from scrutiny.examine import Entry
from scrutiny.examine import examine
from scrutiny.util import createOrAppend

def processFolder(path, merge, auth, options):
    
    """Returns fingerprints of all files found in folder
    Runs recursively on all folders found there of. Adds all fingerprints to
    the dictionary its passed."""
    
    #Path juggling.
    current = os.getcwd()
    os.chdir(path)
    targets = os.listdir(".")

    for entry in targets:
        if os.path.isdir(entry): #If folder, recurse.
            processFolder(entry, merge, auth, options)
        else:
            temp = examine(entry, options)
            for x in temp: #Add to dictionary.
                entry = Entry(x.hash, x.sline, x.scol, x.eline,
                              x.ecol, auth, os.path.abspath(entry))
                createOrAppend(merge, x.hash, entry) 

    os.chdir(current)
                                        

def processBack(path, merge, options):

    """Goes through a folder processing all student submissions.
    Should target a folder where a submission was previously extracted to.
    Adds all fingerprints it gets to the dictionary it is passed in."""

    if not os.path.isdir(path): #check for valid path
        print("Error: Bad path to back assignment.", file=sys.stderr)
        sys.exit(os.EX_USAGE)
    #path juggling
    current = os.getcwd()
    os.chdir(path)
    contents = os.listdir(path)

    #Gather fingerprints for each student folder.
    for student in contents:
        if os.path.isdir(student):
            author = os.path.split(student)[1]
            processFolder(student, merge, author, options)

    os.chdir(current)

def processBackAll(path, merge, options):

    """Process a folder of preveios submissions. 
    Each folder contained should contain folders of students submissions. Each
    will be processed and their fingerprints added to merge, the dictionary
    passed in."""

    if not os.path.isdir(path): #Check for bath paths.
        print("Error: Bad path to back assignments.", file=sys.stderr)
        sys.exit(os.EX_USAGE)

    current = os.getcwd()
    os.chdir(path)

    targets = os.listdir(path)
    for backAssign in targets:
        processBack(os.path.join(path, backAssign), merge, options)

