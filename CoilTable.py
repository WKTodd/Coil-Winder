################################
# ADT winder Table Object
#
# W.K.Todd 25/03/19
#
################################

from tkinter import Label, Entry, Frame
from tkinter import filedialog, messagebox, ttk
from tkinter.constants import *


#--------------------------
class CoilForm(object):

    def __init__(self, turns, wirediameter, layers, SP, RPM, width , offset):
        self.Turns = turns
        self.Pitch = wirediameter
        self.Layers = layers
        self.StartPos =  SP
        self.Feedtoleft = "R" in SP
        self.RPM =RPM
        self.Width = width
        self.Offset = offset
#----------------------------
class CoilTable(object):

    TurnsRowIndex=[]
    Table= []
    ColLabels = ["","Turns", "Wire(mm)","Coil Width", "Offset","Layers", "Start Pos" , "RPM","Comment"]
    ColNames = ['turns','wire', 'width' , 'offset', 'layers', 'start','RPM','comment']
    ColWidths = [8,8,8,8,8,8,8,20]
    RowLabels = ["Section 1"] # ,"Start Marker", "Main Coil section A","Main Coil section B" ,"End Marker", "Termination"]
    RowNames = ['StartConnect'] #,'StartMarker','MainCoilA','MainCoilB', 'EndMark', 'Termination']
    RowLabs =[]
    CurrentRow = None
    CurrentHLR = None
    Coil=[]
    CoilTurns=0
    CoilHeight = 0
    TableLock = False
    


    
    def __init__( self, master = None, Winder=None, menu = None, mnuTable = None, lblHint = None):
        self.master = master
        self.mnuBar = menu
        self.mnuTable = mnuTable
        self.lblHint = lblHint
        self.init_table()
        self.winder = Winder
        self.CLlab = Label(self.master, text = "Overall Coil Length")
        #self.CLlab.grid(row = len(self.Table)+1, column=0 , columnspan=2)
        
        self.CTTlab = Label(self.master, text = "Total Turn Count")
        #self.CTTlab.grid(row = len(self.Table)+2, column=0 , columnspan=2)
        
        self.lock_table(self.TableLock)


    def init_table(self):

        if self.Table != None:
            self.Table.clear()


        #label axes
        for colno in range(len(self.ColLabels)): #row 0
            clab= Label(self.master, text = self.ColLabels[colno], justify=LEFT,width = self.ColWidths[colno-1]).grid( row = 0, column=colno)

        
        for rowno in range(len(self.RowLabels)):
            rlab = Label(self.master, text=self.RowLabels[rowno], justify=LEFT)
            rlab.grid( row = rowno +1, column= 0) #column0
            rlab.bind("<Button-1>",  self.SelectRow)
            self.RowLabs.append(rlab)
 

        for i in range(len(self.RowNames)):
            Cols=[]
            for j in range(len(self.ColNames)):
                e = Entry(self.master, width= self.ColWidths[j], relief=RIDGE)
                e.grid(row=i+1, column=j+1, sticky=NSEW)
                e.bind("<FocusIn>",  self.SelectOnTable)
                e.bind("<FocusOut>", self.DeselectTable)
                #e.bind("<Key>", self.keybind1)
            
                Cols.append(e)
            
        self.Table.append(Cols)

    def clear_table(self):
        widgets = self.master.winfo_children()
        if len(widgets) >0:
            for widget in widgets:
                widget.grid_remove()   
        

    def build_table(self, MS = None ): 

        self.clear_table()                    

        #build table from _MS['Windings']
        self.init_table()

        TV = MS['Windings'] #table values
        nocols = len(self.ColNames) #number of columns
        #print(TV)
        self.CurrentRow = self.Table[0]
        for i in range(len(TV)-1): #build table grid
            self.InsertSection()
        for r in range(len(TV)):   
            for c in range(nocols):
                self.Table[r][c].delete(0,'end')
                self.Table[r][c].insert(0,TV[r][c])
        self.lock_table(self.TableLock)
        

    def lock_table(self, Lock = True):
        for R in self.Table:
            for C in R:
 
                if Lock:
                    C.config(state = "readonly")
                    
                else:
                    C.config(state = "normal")
        self.TableLock = Lock
        if Lock:
            self.lblHint.config(text ="Table Locked: use 'Menu/Table/Protect table' to release")
        else:
            self.lblHint.config(text ="Table Unlocked")
            self.HighLightOff()

