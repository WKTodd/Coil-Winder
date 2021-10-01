# utility file objects
# Ini - reads and saves settings list
# RecentFiles  - maintains list of recent files , provides truncated path etc.
# FileObject - opens and saves files provides path etc.

#---------------------------------------------------------

import os.path
import json
import time
from datetime import date
from tkinter import filedialog, messagebox, ttk

class Ini(object):
    '''Ini file object to save and store settings list'''

    settings=None
    appname =""
    path = ""

    def __init___(self, Appname, Path):
        self.appname = Appname
        self.path = Path
        #open inifile
        try:
            with open(self.appname +'.ini') as json_file:
                self.settings=json.load(json_file)
        except Exception as e:
            print(e)
        
    def __del__(self):
        #save ini file
        with open(self.appname +'.ini' , 'w') as outfile:  
             json.dump(self.settings, outfile)

    def __repr__(self):
        return 'Ini file object'


#---------------------------------------------------------    

class RecentFiles(object):
    recentfiles = []
    currentfile = []
    
    def __init___(self):
        pass
    
    def __del__(self):
        pass

    def __repr__(self):
        return 'Recent Files Object'

    def OpenIndex(self, Index):
        self.OpenFile(self.RecentFiles[Index])

    def Add(self, filename):
       
        self.recentriles.insert(0,filename)
        if len(self.recentfiles) >4:
            self.recentfiles.pop()

#---------------------------------------------------------    

class JSONFile(object):

    name=None
    filetype = "Settings files"
    extension = ".job"
    defaultpath =""
    _MS = None
    def __init___(self):
        self._filedialog
        pass
    
    def __del__(self):
        pass

    def __repr__(self):
        return 'File Object'    
    
    def Open(self, filename =""):
        if filename =="":    
            self.filename = filedialog.askopenfilename(initialdir=self.defaultpath, title="Select file",
                                                  filetypes=((self.filetype, "*" + self.extension), ("all files", "*.*")))
        else:
            self.filename = filename
            
            
        #get settings from file
        try:
            with open(self.filename) as json_file:  
                self._MS = json.load(json_file)
        

                self.AddToRecent(self.filename)
                self.defaultpath = os.path.dirname(self.filename)
                
        except Exception as e:
            print(e)
            messagebox.showwarning("Open File", "File error: " + e , icon="warning")
            
        
        
    def SaveFile(self):
        if self.filename =="":
            self.SaveAsFile()
        else:
            self.save_settings()            

    def SaveAsFile(self, filename = ""):

        filename = filedialog.asksaveasfilename(initialdir="/", title="Select file",
                                                filetypes=((self.filetype, "*" + self.extension), ("all files", "*.*")))
        
        file_name, file_ext = os.path.splitext(filename) 
        
        if file_ext =='' :
            filename +=self.extension
            
        self.save_settings(filename)
        self.AddToRecent(filename)

    def save_settings(self, filename =None):


        if filename == None:
            filename = self.filename
        elif not filename == "":
            self.filename = filename


        with open(filename , 'w') as outfile:  
             json.dump(self._MS, outfile)
        title = "Job Settings - {}".format(filename)
        self.master.title(title)

    def data(self):
        return self._MS
