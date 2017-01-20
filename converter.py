import sys
import os
import time
import select
import shutil
from Tkinter import Tk
from tkFileDialog import askopenfilename

def main(args):
    print "----------------------------------------------------------------"
    print "               Multiplay Portable Project Converter"
    print "----------------------------------------------------------------"
    print

    Tk().withdraw() # Prevent full GUI
    filetypes = [('all files','.*'),('XML files','.XML')]
    oldXmlFilepath = askopenfilename(filetypes = filetypes, multiple = False, title = "Select the XML file of the project to copy...")
    oldXmlFilepath = os.path.normpath(oldXmlFilepath) # Replace forward slashes with backward slashes
    print
    print "Selected: ", oldXmlFilepath
    print

    try:
        directory = os.path.split(oldXmlFilepath)[0]
        projectName = os.path.splitext(os.path.split(oldXmlFilepath)[1])[0] # Get file name and strip extension
        ext = os.path.splitext(os.path.split(oldXmlFilepath)[1])[1]
        if (ext.upper() != ".XML"):
            raise IOError("Improper file extension")
        print "Directory: ", directory
        print
        if not directory:
            raise IOError("Filepath not found")
    except IOError, e:
        errorPrint("Input file could not be opened. Please ensure file exists and is a Multiplay XML show file.", e)

    # Overwrite default project name assigned above if one is present in the XML
    try:
        valid = False
        with open(oldXmlFilepath, 'r') as searchfile:
            for line in searchfile:
                if "<Version>2.5.5.0</Version>" in line:
                    valid = True
                if "<Title>" in line:
                    projectName = line[11:line.index("</Title>")]
        if not valid:
            raise IOError("Not a valid Multiplay XML file. Please ensure you are updated to Multiplay Version 2.5.5.0 or manually change the version number in the XML file.")
    except IOError, e:
        errorPrint("Input file could not be opened. Please ensure file exists and is a Multiplay XML show file.", e)

    print "Project Name: ", projectName
    print

    try:
        folderPath = os.path.join(directory, projectName + " - Portable Copy")
        if not os.path.exists(folderPath):
            os.makedirs(folderPath)
            print "Portable Folder Path: ", folderPath
            print
        else:
            print "Folder '", folderPath, "' already exists."
            folderPath = folderPath + " (" + time.strftime("%m-%d-%Y") + " " + time.strftime("%I.%M.%S") + ")"
            os.makedirs(folderPath)
            print "Renamed to '", folderPath, "'."
            print
    except OSError, e:
        errorPrint("Failed to create main folder.", e)

    mediaFolderPath = os.path.join(folderPath, "media")
    try:
        os.makedirs(mediaFolderPath)
    except OSError, e:
        errorPrint("Failed to create media folder.", e)
    try:
        os.makedirs(os.path.join(folderPath, "backup"))
    except OSError, e:
        errorPrint("Failed to create backup folder.", e)

    backupXmlFilepath = os.path.join(folderPath, "backup", "Backup of " + projectName + " - " + time.strftime("%m-%d-%Y") + " " + time.strftime("%I.%M.%S") + ".XML")
    newXmlFilepath = os.path.join(folderPath, projectName + " - Portable Copy.XML")

    # Copy unaltered XML file to backup file
    try:
        shutil.copy(oldXmlFilepath, backupXmlFilepath)
        shutil.copystat(oldXmlFilepath, backupXmlFilepath) # transfer metadata
        print "Backup file created in 'backup' folder."
        print
    except IOError, e:
        errorPrint("Failed to copy XML file.", e)

    # Write line by line to new XML file with replaced path names
    # Copy files into media folder
    with open(newXmlFilepath, 'a') as newXmlFile:
        with open(backupXmlFilepath, 'r') as searchfile:
            for line in searchfile:
                if "<FileName>" in line and not ".XML" in line:
                    filepathCopyFrom = line[16:line.index("</FileName>")]
                    filenameToCopy = os.path.split(filepathCopyFrom)[1]
                    filepathCopyTo = os.path.join(mediaFolderPath, filenameToCopy)

                    print "Copying file '", filenameToCopy, "'..."
                    try:
                        shutil.copy(filepathCopyFrom, filepathCopyTo)
                        shutil.copystat(filepathCopyFrom, filepathCopyTo)
                        print "File copied."
                        print
                    except IOError, e:
                        print
                        print "File failed to copy."
                        print e
                        print
                        print "Continue with other file operations? (Y/N)"
                        answer = raw_input()
                        if (answer.upper() == "N"):
                            print
                            print "Aborting..."
                            print
                            print "-------------------- INCOMPLETE --------------------"
			
                    line = "      <FileName>" + filepathCopyTo + "</FileName>\n"
                    newXmlFile.write(line)
                elif "<FileName>" in line:
                    line = "  <FileName>" + os.path.join(folderPath, projectName) + " - Portable Copy.XML</FileName>\n"
                    newXmlFile.write(line)
                elif "<Title>" in line:
                    line = "<Title>" + projectName + " - Portable Copy</Title>\n"
                    newXmlFile.write(line)
                else:
                    newXmlFile.write(line)

    setupFilepath = os.path.join(os.path.split(os.path.realpath(__file__))[0], "setup.py") # get directory of running file, strip file, and add setup.py
    try:
        shutil.copy(setupFilepath, os.path.join(folderPath, "setup.py"))
        shutil.copystat(setupFilepath, os.path.join(folderPath, "setup.py"))
    except IOError, e:
        errorPrint("Failed to copy setup.py file. Please ensure that it is located in the same directory as copy.py and is named correctly.", e)
        

    print
    print "Setup file copied."

    print
    print "----------------------------------------------------------------"
    print "                  Project successfully copied."
    print "----------------------------------------------------------------"
    print
    print "Location: ", folderPath
    print
    print "Copy the portable folder to any location and run the setup.py file."
    print "Note: If using a USB drive or other removable media, files will frequently become unlinked"
    print "as a new drive letter will often be assigned. Running the setup.py file each time should fix this."
    print
    print "----------------------------------------------------------------"
    print
    print "Press ENTER to continue..."
    raw_input()

def removeAllFiles(path):
    try:
        shutil.rmtree(path)
        print
        print "Files successfully removed."
    except IOError, e:
        errorPrint("Could not successfully remove all files.", e)

def errorPrint(message, standardErr = ""):
    print "\n\n"
    print message
    if standardErr:
        print "Error message: ", standardErr
    print
    print "Press ENTER to exit..."
    raw_input()
    exit()

if __name__ == "__main__":
    main(sys.argv[1:])