#=========================Table editing section

    def InsertSection(self):
        #insert new blankrow
       
        i= self.Table.index(self.CurrentRow) + 1


        Cols=[]
        for j in range(len(self.ColNames)-1):
            e = Entry(self.master, width= self.ColWidths[j], relief=RIDGE) #,  fg = "blue")
            
            e.bind("<FocusIn>",  self.SelectOnTable)
            e.bind("<FocusOut>", self.DeselectTable)
            #e.bind("<Key>", self.keybind1)
            Cols.insert(i,e)

        #insert comment box
        e = Entry(self.master, width= self.ColWidths[j], relief=RIDGE)
        e.bind("<FocusIn>",  self.SelectOnTable)
        e.bind("<FocusOut>", self.DeselectTable)
        Cols.insert(i,e)
        
        Cols[0].focus_set()            
        self.Table.insert(i, Cols)
        self.CurrentRow = Cols
        
        #section label is appended to end
        lp = len(self.Table) 
        rlab = Label(self.master, text="Section " + str(lp), justify=LEFT)
        rlab.bind("<Button-1>",  self.SelectRow)
        rlab.grid( row = lp, column= 0)
        self.RowLabs.append(rlab)
        self.RegridTable()

    def keybind1 (self,event):
        v = event.char
        try:
            v = int(v)
        except ValueError:
            if v!="\x08" and v!="" and v not in ".":
                return "break"


    def RegridTable(self): #shuffle grid
        i = len(self.Table)
        nocols = len(self.ColNames)
        iolaycol = self.ColNames.index("layers") #index of layers column
        if i > 1:
            for r in range(i):
                for c in range(nocols):
                    self.Table[r][c].grid(row = r+1, column =c+1,sticky=NSEW)
                    self.Table[r][c].config(width= self.ColWidths[c])
                    self.CTTlab.grid(row = len(self.Table)+1, column=0 , columnspan=2, sticky='W')
                    self.CLlab.grid(row = len(self.Table)+1, column=iolaycol, columnspan=3, sticky='W')
            #enable delete option
            self.mnuTable.entryconfig("Delete Section", state = 'normal')
                    
        else:
            #disable delete option
            self.mnuTable.entryconfig("Delete Section", state = 'disable')
        

    def InsertMarker(self):
        #insert new marker
        self.InsertSection()
        marker = [7,0.3,0,1.0,2.1,"Marker"]
        for i in range(len(marker)):
            self.CurrentRow[i].insert(0, marker[i])


    
    def InsertTerm(self):
        #insert new termination
        self.InsertSection()
        term = [30,0.5,0,1.0,10,"Termination"]
        for i in range(len(term)):
            self.CurrentRow[i].insert(0, term[i])

    def DelSection(self):
        #delete current row
        NF = self.Table.index(self.CurrentRow) -1 #new focus
        if NF >=0:
            self.Table[NF][0].focus_set()
            
            for e in self.CurrentRow:
                e.grid_remove()
            
            self.Table.remove(self.CurrentRow)
            self.RegridTable()
            ld = self.RowLabs.pop()
            #print(self.RowLabs, ld)
            ld.grid_remove()

        
    def SelectOnTable(self, event):
        # called on entry focus -  stores current location
        w = event.widget
        for Row in self.Table:
            if w in Row:
                self.CurrentRow = Row
                self.mnuBar.entryconfig('Table', state = 'normal')
                if self.TableLock == True:
                    self.HighLightOnTable(Row)
                elif Row is self.Table[0]:
                   self.mnuTable.entryconfig("Delete Section", state = 'disable')
                elif self.TableLock == False:
                    self.mnuTable.entryconfig("Delete Section", state = 'normal')
                    self.HighLightOff()

                self.DisplayHint(self.ColNames[Row.index(w)])
          

    def D_State(self, Lock):
        if Lock:
            return "readonly"
        else:
            return "normal"

    def HighLightNext(self):
        if self.CurrentHLR == None:
            #highlight first row
            self.HighLightOnTable(self.Table[0])
        else:
            #highlight next row
            I = self.Table.index(self.CurrentHLR) +1
            if I >= len(self.Table):
                self.HighLightOff()
            else:
                self.HighLightOnTable(self.Table[I])
        

    def HighLightOff(self):
        for R in self.Table:
            for C in R:
                C.config(background='white', state = self.D_State(self.TableLock))
        self.CurrentHLR = None
                   
    def HighLightOnTable(self, Row):
        if not self.CurrentHLR is Row:
            self.HighLightOff()
            self.CurrentHLR = Row
            #highlights selected row
            if  Row != None:
                for C in Row:
                    C.config(background = "yellow", state ="normal")
 
    def SelectRow(self,event):
        w = event.widget
        #print(w["text"])
        rowno = int(w["text"][-2:]) -1
        self.HighLightOnTable(self.Table[rowno])
            
                
    def DeselectTable(self,event):
        
        self.CurrentRow = None
        #disable Table Menu
        self.mnuBar.entryconfig('Table' ,state = 'disabled')
        self.Recalc()
        self.lblHint.config(text="")


    def Recalc(self):
        #calculate overall length
        totlay=0
        totturns = 0
        totlayheight =0
        self.TurnsRowIndex.clear()
        iolaycol = self.ColNames.index("layers") #index of Length column
        ioturnscol = self.ColNames.index("turns")
        iowirecol = self.ColNames.index("wire")
        iowidthcol = self.ColNames.index("width")
        iooffsetcol= self.ColNames.index("offset")
        bobwidth = self.winder.Bobbin.InternalWidth #get bobbin width 
