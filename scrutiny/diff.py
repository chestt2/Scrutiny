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


from operator import attrgetter
import os.path

def cleanUp(filename):
    """Cleans up a file removing unwanted attributes.
    Removes '\r's and extra newline characters. Necessary so line numbers
    match up with fingerprints when highlighting is being done.
    """
    
    with open(filename, 'rb') as fin:
        data = fin.read()
    while data.count(b'\r'):
        idx = data.index(b'\r')
        data = data[:idx] + data[idx + 1:]
    while data.startswith(b'\n'):
        data = data[1:]
    while data.endswith(b'\n\n'):
        data = data[:-1]
    if not data.endswith(b'\n'):
        data += b'\n'
    fin.close()
    return data.decode()

def overlap(a, b):
    """Returns true if two fignerprints overlap"""
    if a.eline < b.sline:
        return False
    elif a.eline > b.sline:
        return True
    if a.ecol >= b.scol:
        return True
    else:
        return False        

def highlightAssignment(fingerprints, output):
    """Highlights fingerprints and outputs into a table entry"""
    
    
    index = 0
    output.write('<td>')
    output.write('<p> Files by ' + fingerprints[0].auth + ':</p>\n')
    #Defines html code to start and end highlighting.
    startHighlight = '<SPAN style="BACKGROUND-COLOR: #ffff00">'
    endHighlight = '</SPAN>'

    #wWhile fingerpritns remain.
    while index < len(fingerprints):
        
        filename = fingerprints[index].loc
        data = cleanUp(filename) #process the file.
        output.write('<p>' + fingerprints[index].loc + ':</p>\n')
        line = 0
        col = 0
        output.write('<pre>\n')
        #Go through data one letter at a time.
        for letter in data:
        
            #If its the start of a fingerprint commence highlighting.
            if(index < len(fingerprints) and
               line == fingerprints[index].sline and
               col == fingerprints[index].scol and
               filename == fingerprints[index].loc):
                output.write(startHighlight)
            #If its the end of highlighing for a fingerprint.
            if(index < len(fingerprints) and 
               line == fingerprints[index].eline and
               col == fingerprints[index].ecol and
               filename == fingerprints[index].loc):
                index += 1 #Increment the index.
                #If the fingerprints overlap, don't end highlighting
                if(index < len(fingerprints) and 
                   overlap(fingerprints[index-1],fingerprints[index])):
                    pass
                else:
                    output.write(endHighlight)
            if(index < len(fingerprints) and (fingerprints[index].sline - line < 5 or
                (index > 0 and line - fingerprints[index-1].eline < 5))):
                if letter == '<':
                    output.write("&lt;")
                elif letter == '<':
                    output.write("&gt;")
                elif letter == '&':
                    output.write("&amp;")
                elif letter == '\"':
                    output.write("&quot;")
                else:
                    output.write(letter)
            col += 1
            #If its now a new line, adjust counters accordingly.
            if letter == '\n':
                line += 1
                col = 0
                
        output.write('</pre>')

    output.write('</td>')

    

def postProcess(assignment, matches, acount, mcount, PATH):
    
    #Sort the fingerprints so processing can be fficient.
    assignment.sort( key=attrgetter('loc', 'sline', 'scol'))
    matches.sort( key=attrgetter('loc', 'sline', 'scol'))
    percent = (float(mcount) / float(acount) )* 100
    #Output file.
    saveas = assignment[0].auth + "vs" + matches[0].auth + '.html'
    output = open(os.path.join(PATH, saveas), 'w')

    output.write('<html>\n<body>\n')
    output.write('<p> Significant similarities were found between author ' + assignment[0].auth + 'and author '
                                                                          + matches[0].auth + '</p>')
    output.write('<p> Out of ' + assignment[0].auth + '\'s unique ' + str(acount) + ' fingerprints, ' 
                  + str(mcount) + ' were found in ' + matches[0].auth + ' (' + str(percent) + '%) </p>')   
    output.write('<table width="100%">\n<tr valign="top">\n')
    highlightAssignment(assignment, output)
    highlightAssignment(matches, output)
    output.close()    

