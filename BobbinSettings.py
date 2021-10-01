###########################################
# ADT winder 
#
# W.K.Todd 24/03/2021
#
# settings json generator
# bobbin settings dialogue
#
###########################################
#import json
import pickle
from tkinter import Button, Entry, Frame, Label, LabelFrame, Menu,Spinbox, Tk
from tkinter import filedialog, messagebox,  StringVar , Toplevel#, ttk
from tkinter.constants import LEFT,RIGHT,TOP,BOTTOM,SUNKEN,BOTH,N #,RIDGE,  S,W,E
#from tkinter import ttk
from PIL import Image, ImageTk
from os import listdir
from pathlib import Path

#------------------------
class Bobbin(object):
    '''winder bobbin object'''

    InternalWidth = 0.0
    MaxLayerHeight = 0.0
    CoreDiameter = 0.0
    CoreHeight =0.0
    CoreDepth = 0.0
    AdapterOffset = 0.0 #eg. 21.0mm from inside edge to frame 
    Type = 0
    _imagefile = ""


    #Image = None
    
    def __init__(self, Type):
        self.Type = Type
        #get bobbin params from file
        pass
    def __del__(self):
        pass

    def SetImage(self, filename):
        self._imagefile = filename

    def CorePerimeter(self):
        if self.CoreDiameter >0:
            CP = 3.14159 * self.CoreDiameter
        else:
            CP = (2*self.CoreHeight) + (2*self.CoreDepth)
        return CP

    
#------------------------------------
    
class BobbinGUI(Frame):
    
    '''Bobbin hareware display frame'''
    filename="BobbinSet.pkl"
    Bobbins=[]
    Bimages = {}
    currentimage =0
    CBobbin = None
    _ImageSize = (120,120)

    
    def __init__(self, master, App = None, Editable = False):
        self.master = master
        self.EditMode = Editable
        self.app = App
        if not self.EditMode:
            #use small picture
            self._ImageSize = (80,80)


        self.init_Bobbins() 
        self.GetBobbinImages()
        self.init_widgets(self.EditMode)
        self.master.focus_set()
        #show first bobbin
        self.CBobbin = self.Bobbins[0]
        self.ShowBobbin()
    
    def init_Bobbins(self):
        #get settings from file
        try:
            with open(self.filename,'rb') as infile:  
                self.Bobbins = pickle.load(infile)
                    
        except:
            print("Error loading Pickle")

            #if no file write defaults
            
            self.Set_Defaults()
            
    def StateStr(self, enable):
        if enable:
            State = "normal"
        else:
            State = "readonly"
        return State


    def init_widgets(self, Edit = False):

        State = self.StateStr(Edit)                    
        #create a frmae for table
        self.frmTable = Frame(self.master)
        self.frmTable.pack(side=LEFT)
        
        self.lblCol1 = Label(self.frmTable, text="Type",
                             justify=LEFT, width = 14).grid(row=0,
                                                            column=0,
                                                            pady=0, 
                                                            padx=0, 
                                                            sticky=N)

        self.Blist=[]
        for B in self.Bobbins:
            self.Blist.append(B.Type)     
        
        self.CBobbin = self.Bobbins[0]
        self.SelectedBob = self.CBobbin.Type

        self.typevar = StringVar(value = "0")
        
        self.entType = Spinbox(self.frmTable,
                               width=12,
                               values=self.Blist,
                               command=lambda : self.SelectBobbin(),
                               state ="readonly",
                               textvariable = self.typevar
                               )                               

        self.entType.grid(row=0, column=1,pady=0, padx=0, sticky=N)
        
        
        self.lblCol1 = Label(self.frmTable, text="Width", justify=LEFT, width = 14).grid( row=1, column=0,pady=0, padx=0, sticky=N)

        self.widthvar = StringVar(value ="0.0")
        self.entWidth = Entry(self.frmTable,width=14, state = State, textvariable = self.widthvar)
        #self.entWidth.insert(0,self._MS['Type1']['maxwidth'])
        self.entWidth.grid(row=1, column=1)
        self.entWidth.bind("<FocusOut>", self.UpdateCurrentBobbin)
                                                                                     
        self.lblCol2 = Label(self.frmTable, text="Max Layer height", justify=LEFT,width=14).grid( row=2, column=0)
        self.mlhvar = StringVar(value ="0.0")
        self.entMLH = Entry(self.frmTable,width=14, state = State, textvariable = self.mlhvar)
        #self.entMLH.insert(0,self._MS['Type1']['maxlayerheight'])
        self.entMLH.grid(row=2, column=1)
        self.entMLH.bind("<FocusOut>", self.UpdateCurrentBobbin)
        
        self.lblCol3 = Label(self.frmTable, text="Adapter Offset", justify=LEFT,width=14).grid( row=3, column=0)
        self.adpvar = StringVar(value="0.0")
        self.entAdp = Entry(self.frmTable,width=14, state = State, textvariable = self.adpvar)
        self.entAdp.grid(row=3, column=1)
        self.entAdp.bind("<FocusOut>", self.UpdateCurrentBobbin)

        self.lblCol4 = Label(self.frmTable, text="Image File", justify=LEFT,width=14)
        self.filevar = StringVar(value="filename")
        self.entImage = Entry(self.frmTable,width=14, state = State, textvariable = self.filevar)
        self.entImage.bind("<FocusOut>", self.UpdateCurrentBobbin)
        if Edit:
            self.lblCol4.grid( row=4, column=0)
            self.entImage.grid(row=4, column=1)