#        try:
        for r in self.Table:
            if not  r[ioturnscol].get():
                turns =0
            else:
                turns = float(r[ioturnscol].get())
                
            if  not r[iowirecol].get():
                wirediameter =0
            else:
                wirediameter = float(r[iowirecol].get()) #wire width
                turnsperlayer = int(bobwidth/wirediameter)
                layers = turns / turnsperlayer
                totlayheight += layers * wirediameter
                #print(turnsperlayer, layers)
                r[iolaycol].delete(0,'end')
                r[iolaycol].insert(0, '{0:.2f}'.format(layers))

                r[iowidthcol].delete(0,'end')
                r[iowidthcol].insert(0, '{0:.2f}'.format(bobwidth-wirediameter))
                r[iooffsetcol].delete(0,'end')
                r[iooffsetcol].insert(0, '{0:.2f}'.format(wirediameter/2))
                                   
                if float(r[iowidthcol].get()) == bobwidth - wirediameter:
                    r[iowidthcol].config(fg = "BLACK")
                else:
                    r[iowidthcol].config(fg = "RED")
                    Hint = """Warning:

The selected Bobbin has been changed and the current 'Coil Width' setting may be incorrect.
Coil Width cannot be changed while table is protected - use 'Table' menu to unprotect table settings """
                    self.lblHint.config(text=Hint)

                
                

                    
##        except Exception as e:
##            print("error in CoilTable.Recalc",e)
##            pass
        self.CLlab.config(text= " Overall layer height (mm): {0:.2f}".format(totlayheight))
        
        
        #check if coil too long
        if totlay >= self.winder.Bobbin.MaxLayerHeight :
            self.CLlab.config(fg="red")

        else:
            self.CLlab.config(fg="black")
            

        self.CTTlab.config(text= "  Total Turn Count: {0:.1f}".format(totturns))    
        self.CoilTurns = totturns
        self.CoilHeight = totlay

    def GetCoilList(self):
        #get a text list of coils for json
        CoilList=[]
        for Row in self.Table:
            Section=[]
            for Cel in Row:
                Section.append(Cel.get())
            CoilList.append(Section)
        
        return CoilList


    def GetCoilObject(self):
        #generate Coil[ turns, wirediameter, layers] list
        #print(self.CurrentRow)
        if self.CurrentHLR == None:
            self.HighLightNext()
            
        iolaycol = self.ColNames.index("layers") #index of Length column
        ioturnscol = self.ColNames.index("turns")
        iowirecol = self.ColNames.index("wire")
        ioSPcol = self.ColNames.index("start")
        ioRPMcol = self.ColNames.index("RPM")
        iowidthcol = self.ColNames.index("width")
        iooffsetcol = self.ColNames.index("offset")

        try:

            turns = float(self.CurrentHLR[ioturnscol].get())
            wirediameter = float(self.CurrentHLR[iowirecol].get())
            layers = float(self.CurrentHLR[iolaycol].get())
            RPM =  float(self.CurrentHLR[ioRPMcol].get())
            SP = self.CurrentHLR[ioSPcol].get()
            width = float(self.CurrentHLR[iowidthcol].get())
            offset = float(self.CurrentHLR[iooffsetcol].get())
            
            Coil = CoilForm(turns, wirediameter, layers, SP.upper(), RPM, width , offset)
           
        except Exception:
            Coil = None
            
        return Coil #object
        
    def DisplayHint(self, column):
        #update lblHint to reflect column use
        Hint=""
        if column=="wire":
            Hint = """Wire Diameter:

Enter actual wire diameter (including coating) in millimetres """
            

        elif column == "turns":

            Hint="""Turns:

Enter the number of turns for this section of the coil. (e.g. 84.2) """

        elif column=="width":
            Hint="""Coil Width:

Width of coil on the bobbin - usually the bobbin width minus the wirediameter ,but can be adjusted during wind for best fit"""

        elif column=="offset":
            Hint="""Coil Offset:

Position of coil offset from edge of bobbin - usually half the wire diameter bet can be set to allow
multiple coils side by side
(can be adjusted during wind) """

        elif column == "layers":
            Hint="""Layers:

The number of layers is calculated from the turns, bobbin width and wire diameter.  """

        elif column=="start":
            Hint="""Start position:

Start Left,Right or Cont (continue from previous coil)  """

        elif column=="RPM":
            Hint="""Winding Speed (RPM):

Enter speed between 0 and {} RPM  to suit wire size
RPM x Wire Diameter must not exceed maximum feeder speed of {}mm/min
""".format(int(self.winder.Spindle.MaxSpeed),int(self.winder.Feeder.MaxSpeed))         

        elif column=="comment":
            Hint="""Comment:

Enter a brief description of the coil section. (e.g. Input) """

        self.lblHint.config(text=Hint)

#==================================================


        
