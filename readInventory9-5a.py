import os
import logging
import shelve
from collections import defaultdict
import pprint
import tkinter as tk
from tkinter import filedialog
import os.path
global ID

########### Check Stored variables - currently these variables are locations of Inventory File and Join File
def checkShelfValue(thisShelf):
    import os.path
    shelffile = shelve.open('invappdata')
    type(shelffile)
    try:
        thisFile = shelffile[thisShelf]
        if os.path.isfile(thisFile[0]):
            shelffile.close
            return True
        else:
            shelffile.close
            return False
        
    except KeyError:
        print("Shelf file or " + thisShelf + " missing. Creating new shelf file.")
        shelffile.close
        return False        

########### Function for loading Data files
def setFiles(whichFile,DialogMessage):
    
    shelffile = shelve.open('invappdata')
    root = tk.Tk()
    root.withdraw()
    
    openThisFile= ['']
    while openThisFile == ['']:     #Require User to choose file (Join File)
        root = tk.Tk()                  #Dialog Box Setting
        root.overrideredirect(True)     #Dialog Box Setting
        root.geometry('0x0+0+0')        #Dialog Box Setting
        root.focus_force()              #Dialog Box Setting
        File = filedialog.askopenfilename(parent=root, title=DialogMessage ) #Call Diag Box
        root.withdraw()
        openThisFile = [File]
    
    shelffile[whichFile] = openThisFile #Save path/file to binary file
    shelffile.close
    return openThisFile[0]

###########   Open Join File CSV split by row (CR/LF) and column (comma) 
def openJoinFile():
    global joinFileLines
    global currentJoinFile
    #Begin By Reading Product Join File
    shelffile = shelve.open('invappdata')
    type(shelffile)
    openJoinFileName = shelffile['openJoinFileName']
    shelffile.close
    print("Loading: " + openJoinFileName[0])
    currentJoinFile = openJoinFileName[0]
    helloJoinFile = open(openJoinFileName[0])
    joinFileContent = helloJoinFile.read()
    joinFileContent = joinFileContent.strip()
    joinFileLines = joinFileContent.split("\n")
    createProductIndexTable(joinFileLines)
    helloJoinFile.close
########### Open Inventory File CSV split by row (CR/LF) and column (comma)
def openInventoryFile():
    global inventFileLines                          #Make file values available outside this function
    global currentInventoryFile
    shelffile = shelve.open('invappdata')           
    type(shelffile)
    openInvFileName = shelffile['openInvFileName']
    shelffile.close
    print("Loading: " + openInvFileName[0])
    inventFile = open(openInvFileName[0])
    currentInventoryFile = openInvFileName[0]
    inventFileContent = inventFile.read()
    inventFileContent = inventFileContent.strip()
    inventFileLines = inventFileContent.split("\n")
    GetInventoryTable(inventFileLines)
    inventFile.close
########### Load inventory data into Python "Dictionary" construct
def GetInventoryTable(inventFileLines):
    global lineItems
    
    lineItems = {'': 'Sluggy'} #Seed Dictionary
    for foo in range(len(inventFileLines)):
        if foo == 0:                                            #Read all the file headers from first line of file (index 0)
            FileLineHeaders =  inventFileLines[foo].split(",")  #Column headers are separated by commas - parse them        
        else:                                                   #subsequesnt lines contain data. Use the headers (read above)as keys to each data line and field
            FileLineData = inventFileLines[foo].split(",")      #Data is comma separated - parse them
            for zed in range(len(FileLineHeaders)):             #A enumerate data using matching header count to define loop count
                if zed == 0:                                    #First Value per line should be part number - Use as Key
                    theKey = FileLineData[zed].strip(chr(34))   #get rid of any quotes in field - ASCII character(34)
                    lineItems.update({FileLineData[0].strip(chr(34)) : {}}) # create parent dictionary with "part number" key and value and seed empty nested dictionary  
                else:                  
                    try: #add data fields to the empty nested disctionary 
                      lineItems[theKey][FileLineHeaders[zed].strip(chr(34))] = FileLineData[zed].strip(chr(34)) #Each data valur maps to an associated key
                    except KeyError:                            #whoops
                      lineItems[theKey] = {FileLineHeaders[zed] : FileLineData[zed]}
                    
             