##        self.imgES=Image.open("bobbintype1.gif")
##        resized = self.imgES.resize((120,120),Image.ANTIALIAS)
##        self.RI = ImageTk.PhotoImage(resized)
        

        # create image frame
        self.frmImg =Frame(self.master)
        self.frmImg.pack(side=RIGHT, pady=2, padx=10)

        self.labImg = Label(self.frmImg, text = "place holder", relief =SUNKEN)
        self.labImg.pack(side=LEFT)

        self.btnUP = Button(self.frmImg, text ="Prev",   command =  self.PrevImage)
        
        self.btnDWN = Button(self.frmImg, text = "Next", command =  self.NextImage)
        if Edit:
            self.btnUP.pack(side=TOP)
            self.btnDWN.pack(side=BOTTOM)
       
        self.UpdateBobbinImage(self.currentimage)
    
    def refresh_Blist(self):
        self.init_Bobbins()
        self.Blist=[]
        for B in self.Bobbins:
            self.Blist.append(B.Type)  
        self.entType.config(values = self.Blist)
        
    def UpdateCurrentBobbin(self,event):
        #save enties to current bobbin
        #self.CBobbin.Type = self.entType.get()
        self.CBobbin.InternalWidth = float(self.entWidth.get())
        self.CBobbin.MaxLayerHeight =float(self.entMLH.get())
        self.CBobbin.AdapterOffset = float(self.entAdp.get())
        self.CBobbin.SetImage(self.entImage.get())
        
    def SelectBobbin(self, Sel=None):
        self.UpdateCurrentBobbin(0)

        if not Sel:
            Sel = int(self.entType.get())
        
        for B in self.Bobbins:
            #print(B.Type, B.InternalWidth)
            if B.Type == Sel:
                self.CBobbin = B

        self.ShowBobbin()
        if self.app : self.app.BobbinChanged()

    def NextImage(self):
        self.currentimage += 1
        self.currentimage = self.currentimage % len(self.Bimages)
        self.UpdateBobbinImage(self.currentimage)
        
        
    def PrevImage(self):
        self.currentimage -= 1 
        self.currentimage = self.currentimage % len(self.Bimages)
        self.UpdateBobbinImage(self.currentimage)
        
    def UpdateBobbinImage(self, typenumber):
        BK = list(self.Bimages.keys())
        self.ShowImagefile(BK[typenumber])
        self.currentimage = typenumber


    def ShowImagefile(self,imagefile):
        try:
            resized = self.Bimages[imagefile].resize(self._ImageSize,Image.ANTIALIAS)
        except:
            resized = self.Bimages["bobbintype1.gif"].resize(self._ImageSize,Image.ANTIALIAS)
            
        self.RI = ImageTk.PhotoImage(resized)

         
        self.labImg.config(image=self.RI)
        self.labImg.pack(side=LEFT)
        self.filevar.set(imagefile)

            
    def GetBobbinImages(self):
        #open all bobbintypex.gif files and save object to Bimages
        imagespath = str(Path.cwd().joinpath('Images') )
        for i in listdir(imagespath):
            if "bobbintype" in i:
                #try:
                    self.Bimages[i] = Image.open(imagespath + '/'+ i) #.resize((120,120),Image.ANTIALIAS).convert('1')
                #except:
                #    pass
        #print(self.Bimages)
                
    def NewBobbin(self):
        self.UpdateCurrentBobbin(0)
        BK = list(self.Bimages.keys())
        NB = Bobbin(len(self.Bobbins)+1)
        NB.SetImage(BK[0]) #default image
        self.Bobbins.append(NB)
        self.CBobbin = NB
        self.ShowBobbin()
        self.Blist.append(NB.Type)
        self.entType.configure(values = self.Blist, state="normal")
        self.entType.delete(0,"end")
        self.typevar.set(NB.Type)
        self.entType.configure( state="readonly")
        
    def DeleteBobbin(self):
        root = Tk()
        TL = Toplevel(root)
        if messagebox.askyesno("Delete Current Bobbin", "Do you really want to delete this Bobbin?",
                               icon="warning",
                               parent = TL):
            #remove from Blist and Bobbins
            self.Blist.remove(self.CBobbin.Type)
            self.Bobbins.remove(self.CBobbin)
            self.entType.config(values = self.Blist)
        
    def ShowBobbin(self):
        #display current Bobbin
        self.Unlock(True)
        self.typevar.set(self.CBobbin.Type)
        self.widthvar.set(self.CBobbin.InternalWidth)
        self.mlhvar.set(self.CBobbin.MaxLayerHeight)
        self.adpvar.set(self.CBobbin.AdapterOffset)
        
        if self.CBobbin._imagefile:
            self.ShowImagefile(self.CBobbin._imagefile)
        self.Unlock(self.EditMode)


    def Unlock(self, enable):
        State = self.StateStr(enable)
        self.entType.config(state = State)
        self.entWidth.config(state = State)
        self.entMLH.config(state = State)
        self.entAdp.config(state = State)
        self.entImage.config(state = State)
        
    def Set_Defaults(self):
        self.CBobbin = Bobbin(0)
        self.Bobbins.append(self.CBobbin)


