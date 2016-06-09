#SecureWallet password manager.
#Created by Ritwik Dutta
#Please do not distribute without credit.
#If you have any questions, email: ritzymail@gmail.com
# Import required modules.
#wx is used for the GUI.
import wx
#OS is used to check if the configuration exists.
import os
#Hashing used to encrypt password
from hashlib import sha256
from hashlib import md5
#Split used to split apart username and password upon parse
from shlex import split

#Main class for application frame
class secureWalletFrame(wx.Frame):
    def __init__(self):
        #Initialize base frame for application
        wx.Frame.__init__(self,None,-1,'SecureWallet')
        #Boot app to check for config and first run
        runApp = self.initAppBoot()
        #Initialize basic elements of application
        if (runApp != False):
            #Initialize info in elements
            self.initElementsDisplay()
            if (runApp != True):
                self.initAppBasic()
            #Bind menu objects to corresponding functions while creating add and remove items
            self.Bind(wx.EVT_MENU, self.addItem,    self.addMenuItem)
            self.Bind(wx.EVT_MENU, self.deleteItem, self.deleteMenuItem)
            self.Bind(wx.EVT_MENU, self.modifyItem, self.modifyMenuItem)
            self.Bind(wx.EVT_MENU, self.saveItems,  self.saveMenuItem)
            self.Bind(wx.EVT_LISTBOX, self.displayItemInfo, self.serviceListBox)
        else:
            self.Destroy()

    #Creates elements in window        
    def initElementsDisplay(self):
        #Creates split view for service and username/password combo
        self.splitView = wx.SplitterWindow(self, 0)
        #Create list for services and dictionary for resulting username/password combo 
        self.serviceList = []
        self.serviceListFull={}
        #Create service list box and username/password display box and put into split view
        self.serviceListBox = wx.ListBox(self.splitView, 10, wx.DefaultPosition, wx.DefaultSize,\
        self.serviceList, wx.LB_SINGLE)        
        self.infoArea = wx.TextCtrl(self.splitView, 2, "Choose a service to display its information.",\
        wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY|wx.TE_MULTILINE) 
        self.splitView.SplitVertically(self.serviceListBox, self.infoArea)
        #Create menu bar with File and Manage sections
        self.menuBar = wx.MenuBar()
        self.manageMenu = wx.Menu()
        self.fileMenu = wx.Menu()
        self.menuBar.Append(self.fileMenu, 'File')
        self.menuBar.Append(self.manageMenu, 'Manage')
        self.SetMenuBar(self.menuBar)
        #Create and add menu options 
        self.addMenuItem    = self.manageMenu.Append(4, "Add Item")
        self.deleteMenuItem = self.manageMenu.Append(5, "Delete Item")
        self.modifyMenuItem = self.manageMenu.Append(6, "Modify Item")
        self.saveMenuItem   = self.fileMenu.Append(7, "Save Items")
        #Show frame on screen
        self.Show(True)
        
    #Start app or configure first time
    def initAppBoot(self):
        #Check for configuration file
        if ("securewallet" not in os.listdir(".")):
            #If it does not exist, run the initial configuration
            self.firstRun()
            return True
        else:
            #If it does not, check for the password
            passTries = 0
            #If wrong three times, the app closes
            while (passTries < 3):
                if passTries<1:
                    if ( not self.checkPassword()): pass
                    else: break   
                elif passTries<2:
                    if (not self.checkPassword("Incorrect once. Enter password.")): pass
                    else: break
                elif passTries<3:
                    if (not self.checkPassword("Incorrect twice. Enter password.")):
                        #Show notification and close
                        if (wx.MessageDialog(self, "Password incorrect three times.","Closing application.", wx.OK).ShowModal()):
                            return False
                #Increment number of tries
                passTries = passTries + 1

    #Function to fill info into app elements
    def initAppBasic(self):
        #Read encrypted data from file and close file
        self.configFile = open('securewallet', 'r')
        self.encryptedBuffer = self.configFile.readlines()[1:]
        self.configFile.close()
        #Create empty buffer
        dataBuffer = []
        #Iterate through encrypted lines
        for itemLine in self.encryptedBuffer:
            #Split into character sections
            itemLine = split(itemLine)
            #Initiate empty slot for element
            dataBuffer.append("")
            #Loop through character sections
            for characterNum in itemLine:
                #Decrypt character and add to element
                dataBuffer[-1] = dataBuffer[-1] + (chr(eval(characterNum)-self.passNum))            
        #Create empty array to hold sets with service information
        serviceSets = []
        #Cut buffer into chunks of three and add each as a service set
        for i in xrange(0, len(dataBuffer), 3):
            serviceSets.append(dataBuffer[i:i+3])
        #Add keys to service list and service dictionary 
        for serviceSet in serviceSets:
            self.serviceList.append(serviceSet[0])
            self.serviceListFull[serviceSet[0]] = [serviceSet[1],serviceSet[2]]
        #Set service list box items to service sets
        self.serviceListBox.SetItems(self.serviceList)
                                                
    #Set up stuff for first run
    def firstRun(self):
        #Create dialog and get password
        self.passWordDialogInstance = passWordDialog(self,"Welcome! Enter a new password.")
        if (self.passWordDialogInstance.ShowModal() == wx.ID_OK):
            self.passwdData = self.passWordDialogInstance.passwordBox.GetValue().strip()
        self.passWordDialogInstance.Destroy()
        #Create config file and generate hashed password
        self.configFile = open('securewallet', 'w+')
        self.hashedPasswordword = md5(sha256(md5(sha256(self.passwdData).hexdigest()).hexdigest()).\
        hexdigest()).hexdigest()
        #Write password to file and close handler
        self.configFile.write(str(self.hashedPasswordword) + '\n')
        self.configFile.close()
        self.passNum = int(md5(self.passwdData).hexdigest(), 16)
    
    #Checks input password against entropy bit and written key
    def checkPassword(self, message="Enter password."):
        #Open configuration file and read first line to get hashed password
        self.configFile = open('securewallet', 'r+')
        self.hashedPassword = self.configFile.readline()
        #Open password dialog
        self.passWordDialogInstance = passWordDialog(self,message)
        if (self.passWordDialogInstance.ShowModal()):
            #Get password
            self.passwdData = self.passWordDialogInstance.passwordBox.GetValue().strip()
        #Close dialog
        self.passWordDialogInstance.Destroy() 
        #Hash password
        self.digestPass = md5(sha256(md5(sha256(self.passwdData).hexdigest()).hexdigest()).hexdigest()).\
        hexdigest()
        #Check for equality between passwords
        if (self.digestPass in self.hashedPassword):
            self.passNum = int(md5(self.passwdData).hexdigest(), 16)
            return True
        
        
        
    #Function for adding item
    def addItem(self, event):
        #Create dialog with empty text boxes
        self.itemEditDialogInstance = itemEditDialog(self, "", "", "")
        if (self.itemEditDialogInstance.ShowModal() == wx.ID_OK):
            #Close dialog
            self.itemEditDialogInstance.Destroy()
            #Add service name to service dictionary with [username, password] array as value
            self.serviceListFull[self.itemEditDialogInstance.serviceTextBox.GetValue().strip()] =\
            [self.itemEditDialogInstance.userTextBox.GetValue().strip() ,\
            self.itemEditDialogInstance.passwordTextBox.GetValue().strip()]
            #Add service name to service list
            self.serviceList.append(self.itemEditDialogInstance.serviceTextBox.GetValue().strip())
            #Refresh service list box with update service list
            self.serviceListBox.SetItems(self.serviceList)
        #Save items to file
        self.saveItems()
            
    #Function for deleting item
    def deleteItem(self, event=None, delIndex=None):
        #Prevent IndexError output when no elements present or none selected
        try:
            #Get index of item to be deleted
            if (delIndex == None):
                delIndex = self.serviceListBox.GetSelection()
            #Delete item from service list
            del(self.serviceList[delIndex])
            #Delete item from service dictionary
            del(self.serviceListFull[self.serviceListBox.GetString(delIndex)]) 
            #Delete item from service list box
            self.serviceListBox.Delete(delIndex)
            #Save items to file
            self.saveItems()
            #Clear text in display box
            self.infoArea.SetValue("")
        except IndexError:
            pass
        
    #Function for modifying item
    def modifyItem(self, event):
        #Prevent IndexError output when no elements present or none selected
        try:
            #Get index of item to modify
            modifyIndex = self.serviceListBox.GetSelection()
            #Create array of items to be modified
            #Service name
            modifyArray = [self.serviceList[modifyIndex],\
            #Username
            self.serviceListFull[self.serviceList[modifyIndex]][0],\
            #Password
            self.serviceListFull[self.serviceList[modifyIndex]][1]]
            #Delete item
            self.deleteItem(modifyIndex)
            #Create dialog
            self.itemEditDialogInstance = itemEditDialog(self, modifyArray[0], modifyArray[1], modifyArray[2])
            if (self.itemEditDialogInstance.ShowModal() == wx.ID_OK):
                #Close dialog
                self.itemEditDialogInstance.Destroy()
                #Add service name to service dictionary with [username, password] array as value
                self.serviceListFull[self.itemEditDialogInstance.serviceTextBox.GetValue().strip()] =\
                [self.itemEditDialogInstance.userTextBox.GetValue().strip() ,\
                self.itemEditDialogInstance.passwordTextBox.GetValue().strip()]
                #Add service name to service list
                self.serviceList.append(self.itemEditDialogInstance.serviceTextBox.GetValue().strip())
                #Refresh service list box with update service list
                self.serviceListBox.SetItems(self.serviceList)
            #Save items to file
            self.saveItems()
        except IndexError:
            pass
            
    #Function to write items to file
    def saveItems(self, event=None):
        #Open file and read to first line, past password, and truncate the rest of the file
        self.configFile = open("securewallet", "r+")
        self.configFile.readline()
        self.configFile.truncate()
        #Check if any items are present
        #If so, write to file
        if (len(self.serviceList) > 0):
            #Initialize empty buffer for the data
            dataBuffer = ""
            #For every item, encrypt it, and add to the buffer
            for serviceItem in self.serviceListFull:
                for serviceCharacter in serviceItem:
                    dataBuffer = dataBuffer + str(ord(serviceCharacter)+self.passNum) + ' '
                dataBuffer = dataBuffer + "\n"
                for serviceCharacter in self.serviceListFull[serviceItem][0]:
                    dataBuffer = dataBuffer + str(ord(serviceCharacter)+self.passNum) + ' '
                dataBuffer = dataBuffer + "\n"
                for serviceCharacter in self.serviceListFull[serviceItem][1]:
                    dataBuffer = dataBuffer + str(ord(serviceCharacter)+self.passNum) + ' '
                dataBuffer = dataBuffer + "\n"
            #Encrypt with password ASCII strings
            #Write the buffer and close the file handler
            self.configFile.write(dataBuffer)
        #Close file
        self.configFile.close()
        
    #Function to display service info in text box        
    def displayItemInfo(self, event=None, clearText=None):
        try:
            #Display selection if flag not set
            #Get item to display
            itemToDisplay = self.serviceListBox.GetString(self.serviceListBox.GetSelection())
            #Set value
            self.infoArea.SetValue("Username:\n" + self.serviceListFull[itemToDisplay][0] +\
            "\n" + "Password:\n" + self.serviceListFull[itemToDisplay][1])
        except:
            pass        
  
