"""
comicreader
"""
import os
from zipfile import ZipFile
import sqlite3
import re

DB = sqlite3.connect('data/mydb')

COMICFOLDER = 'testcomics/'

COMICNAME = ''
COMICMOD = ''

COMICFILE = ["Title", "Series", "Summary", "Writer", "Penciller", "Inker", "Letterer",
             "CoverArtist", "Editor", "Publisher", "Genre", "Web", "LanguageISO",
             "Translator", "AgeRating", "Manga", "Characters", "PageCount"]

ELEMENTLIST = COMICFILE
ELEMENTSTRING = ','.join(map(str, ELEMENTLIST))

CURSOR = DB.cursor()
# create table query and execute
CURSOR.execute('''CREATE TABLE IF NOT EXISTS"comics" ( `id` INTEGER PRIMARY KEY AUTOINCREMENT,
`Filename` TEXT, `ModDate` NUMERIC, `Title` TEXT, `Series` TEXT, `Summary` TEXT, `Writer` TEXT,
`Penciller` TEXT, `Inker` TEXT, `Letterer` TEXT, `CoverArtist` TEXT, `Editor` TEXT,
`Publisher` TEXT, `Genre` TEXT, `Web` TEXT, `LanguageISO` TEXT, `Translator` TEXT,
`AgeRating` TEXT, `Manga` TEXT, `Characters` TEXT, `PageCount` INTEGER )''')
# the changes get commited
DB.commit()

def files():
    """generates list of files in comicfolder"""
    # Loop for every file in comic folder
    for file in os.listdir(COMICFOLDER):
        if os.path.isfile(os.path.join(COMICFOLDER, file)):
            yield file

def parse_subject(to_parse, manual):
    """parses comicinfo.xml"""
    read_parse = to_parse.read().decode('utf-8')
    values = []
    for subject in COMICFILE:
        subject_parsed = re.search('<' + subject + '>(.*?)</' + subject + '>', read_parse)
        if subject_parsed is None:
            values.append(" ")
        else:
            values.append(subject_parsed.group(1))
    if manual == False:
        update_to_db(values)
    add_to_db(values)


def add_to_db(dbvalues):
    """adds info to db"""
    dbvalues.insert(0,COMICNAME)
    dbvalues.insert(1,COMICMOD)
    placeholder = '?'
    placeholders = ', '.join([placeholder]*len(dbvalues))
    CURSOR.execute("INSERT INTO comics(Filename,ModDate," + ELEMENTSTRING +") VALUES("+ placeholders +")",
                   (dbvalues))

def update_to_db(dbvalues):
    """updates info to db"""
    CURSOR.execute("DELETE FROM comics WHERE Filename = ?",(COMICNAME,))
    # nicer as update
    

for comic in files():
    MANUAL = True
    COMICNAME = comic
    COMICMOD = os.path.getmtime(COMICFOLDER+comic)
    CURSOR.execute("select Filename,ModDate from comics where Filename=? order by ModDate desc", (COMICNAME,))
    CHECKS = CURSOR.fetchone()
    if CHECKS is not None:
        if CHECKS[0] == COMICNAME:
            if CHECKS[1] == COMICMOD:
                continue
            else:
                MANUAL = False
    with ZipFile(COMICFOLDER+comic) as zip_file:
        if 'ComicInfo.xml' in zip_file.namelist():
            with zip_file.open('ComicInfo.xml') as xml_file:
                parse_subject(xml_file, MANUAL)
        else:
            if MANUAL == False:
                dbvalues = [COMICMOD, COMICNAME]
                CURSOR.execute("UPDATE comics SET ModDate = ? WHERE Filename = ? ",(dbvalues))
            else:
                dbvalues = [COMICNAME, COMICMOD]
                CURSOR.execute("INSERT INTO comics(Filename,ModDate) VALUES(?, ?)",(dbvalues))
DB.commit()
DB.close()