#------------------------------------
class BobbinSet(Frame):

    _MS = {}
    child = False

    def __init__(self, master = None, child = False ):

        self.child = child
        self.master = master
        self.init_window()
        self.init_menu()

        self.init_widgets()
        
            
    def init_window(self):
        
        self.master.title("Bobbin Settings")
        self.master.protocol('WM_DELETE_WINDOW',self.close)

        # set up the window size and position
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        window_width = screen_width/2
        window_height = screen_height/5
        window_position_x = screen_width/2 - window_width/2
        window_position_y = screen_height/2 - window_height/2
        self.master.geometry('%dx%d+%d+%d' % (window_width, window_height, window_position_x, window_position_y))
        

    def init_menu(self):
        #menu
        self.mnuBar = Menu(self.master)
        self.master.config(menu=self.mnuBar)
        self.mnuFile = Menu(self.mnuBar, tearoff=0)
        self.mnuFile.add_command(label="New" , command =self.NewBobbin)
        self.mnuFile.add_command(label="Delete" , command = self.DeleteBobbin)
        self.mnuFile.add_separator()
        self.mnuFile.add_command(label="Open" , command =self.OpenFile)
        self.mnuFile.add_command(label="Save", command =self.SaveFile)
        self.mnuFile.add_separator()
        self.mnuFile.add_command(label="Revert", command = self.Revert)
        self.mnuFile.add_separator()
        self.mnuFile.add_command(label="Exit", command = self.close)
        self.mnuBar.add_cascade(label="File", menu = self.mnuFile)

        self.mnuEdit = Menu(self.mnuBar, tearoff=0)
        self.mnuEdit.add_command(label="Undo")
        self.mnuEdit.add_separator()
        self.mnuEdit.add_command(label="Cut")
        self.mnuEdit.add_command(label="Copy")
        self.mnuEdit.add_command(label="Paste")
        self.mnuBar.add_cascade(label="Edit", menu=self.mnuEdit, state="disabled")

        

    def init_widgets(self):
        hardware = LabelFrame(self.master,bd=1, relief=SUNKEN, padx=2, pady = 2, text='Hardware')
        self.BG = BobbinGUI(master = hardware,
                            App = self,
                            Editable = True,
                            )
        hardware.pack(fill=BOTH)

    def NewBobbin(self):
        self.BG.NewBobbin()
        
    def DeleteBobbin(self):
        self.BG.DeleteBobbin()

    def BobbinChanged(self):
        #print("bobbin changed")
        pass

    def close(self):
        #app is closing
        if self.child:
            if messagebox.askyesno("Save Changes", 
                                   "Save changes to Bobbins?",
                                   icon="warning"):
                self.SaveFile()
            self.master.destroy()
        else:
            if messagebox.askyesno("Exit Application", 
                                   "Do you really want to end this application?", 
                                   icon="warning"):

                  self.master.destroy()

        
        
#========================== file io ==================


    def SaveFile(self):
        #save file as JSON
        #copy entries to dictionary

        self.save_settings(self.BG.filename)
            
    def OpenFile(self):
        initpath = str(Path.cwd())
        self.filename = filedialog.askopenfilename(initialdir=initpath, title="Select file",
                                                  filetypes=(("Settings files", "*.pkl"), ("all files", "*.*")))
        #get settings from file
        try:
            with open(self.filename,'rb') as infile:  
                self.BG.Bobbins = pickle.load( infile)
        except Exception as e:
            messagebox.showwarning("Open File", "File error?:", str( e), icon="warning")



    def save_settings(self, filename):

        with open(filename, 'wb') as outfile:
             print(filename , self.BG.Bobbins)
             #json.dump(self.Bobbins, outfile)
             pickle.dump(self.BG.Bobbins, outfile, pickle.HIGHEST_PROTOCOL )
             
            

    def Revert(self):
        #reload entry boxes
        self.init_widgets()



#-----------------------------------------------
if __name__ == '__main__':
     
    root=Tk()

    app = BobbinSet(root)


    root.mainloop()               






