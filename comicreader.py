"""
comicreader
"""
import glob, os
from zipfile import ZipFile
import sqlite3
import re
from PIL import Image

DB = sqlite3.connect('data/mydb')

COMICFOLDER = 'comics/'
CACHEFOLDER = 'cache/'

THUMBNAILSIZE = 256, 256

NUMROWS = ''

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

# create numrows variable at start of code to get the number of rows before inserting
CURSOR.execute("select MAX(id) from comics")
NUMROWS = CURSOR.fetchone()[0]
if NUMROWS is None:
    NUMROWS = 0
else:
    NUMROWS = NUMROWS + 1

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
    if manual is False:
        update_to_db(values)
    else:
        add_to_db(values)


def add_to_db(dbvalues):
    """adds info to db"""
    dbvalues.insert(0, NUMROWS)
    dbvalues.insert(1, COMICNAME)
    dbvalues.insert(2, COMICMOD)
    placeholder = '?'
    placeholders = ', '.join([placeholder]*len(dbvalues))
    CURSOR.execute("INSERT INTO comics(id,Filename,ModDate," + ELEMENTSTRING +") VALUES("+ placeholders +")",
                   (dbvalues))


def update_to_db(dbvalues):
    """updates info to db"""
    CURSOR.execute("UPDATE comics SET ModDate = ? WHERE Filename = ?",(COMICMOD, COMICNAME))

def create_thumbnail(zip, manual):
    """takes the dirst file in a document and makes a thumbnail of it"""
    if(zip_file.namelist()[0] == 'ComicInfo.xml'):
        CACHEIMAGE = zip_file.namelist()[1]
    else:
        CACHEIMAGE = zip_file.namelist()[0]

    with zip_file.open(CACHEIMAGE) as file:
        img = Image.open(file,'r')
        img.thumbnail(THUMBNAILSIZE)
        if manual is False:
            img.save(CACHEFOLDER + str(CHECKS[0]) + ".png", "PNG")
        else:
            img.save(CACHEFOLDER + str(NUMROWS) + ".png", "PNG")

for comic in files():
    MANUAL = True
    COMICNAME = comic
    COMICMOD = os.path.getmtime(COMICFOLDER+comic)
    CURSOR.execute("select id,Filename,ModDate from comics where Filename=? order by ModDate desc", (COMICNAME,))
    CHECKS = CURSOR.fetchone()
    if CHECKS is not None:
        if CHECKS[1] == COMICNAME:
            if CHECKS[2] == COMICMOD:
                continue
            else:
                MANUAL = False
    with ZipFile(COMICFOLDER+comic) as zip_file:
        if 'ComicInfo.xml' in zip_file.namelist():
            with zip_file.open('ComicInfo.xml') as xml_file:
                parse_subject(xml_file, MANUAL)
        else:
            if MANUAL is False:
                dbvalues = [COMICMOD, COMICNAME]
                CURSOR.execute("UPDATE comics SET ModDate = ? WHERE Filename = ? ",(dbvalues))
            else:
                dbvalues = [NUMROWS, COMICNAME, COMICMOD]
                CURSOR.execute("INSERT INTO comics(id,Filename,ModDate) VALUES(?, ?)",(dbvalues))

        create_thumbnail(zip_file, MANUAL)

        if MANUAL is True:
            NUMROWS = NUMROWS + 1
DB.commit()
DB.close()