###########  Load join data 
def createProductIndexTable(myjoinFileLines): #This function reads "product join table" for bi-directional search (by Part Number or Join ID)

    global InventortyDictionary
    global productID
    #seed values
    InventortyDictionary = {}
    productID = {}
    lastJoinFileIndex = 0
    lastJoinFileProduct = 'zero'
    lastJoinFileItem = 0
    fullJoinFileProduct = ["ZERO"]
    
    
    for foo in range(len(myjoinFileLines)): #Iterate through Join variable that liks product type
            
        joinFileItem =  str(myjoinFileLines[foo]).split(",")
        thisJoinFileIndex = joinFileItem[0]

        #Create Product-to-ID link
        productID.update({joinFileItem[1] : joinFileItem[0]})
        try:
            #multiple  fullJoinFileProduct / joinFileItem[1]
            #Note: Flow may seem confusing because each list is essentially "finished" new values are read from file and previous ones are updated to .  posting fully populated list 
            if thisJoinFileIndex != lastJoinFileIndex:
                #C.  Create new record for each product type (1,2,3,4 Etc). This is after previous product type has been finished. This will add seed values on very first pass
                InventortyDictionary.update({lastJoinFileIndex : fullJoinFileProduct})
                #A.  Empty previous list "fullJoinFileProduct" to read new values into list
                fullJoinFileProduct = []
                # Finally add FIRST value to each list "fullJoinFileProduct" 
                fullJoinFileProduct.append(joinFileItem[1])
            else:
                #B. Adding subsequesnt Product Numbers to list
                fullJoinFileProduct.append(joinFileItem[1])
        except IndexError:
            print('IndexError')
              
              
        #set last values to cutrrent values before incrementing    
        lastJoinFileIndex = joinFileItem[0]
        lastJoinFileProduct = joinFileItem[1]
        
    #delete seed value
    del InventortyDictionary[0] # Remove seed value
    return InventortyDictionary #Function retuen value is the table keyed by table join variable 


###########
def MatchProduct(thisPartNo):            # function to look up product ID then match other Products to ID
    try:
        thisProductID = productID[thisPartNo]
        return InventortyDictionary[thisProductID]
    except KeyError:
        print ("Part: " + thisPartNo + ' is not in Join File. Add if necessary!' )
        return [thisPartNo]
        
    


###########
def MatchProductDetail(thisProductID):      #send list to this function to return details on each list item
    iterator = []                           # declare a list variable
    iterator = MatchProduct(thisProductID)  #pass products to list variable
    for foo in iterator:
        displayProductData(foo)             # pass each part number in list to "displayProductData" function 
        print("")                           # add blank line between products
    
###########
def displayProductData(thisProductID):      #Show Data associated with inventory item
    print("Part: " + thisProductID)
    ThisProductDetails = {}                 #declare as dictionary item
    try:
        ThisProductDetails = lineItems[thisProductID]   #Lineitems are in memory - read from inventory file
    except KeyError:                                    #Part Number not found in inventory file
        print("Part: " + thisProductID + " not in inventory file")                  #tell user item not found
    
    for foo in ThisProductDetails.keys():               #Iterate through columns of selected inventory file
        if len(str(foo)) >=1:                           #Ignore blank columns (commas with no values)
            print( foo.ljust(40,".") + ': ' + ThisProductDetails[foo]) # Print key followed by value

#############
def pp(theData):                        #Make printing to screen easy
    pprint.pprint(theData)

#############                           #Help Menu Function
def  uGetdisplayProductData():
    print('Enter Part #:')
    uResponse = input()
    displayProductData(uResponse)

#############                           #Help Menu Function
def uGetMatchProductDetail():
    print('Enter Part #:')
    uResponse = input()
    MatchProductDetail(uResponse)

#############                           #Help Menu Function
def uNewJoinFile():
    global currentJoinFile
    print("Current Join file is: " + currentJoinFile)
    print ('Do you want to upload new join file? (y or n)')
    uInput = input()
    uInput = uInput.upper()
    if uInput == 'Y':
        currentJoinFile = setFiles('openJoinFileName','Open Product Join File')
        openJoinFile()
        openInventoryFile()
        

#############                           #Help Menu Function
def uNewInvFile():
    global currentInventoryFile
    print("Current Inventory file is: " + currentInventoryFile)
    print ('Do you want to upload new Inventory file? (y or n)')
    uInput = input()
    uInput = uInput.upper()
    if uInput == 'Y':
       currentInventoryFile = setFiles('openInvFileName','Open Inventory File')
       openJoinFile()
       openInventoryFile()
        
   
#############                           #Help Menu Function
def h():
    global ID
    print('\n' + 'This is "Help Function". Choose An Option.')
    print('1:Part # Inventory  '.ljust(25) + '2:Part # match Inventory\n' + '3:Index table.'.ljust(25) + '4:Inventory table \n' + '5:Open Index table CSV.'.ljust(25) + '6:Open Inventory table CSV.\n' + '7: Exit Help')
    uResponse = input()
    if  uResponse == "1":
        uGetdisplayProductData()
        h()
    elif uResponse == "2":
        uGetMatchProductDetail()
        h()
    elif uResponse == "3":
        pp(ID)
        h()
    elif uResponse == "4":
        pp(lineItems)
        h()
    elif uResponse == "5":
        uNewJoinFile()
        ID = createProductIndexTable(joinFileLines)
        h()
    elif uResponse == "6":
        uNewInvFile()
        h()
    elif uResponse == "7":
        print('Thank you!')
    else:
        print("Sluggy")
        h()
    
    
              
#############                                    

global cwd
cwd = os.chdir("C:\\python\\") #set default file directory
cwd
if checkShelfValue('openJoinFileName') == False:
    setFiles('openJoinFileName','Open Product Join File1')

if checkShelfValue('openInvFileName') == False:
    setFiles('openInvFileName','Open Inventory File1')

openJoinFile()
openInventoryFile()
global ID
global help
ID = {}
ID = createProductIndexTable(joinFileLines)
GetInventoryTable(inventFileLines)
print ('Enter a command or type "h()" for input list.')

#############
    



##--------------##
##end of program##


