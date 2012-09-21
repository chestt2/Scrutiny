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


import sqlite3
import sys
import re
from pygments.lexers import get_lexer_by_name
    

def getProperName(lang):
    
    lexer = get_lexer_by_name(lang)
    name = lexer.name
    
    #sqlite table names cannot contain symbols, so adjust.
    if name == "C++":
        name = "cpp"
    elif name == "C#":
        name = "csharp"
    else:
        #Check to make sure their aren't other symbols present.
        #TODO: if not all(map(str.isalnum, name))
        for char in name:
            if not char.isalnum():
                print("Error: Lexer name must be alphanumeric and start", 
                    " with a letter.", file=sys.stderr)
                sys.exit(1)
    #return the proper name.
    return name


def addToDB(master, path, lang):


    #TODO: Don't use try/except for control flow.
    conn = sqlite3.connect(path)
    c = conn.cursor()
    name = getProperName(lang)
    create = str("create table " + name + " (hash integer, sline integer, " + 
     "scol integer, eline integer, ecol integer, auth text, path text)")
    
    insertString = "insert into " + name + " values (?,?,?,?,?,?,?)"
    
    try:
        #Try to create the table.
        c.execute(buildCreateString(name))
    except:
        #If the table already exists. Do nothing.
        pass

    keys = master.keys()


    #Go through the master and add everything to the database.
    for key in keys:
        for entry in master[key]:
            c.execute(insertString, entry) 

    #Save changes.
    conn.commit()
    c.close()

def regexp(expr, item):
    reg = re.compile(expr)
    return reg.search(item) is not None

def removePath(lang, dbpath, tgtpath):
    conn = sqlite3.connect(dbpath)
    c = conn.cursor()
    name = getProperName(lang)
    conn.create_function("REGEXP", 2, regexp)
    quryStr = 'delete from ' + name + ' where path REGEXP ?'
    c.execute(quryStr, [tgtpath,])
    conn.commit()
    c.close()
    
def removeAuth(lang, dbpath, auth):
    conn = sqlite3.connect(dbpath)
    c = conn.cursor()
    name = getProperName(lang)
    quryStr = 'delete from ' + name + ' where auth=?'
    c.execute(quryStr, [auth,])
    conn.commit()
    c.close()