#Dialog for adding items    
class itemEditDialog(wx.Dialog):
    #Initialize function for dialog
    def __init__(self, parent , serviceText, usernameText, passwordText):
        #Initialize base dialog
        wx.Dialog.__init__(self, parent, 1, "Add Item", size=(350, 120))
        #Initialize service name label and input field
        self.serviceText = wx.StaticText(self, 2, "Service name:", (5,10))
        self.serviceTextBox = wx.TextCtrl(self, 3, serviceText,(100,0),(250,30))
        #Initialize username label and input field
        self.userText = wx.StaticText(self, 4, "Username:", (5,40))
        self.userTextBox = wx.TextCtrl(self, 5, usernameText,(100,30),(250,30))
        #Initialize password label, input field, and OK button
        self.passwordTet = wx.StaticText(self, 6, "Password:", (5,70))
        self.passwordTextBox = wx.TextCtrl(self, 7, passwordText,(100,60),(250,30))
        self.okButton = wx.Button(self,wx.ID_OK,"OK",(125,90),(100,30))
    
#Dialog for entering the password
class passWordDialog(wx.Dialog):
    #Initialize function for dialog
    def __init__(self, parent, title):
        wx.Dialog.__init__(self, parent, 1, title, size=(320,80))
        self.passwordBox = wx.TextCtrl(self,wx.ID_OK,'',(10,5),(300,30), style = wx.TE_PASSWORD)
        self.okButton = wx.Button(self,wx.ID_OK,"OK",(100,45),(100,30))
                
#Main app container for application frame
class secureWalletApp(wx.App):
    def OnInit(self):
        #Create instance of frame and start loop
        self.secureWalletInstance = secureWalletFrame()
        self.MainLoop()
        return True

#Start application        
secureWalletRunningInstance = secureWalletApp(0)