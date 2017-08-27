import sys
import os
import time
import shutil
from Tkinter import Tk
from tkFileDialog import askopenfilename

def main(args):
    print "----------------------------------------------------------------"
    print "               Multiplay Portable Project Setup"
    print "----------------------------------------------------------------"
    print
    
    Tk().withdraw() # Prevent full GUI
    filetypes = [('All Files','.*'),('XML files','.XML')]
    oldXmlFilepath = askopenfilename(filetypes = filetypes, multiple = False, title = "Select the XML file of the project to setup...")
    if oldXmlFilepath == "":
        exit()
    oldXmlFilepath = os.path.normpath(oldXmlFilepath) # Replace forward slashes with backward slashes
    print
    print "Selected: ", oldXmlFilepath
    print

    try:
        folderPath = os.path.split(oldXmlFilepath)[0]
        projectName = os.path.splitext(os.path.split(oldXmlFilepath)[1])[0] # Get file name and strip extension
        ext = os.path.splitext(os.path.split(oldXmlFilepath)[1])[1]
        if (ext.upper() != ".XML"):
            raise IOError("Improper file extension")
        if not folderPath:
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

    mediaFolderPath = os.path.join(folderPath, "media")
    backupXmlFilepath = os.path.join(folderPath, "backup", "Backup of " + projectName + " - " + time.strftime("%m-%d-%Y") + " " + time.strftime("%I.%M.%S") + ".XML")
    newXmlFilepath = os.path.join(folderPath, projectName + ".XML")

    try:
        shutil.copy(oldXmlFilepath, backupXmlFilepath)
        shutil.copystat(oldXmlFilepath, backupXmlFilepath) # transfer metadata
        print "Backup file created in 'backup' folder."
        print
    except IOError, e:
        errorPrint("Failed to copy XML file.", e)

    # Write line by line to new file with relative path names
    # Copy files into media folder
    with open(newXmlFilepath, 'w') as newXmlFile:
        try:
            with open(backupXmlFilepath, 'r') as searchfile:
                for line in searchfile:
                    if "<FileName>" in line and not ".XML" in line:
                        filepathCopyFrom = line[16:line.index("</FileName>")]
                        filenameToCopy = os.path.split(filepathCopyFrom)[1]

                        line = "      <FileName>" + os.path.join(mediaFolderPath, filenameToCopy) + "</FileName>\n"
                        newXmlFile.write(line)
                    elif "<FileName>" in line:
                        line = "  <FileName>" + os.path.join(folderPath, projectName + ".XML") + "</FileName>\n"
                        newXmlFile.write(line)
                    else:
                        newXmlFile.write(line)
        except IOError, e:
            errorPrint("Input file could not be opened. Please ensure file exists and is a Multiplay XML show file.", e)

    print
    print "----------------------------------------------------------------"
    print "                  Project successfully setup."
    print "----------------------------------------------------------------"
    print
    print "Note: If using a USB drive or other removable media, files will frequently become unlinked"
    print "as a new drive letter will often be assigned. Running the setup.py file each time should fix this."
    print
    print "----------------------------------------------------------------"
    print
    print "Press ENTER to continue..."
    raw_input()

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
