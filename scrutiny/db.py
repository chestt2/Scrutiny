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
    name = lexer.name.lower()
    
    #sqlite table names cannot contain symbols, so adjust.
    name = name.replace('+', 'plus')
    name = name.replace('#', 'sharp')
    name = name.replace('-', 'dash')
    name = name.replace('@', 'at')
    name = name.replace('.', 'dot')
    if not all(map(str.isalnum, name)):
        sys.exit(1)
    #return the proper name.
    return name

def getTableNames(lang):
    entry_table = getProperName(lang)
    author_table = entry_table + '_authors'
    return entry_table, author_table

def add_file_to_authors( cur, authtable, entry):
    insert_auth = "INSERT OR ABORT INTO " + authtable + \
                    "(auth,path) VALUES (?,?)"
    try:
        cur.execute(insert_auth, (entry.auth, entry.loc))
    except:
        return None
    return cur.lastrowid


def create_tables(cur, lang):
    '''Create two tables in the cur database lang and lang_auth'''

    name, authors = getTableNames(lang)
    create_entry_table = str("CREATE TABLE IF NOT EXISTS " + name +\
        " (hash INT, sline INT, scol INT, eline INT, ecol INT, fileid INT " +\
        " not null, CONSTRAINT entry UNIQUE (sline, scol, eline, ecol, " +\
        "fileid))")
    create_auth_table = "CREATE TABLE IF NOT EXISTS " + authors + \
        "(auth TEXT, path TEXT UNIQUE)"
    cur.execute(create_entry_table)
    cur.execute(create_auth_table)
    return name, authors
    

def addToDB(master, path, lang):
    conn = sqlite3.connect(path)
    cur = conn.cursor()

    ent_table, auth_table = create_tables(cur, lang) 

    insert_str = "INSERT OR IGNORE INTO " + ent_table + " (hash, sline, " +\
                   "scol, eline, ecol, fileid) values (?,?,?,?,?,?)"

    files = {}
    #Go through the master and add everything to the database.
    for key in master.keys():
        for entry in master[key]:
            if entry.loc not in files:
                files[entry.loc] = add_file_to_authors(cur, auth_table, entry)
            cur.execute(insert_str, (entry.hash, entry.sline, entry.scol,
                                    entry.eline, entry.ecol, files[entry.loc])) 

    #Save changes.
    conn.commit()
    cur.close()

def delete_after_select(dbpath, select, delete, target, ent_table):
    """Deletes entries from both the entry and author tables"""
    
    with sqlite3.connect(dbpath) as conn:
        delete_ent = 'delete from ' + ent_table + ' where fileid=?'
        targets = conn.execute(select, (target)).fetchall()
        conn.execute(delete, (target))
        for fileid in targets:
            conn.execute(delete_ent, (fileid[0]))
    

def remove_path(lang, dbpath, tgtpath):
    """Removes all entries whose path matches *tgtpath*"""
    ent_table, auth_table = getTableNames(lang)

    suffix = auth_table + ' where path like \'%' + tgtpath + '%\''
    select = 'select rowid from ' + suffix
    delete = 'delete rowid from ' + suffix
    delete_after_select(dbpath, select, delete, tgtpath, ent_table)

    
def remove_auth(lang, dbpath, auth):
    """Removes all of auth's entries in the database"""
    ent_table, auth_table = getTableNames(lang)

    suffix = ' from ' + auth_table + ' where auth=?'
    select = 'select rowid' + suffix 
    delete = 'delete' + suffix 
    delete_after_select(dbpath, select, delete, auth, ent_table)

def main(argv):
    """Main function dealing with all user interactions with database"""

    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-l", "--language", dest="language", default="c",
                      help="tokenize using lexer for language", metavar="LANG")
    parser.add_option("--delete-path", dest="delpath", default=False,
                      help='delete entries that match the regex \'*path*\'')
    parser.add_option("--delete-auth", dest="delauth", default=False,
                      help='delete any of a specific authors entires')
    options, args = parser.parse_args(argv)

    if options['delauth'] is not False:
        remove_auth(options['language'], args[0], options['delauth'])
    if options['delpath'] is not False:
        remove_path(options['language'], args[0], options['delauth'])

if __name__ == "__main__":
    main(sys.argv[1:])

