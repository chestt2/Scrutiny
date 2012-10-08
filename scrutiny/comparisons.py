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


from scrutiny.diff import postProcess
from scrutiny.db import getTableNames
from scrutiny.examine import Entry
from scrutiny.back import processBack
from scrutiny.back import processBackAll
from scrutiny.util import createOrAppend

def buildMaster(gathered):
    master = {}
    #Put all the fingerprints into a single dictionary
    for assignment in gathered:
        for element in assignment.values():
            for entry in element:
                createOrAppend(master, entry.hash, entry)

    return master
    
def runCompares(gathered, master, iprints, options):

    #Iterate through assignments to perform comparisons
    for assignment in gathered:
        matches = {}
        
        #Calculate the total number of fingerprints for later statistics
        fingerprints = sum(map(len, assignment.values()))
            
        #Run a comparison of the file to the other assignments submitted.
        compareAll(assignment, master, matches)


        #Run an assignment against the database if needed.
        if options.vsdb:
            vsDB(assignment, matches, options.db, options.language)

        if options.back or options.backall:
            old = {}
            if options.back:
                processBack(options.back, old, options)
            else:
                processBackAll(options.backall, old, options)

            for item in iprints:
                if item in old:
                    old.pop(item)
            compareAll(assignment, old, matches)

        best = [ None, 0 ]
        #Look if any author has suspicious similarities.

        #TODO: Make this more clear. Function?
        for author in matches.keys(): 
            if len(matches[author]) > (1/4) * fingerprints:
                if len(matches[author]) > best[1]:
                    best[0], best[1] = author, len(matches[author])

        if best[0]: #If there are similarities.
            intersect = []
            old_hash = None 
            #Get the fingerprints in assignment that it shares with the match
            unique = 0
#            old = None
#            for x in matches[best[0]]:
#                if x.hash != old:
#                    unique += 1
#                    old = x.hash
            unique = len(set([x.hash for x in matches[best[0]]]))
            for element in matches[best[0]]:
                if element.hash != old_hash:
                    old_hash = element.hash
                    row = assignment[element.hash]
                    for item in row:
                        intersect.append(item)
            #Highlight the similarities.
            postProcess(intersect, matches[best[0]], len(assignment.keys()), 
                        unique, options.path)

	
def compareAll(assignment, master, matches):
    
    #Calculates inersection between assignments.

    for key in assignment.keys():
        if key not in master:
            continue
        data = master[key]
        #Check for fingerprints with same hash in the master.
        for entry in data:
        #If there is a match and its not by the same author, add it.
            if entry.auth != assignment[key][0].auth:               
                createOrAppend(matches, entry.auth, entry)

       

def vsDB(assignment, matches, db_path, lang):

    import sqlite3
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    lang, auth = getTableNames(lang)

    query_string = 'select hash, sline, scol, eline, ecol, auth, path'
    query_string += 'from ' + lang + ', ' + auth + ' where auth<>? and '
    query_string += 'hash=? and ' + lang + '.fileid=' + auth + '.rowid'
#    queryString = 'select hash, sline, scol, eline, ecol, auth, path from ' + lang + ' where auth<>? and hash=?'

		
    for key in assignment.keys():
        target = (assignment[key][0].auth, key)
        for row in cur.execute(query_string, target):
            createOrAppend( matches, row['auth'], Entry(*row))
        
#        #fetches one at a time due to memory concerns about scaling.
#        hsh, sline, scol, eline, ecol, auth, path = c.fetchone()
#        while tmp != None:
            #tmp[5] refers to the auth. Matches get inserted.
#            entry = Entry(hsh, sline, scol, eline, ecol, auth, path)
#            createOrAppend( matches, tmp[5], entry)
#
#            tmp = c.fetchone()
            
            
