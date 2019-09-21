"""
Comic Importer
"""

import sqlite3
from pathlib import Path
from zipfile import ZipFile
from PIL import Image
import re

DB = sqlite3.connect('data/comics')

COMICFOLDER = 'comics/'
THUMBNAILS = 'cache/'

THUMBNAILSIZE = 256, 256

COMICPATHS = Path(COMICFOLDER).glob('**/*.*')


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

# create numrows variable at start of code to get the number of rows before inserting
CURSOR.execute("select MAX(id) from comics")
NUMROWS = CURSOR.fetchone()[0]
if NUMROWS is None:
    NUMROWS = 1
else:
    NUMROWS = NUMROWS + 1

def parse_subject(to_parse, exists):
    """parses comicinfo.xml"""
    read_parse = to_parse.read().decode('utf-8')
    values = []
    for subject in COMICFILE:
        subject_parsed = re.search('<' + subject + '>(.*?)</' + subject + '>', read_parse)
        if subject_parsed is None:
            values.append(" ")
        else:
            values.append(subject_parsed.group(1))
    if exists is True:
        update_to_db(values)
    else:
        add_to_db(values)

def add_to_db(dbvalues):
    """adds info to db"""
    dbvalues.insert(0, COMICNAME)
    dbvalues.insert(1, COMICMOD)
    placeholder = '?'
    placeholders = ', '.join([placeholder]*len(dbvalues))
    CURSOR.execute("INSERT INTO comics(Filename,ModDate," + ELEMENTSTRING +") VALUES("+ placeholders +")",
                   (dbvalues))

def update_to_db(dbvalues):
    """updates info to db"""
    CURSOR.execute("DELETE FROM comics WHERE Filename = ?", (COMICNAME,))
    # TODO: nicer as update

def createThumbnail(zip_file, exists):
    """takes the first non Comicinfo.xml file in a zip and makes a thumbnail for it"""
    if(zip_file.namelist()[0] == 'ComicInfo.xml'):
        CACHEIMAGE = zip_file.namelist()[1]
    else:
        CACHEIMAGE = zip_file.namelist()[0]
    with zip_file.open(CACHEIMAGE) as file:
        img = Image.open(file,'r')
        img.thumbnail(THUMBNAILSIZE)
        if exists is True:
            img.save(THUMBNAILS + str(CHECKS[0]) + ".png", "PNG")
        else:
            img.save(THUMBNAILS + str(NUMROWS) + ".png", "PNG")

for comic in COMICPATHS:
    EXISTS = False #Variable which is true when comic already in database
    COMICMOD = comic.stat().st_mtime
    COMICNAME = comic.name
    CURSOR.execute("select id,Filename,ModDate from comics where Filename=? order by ModDate desc", (COMICNAME,))
    CHECKS = CURSOR.fetchone()
    if CHECKS is not None:
        if CHECKS[1] == COMICNAME: #compares filename with filename in database
            if CHECKS[2] == COMICMOD: #compares date with date in database
                continue
            else:
                EXISTS = True

    with ZipFile(comic) as zip_file:
        if 'ComicInfo.xml' in zip_file.namelist():
            with zip_file.open('ComicInfo.xml') as xml_file:
                parse_subject(xml_file, EXISTS)
        else: #If no comicinfo file found in the comic the filename is used as title,the other variables are empty
            if EXISTS is True:
                dbvalues = [COMICMOD, COMICNAME]
                CURSOR.execute("UPDATE comics SET ModDate = ? WHERE Filename = ? ",(dbvalues))
            else:
                dbvalues = [NUMROWS, COMICNAME, COMICMOD, comic.stem]
                CURSOR.execute("INSERT INTO comics(id,Filename,ModDate,Title) VALUES(?, ?, ?, ?)",(dbvalues))

        createThumbnail(zip_file, EXISTS)

        if EXISTS is False:
            NUMROWS = NUMROWS + 1
        print(comic.name)
DB.commit()
DB.close()