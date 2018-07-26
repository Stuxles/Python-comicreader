import zipfile
import xml.etree.ElementTree as ET
import os
import sqlite3
from PIL import Image

# database connection
db = sqlite3.connect('data/mydb')
# thumbnail size
thumbsize = 230, 230
# folder where comics are stored
comicfolder = 'test/'

cursor = db.cursor()
# create table query and execute
cursor.execute('''CREATE TABLE IF NOT EXISTS"comics" ( `id` INTEGER PRIMARY KEY AUTOINCREMENT, `Filename` TEXT, `ModDate` NUMERIC, 
`Title` TEXT, `Series` TEXT, `Summary` TEXT, `Writer` TEXT, `Penciller` TEXT, `Inker` TEXT, `Letterer` TEXT, 
`CoverArtist` TEXT, `Editor` TEXT, `Publisher` TEXT, `Genre` TEXT, `Web` TEXT, `LanguageISO` TEXT, `Translator` TEXT, 
`AgeRating` TEXT, `Manga` TEXT, `Characters` TEXT, `PageCount` INTEGER )''')
# the changes get commited
db.commit()

# Addocomic function
def addcomic(cbzfile):
    # selects the zip
    zips = zipfile.ZipFile(comicfolder+cbzfile,'r')
    # 2 lists are generated which already include the filename and modification date
    elements = list(('Filename','ModDate'))
    values = list((cbzfile,os.path.getmtime(comicfolder+cbzfile)))
    print(cbzfile)
    # a local list is created with all the files in this zip
    imagelist = zips.namelist()
    # check if comicinfo.xml is in the zip
    if 'ComicInfo.xml' in zips.namelist():
        # remove comicinfo.xml from the local list of filenames
        imagelist.remove('ComicInfo.xml')
        # open comicinfo.xml
        file = zips.open('ComicInfo.xml')
        # parse xml to elemnttree instance
        tree = ET.parse(file)
        # get the root of the xml file
        root = tree.getroot()
        # loop through (almost) all elements in the xml file
        for thing in root:
            # add element names to the element list and values to the value list, this excludes the pages element
            if not thing.tag == "Pages":
                elements.append(thing.tag)
                values.append(thing.text)

    # the first image in the zip file is opened
    image = zips.open(imagelist[0])
    # open the image as an image with pillow
    orig = Image.open(image)
    # image is converted to RGB as to remove the alphachannel if present
    orig = orig.convert("RGB")
    # create thumbnail with desired size while keeping the correct aspect ratio
    orig.thumbnail(thumbsize)
    # save the image as jpeg with a temporary filename
    orig.save('cache/temp.jpg', "JPEG")

    # make a string from the list of elements
    elementstring = ','.join(str(x) for x in elements)
    # make a string from the list of values and putting quest around them
    valuestring = '","'.join(str(x) for x in values)
    # create sql query to insert data in the table
    sql = f'''INSERT INTO comics({elementstring}) VALUES("{valuestring}")'''
    # execution of the insert query
    cursor.execute(sql)
    # getting the id from the row that was just inserted
    lastid = cursor.lastrowid
    # the thumbnail gets renamed to the row id
    os.rename('cache/temp.jpg',f'cache/{lastid}.jpg')
    # the changes are commited to the database
    db.commit()

# generates list of files in comicfolder
def files():  
    for file in os.listdir(comicfolder):
        if os.path.isfile(os.path.join(comicfolder, file)):
            yield file

# runs(adds comic) for every file found with the file function
for file in files():  
    addcomic(file)

# connection to the database is closed
db.close()