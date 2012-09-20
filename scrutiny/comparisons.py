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
from scrutiny.db import getProperName
from scrutiny.examine import Entry
from scrutiny.back import processBack
from scrutiny.back import processBackAll

def buildMaster(gathered):
    master = {}
    #Put all the fingerprints into a single dictionary
    for assignment in gathered:
        data = assignment.values()
        for element in data:
            for entry in element:
                if entry.hash in master:
                    master[entry.hash].append(entry)
                else:
                    master[entry.hash] = [entry]

    return master
    
def runCompares(gathered, master, iprints, options):

    #Iterate through assignments to perform comparisons
    for assignment in gathered:
        matches = {}
        
        fingerprints = 0
        keys = assignment.keys()
        #Calculate the total number of fingerprints for later statistics
        for key in keys:
            fingerprints += len(assignment[key])
            
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


        
        authors = matches.keys()
        best = [ None, 0 ]
        #Look if any author has suspicious similarities.
        for author in authors: 
            if len(matches[author]) > (1/4) * fingerprints:
                if len(matches[author]) > best[1]:
                    best[0], best[1] = author, len(matches[author])

        if best[0]: #If there are similarities.
            intersect = []
            oldHash = None 
            #Get the fingerprints in assignment that it shares with the match
            unique = 0
            old = None
            for x in matches[best[0]]:
                if x.hash != old:
                    unique += 1
                    old = x.hash
            for element in matches[best[0]]:
                if element.hash != oldHash:
                    oldHash = element.hash
                    row = assignment[element.hash]
                    for item in row:
                        intersect.append(item)
            #Highlight the similarities.
            postProcess(intersect, matches[best[0]],len(keys), unique, options.path)

		
	
def compareAll(assignment, master, matches):
    
    

    #Calculates inersection between assignments.
   keys = assignment.keys()

   for key in keys:
       if key not in master:
           continue
       data = master[key]
       #Check for fingerprints with same hash in the master.
       for entry in data:
           #If there is a match and its not by the same author, add it.
           if entry.auth != assignment[key][0].auth:               
               if entry.auth in matches:
                   matches[entry.auth].append(entry)
               else:
                   matches[entry.auth] = [entry]

       

def vsDB(assignment, matches, db_path, lang):


    import sqlite3
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    keys = assignment.keys()
    lang = getProperName(lang)

    queryString = ('select * from ' + lang + ' where auth<>? and hash=?')

		
    for key in keys:
        t = (assignment[key][0].auth, key)
        c.execute(queryString, t)
        
        #fetches one at a time due to memory concerns about scaling.
        tmp = c.fetchone()
        while tmp != None:
            #tmp[5] refers to the auth. Matches get inserted.
            if tmp[5] in matches:
                matches[tmp[5]].append(Entry(tmp[0], tmp[1], tmp[2],
                                             tmp[3], tmp[4], tmp[5], tmp[6]))
            else:
                matches[tmp[5]] = [Entry(tmp[0], tmp[1], tmp[2], tmp[3],
                                        tmp[4], tmp[5], tmp[6])]
            tmp = c.fetchone()
            
            

