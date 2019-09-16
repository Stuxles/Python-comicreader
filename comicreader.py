"""
Comic Importer
"""

import sqlite3
from pathlib import Path
from zipfile import ZipFile
from PIL import Image

DB = sqlite3.connect('data/comics')

COMICFOLDER = 'comics/'
THUMBNAILS = 'cache/'

THUMBNAILSIZE = 256, 256

COMICPATHS = Path(COMICFOLDER).glob('**/*.*')

COMICFILE = ["Title", "Series", "Summary", "Writer", "Penciller", "Inker", "Letterer",
             "CoverArtist", "Editor", "Publisher", "Genre", "Web", "LanguageISO",
             "Translator", "AgeRating", "Manga", "Characters", "PageCount"]

CURSOR = DB.cursor()
# create table query and execute
CURSOR.execute('''CREATE TABLE IF NOT EXISTS"comics" ( `id` INTEGER PRIMARY KEY AUTOINCREMENT,
`Filename` TEXT, `ModDate` NUMERIC, `Title` TEXT, `Series` TEXT, `Summary` TEXT, `Writer` TEXT,
`Penciller` TEXT, `Inker` TEXT, `Letterer` TEXT, `CoverArtist` TEXT, `Editor` TEXT,
`Publisher` TEXT, `Genre` TEXT, `Web` TEXT, `LanguageISO` TEXT, `Translator` TEXT,
`AgeRating` TEXT, `Manga` TEXT, `Characters` TEXT, `PageCount` INTEGER )''')
# the changes get commited
DB.commit()

def createThumbnail(zip_file):
    """takes the first file in a zip and makes a thumbnail for it"""
    if(zip_file.namelist()[0] == 'ComicInfo.xml'):
        CACHEIMAGE = zip_file.namelist()[1]
    else:
        CACHEIMAGE = zip_file.namelist()[0]
    with zip_file.open(CACHEIMAGE) as file:
        img = Image.open(file,'r')
        img.thumbnail(THUMBNAILSIZE)
        img.save(THUMBNAILS + str("1") + ".png", "PNG")

for comic in COMICPATHS:
    with ZipFile(comic) as zip_file:
        createThumbnail(zip_file)
        # print(comic.name)