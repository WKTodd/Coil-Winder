###########################################
# ADT winder 
#
# W.K.Todd 24/03/2021
#
# settings json generator
# machine settings dialogue
#
###########################################
import json
from tkinter import Button, Entry, Frame, Label, LabelFrame, Menu, Tk
from tkinter import filedialog, messagebox, Radiobutton, StringVar
from tkinter.constants import LEFT, SUNKEN, BOTH

#from  HelixServo import PinchRollerLift, Feeder, Cutter

#------------------------------------


class MachineSet(Frame):
    filename="MachineSet.txt"
    _MS = {}
    child = False
    
    def __init__(self, master = None, child = False ):

        self.child = child

        #get settings from file
        try:
            with open(self.filename) as json_file:  
                self._MS = json.load(json_file)
        except:
            #if no file write defaults
            print("setting defaults")
            self.Set_Defaults()
            
        if not 'AdapterOffsets' in self._MS.keys():
            self._MS["AdapterOffsets"] ={
            'LongAdapterOffset':54.0,
            'ShortAdapterOffset':15.0,
            'Use':"SAO",
            }

        self.AOS = StringVar()
        self.master = master
        self.init_window()
        self.init_menu()
        self.init_widgets()

        self.master.focus_set()
        
            
    def init_window(self):
        
        self.master.title("Machine Settings")
        self.master.protocol('WM_DELETE_WINDOW',self.close)

        # set up the window size and position
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        window_width = screen_width/2
        window_height = screen_height/3.5
        window_position_x = screen_width/2 - window_width/2
        window_position_y = screen_height/2 - window_height/2
        self.master.geometry('%dx%d+%d+%d' % (window_width, window_height, window_position_x, window_position_y))
        

    def init_menu(self):
        #menu
        self.mnuBar = Menu(self.master)
        self.master.config(menu=self.mnuBar)
        self.mnuFile = Menu(self.mnuBar, tearoff=0)
        self.mnuFile.add_command(label="Open" , command = self.OpenFile)
        self.mnuFile.add_command(label="Save", command = self.SaveFile)
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

        self.tabfrm = LabelFrame(self.master, text='Machine Settings')
        
        lblCol1 = Label(self.tabfrm, text="Steps/Unit", justify=LEFT).grid( row=0, column=1)
        
        lblCol2 = Label(self.tabfrm, text="Home Distance", justify=LEFT,width=12).grid( row=0, column=2)
        lblCol3 = Label(self.tabfrm, text="Home Speed", justify=LEFT,width=12).grid( row=0, column=3)
        lblCol4 = Label(self.tabfrm, text="Zero Offset", justify=LEFT,width=12).grid( row=0, column=4)
        lblCol5 = Label(self.tabfrm, text="Zero Speed", justify=LEFT,width=12).grid( row=0, column=5)
        lblCol6 = Label(self.tabfrm, text="Max Speed", justify=LEFT,width=12).grid( row=0, column=6)
        lblCol7 = Label(self.tabfrm, text="Acc. Time (s)", justify=LEFT,width=12).grid( row=0, column=7)
        
        lblXsteps = Label(self.tabfrm, text="Spindle (Revs)", justify=LEFT).grid( row=1, column=0)
        lblYsteps = Label(self.tabfrm, text="Feeder (mm)", justify=LEFT).grid( row=2, column=0)

        #--- spindle row 1
        self.entXsteps = Entry(self.tabfrm,width=12)
        self.entXsteps.insert(0,self._MS['Spindle']['stepsperunit'])
        self.entXsteps.grid(row=1, column=1)

        self.entXHD = Entry(self.tabfrm,width=12)
        self.entXHD.insert(0,self._MS['Spindle']['homedistance'])
        self.entXHD.grid(row=1, column=2)

        self.entXHS = Entry(self.tabfrm,width=12)
        self.entXHS.insert(0,self._MS['Spindle']['homespeed'])
        self.entXHS.grid(row=1, column=3)

        self.entXZO = Entry(self.tabfrm,width=12)
        self.entXZO.insert(0,self._MS['Spindle']['zerooffset'])
        self.entXZO.grid(row=1, column=4)

        self.entXZS = Entry(self.tabfrm,width=12)
        self.entXZS.insert(0,self._MS['Spindle']['zerospeed'])
        self.entXZS.grid(row=1, column=5)

        self.entXMS = Entry(self.tabfrm,width=12)
        self.entXMS.insert(0,self._MS['Spindle']['maxspeed'])
        self.entXMS.grid(row=1, column=6)

        self.entXAccTm = Entry(self.tabfrm,width=12)
        self.entXAccTm.insert(0,self._MS['Spindle']['accelerationtime'])
        self.entXAccTm.grid(row=1, column=7)

        
        #---carriage row=2
        self.entYsteps = Entry(self.tabfrm,width=12)
        self.entYsteps.insert(0,self._MS['Feeder']['stepsperunit'])
        self.entYsteps.grid(row=2, column=1)

        self.entYHD = Entry(self.tabfrm,width=12)
        self.entYHD.insert(0,self._MS['Feeder']['homedistance'])
        self.entYHD.grid(row=2, column=2)

        self.entYHS = Entry(self.tabfrm,width=12)
        self.entYHS.insert(0,self._MS['Feeder']['homespeed'])
        self.entYHS.grid(row=2, column=3)
        
        self.entYZO = Entry(self.tabfrm,width=12)
        self.entYZO.insert(0,self._MS['Feeder']['zerooffset'])
        self.entYZO.grid(row=2, column=4)

        self.entYZS = Entry(self.tabfrm,width=12)
        self.entYZS.insert(0,self._MS['Feeder']['zerospeed'])
        self.entYZS.grid(row=2, column=5)

        self.entYMS = Entry(self.tabfrm,width=12)
        self.entYMS.insert(0,self._MS['Feeder']['maxspeed'])
        self.entYMS.grid(row=2, column=6)

        self.entYAccTm = Entry(self.tabfrm,width=12)
        self.entYAccTm.insert(0,self._MS['Feeder']['accelerationtime'])
        self.entYAccTm.grid(row=2, column=7)

        self.tabfrm.pack(fill= BOTH)
        
        adapfrm = self.init_adapterfrm()
        adapfrm.pack( fill=BOTH, pady=5)
        
        hintfrm = Frame(self.master,bd=1,relief=SUNKEN, ) #packed after table
        self.lblHint = Label(hintfrm, text="Hint Panel", justify='left', bg="khaki")
        self.lblHint.pack(side="bottom", fill='x', expand='no')
        hintfrm.pack( fill=BOTH, pady=5)
        
    def init_adapterfrm(self):
        adapfrm = LabelFrame(self.master, text ="Adapter settings" )
        SAlab = Label(adapfrm,text ="Short Home Offset")
        LAlab = Label(adapfrm,text ="Long Home Offset")
        
        self.entSAO = Entry(adapfrm,width=12)
        self.entLAO = Entry(adapfrm,width=12)
        self.entSAO.insert(0,self._MS['AdapterOffsets']['ShortAdapterOffset'])
        self.entLAO.insert(0,self._MS['AdapterOffsets']['LongAdapterOffset'])
        self.entSAO.bind("<FocusIn>",  self.Select) 
        self.entLAO.bind("<FocusIn>",  self.Select) 
        
        self.selSAO = Radiobutton(adapfrm, text="use short settings", variable = self.AOS, value ="SAO")
        self.selLAO = Radiobutton(adapfrm, text="use long settings",variable = self.AOS, value ="LAO")
        self.selSAO.bind("<FocusIn>",  self.Select) 
        self.selLAO.bind("<FocusIn>",  self.Select) 
        
        self.AOS.set(self._MS['AdapterOffsets']['Use'])
        SAlab.grid(row=0,column=0)
        self.entSAO.grid(row=0,column=1)
        LAlab.grid(row=1,column=0)
        self.entLAO.grid(row=1,column=1)
        self.selSAO.grid(row=0,column=2)
        self.selLAO.grid(row=1,column=2)
        return adapfrm        
    
    def Select(self, event):
        w=event.widget
        
        self.DisplayHint(w)
        
    def DisplayHint(self, widget):
        #update lblHint to reflect column use
        #Hint=""
        #if widget is self.entSAO:
        Hint="""For use with long or short adapters
            Enter the distance between side of case and centre of nozzle
            """
        # if widget is self.entLAO:
        #     Hint="""For use with long adapter
        #     Enter the distance between side of case and centre of nozzle"""
            
        # if widget is self.selLAO:
        #     Hint="""Use long adapter settings
        #     Remember to save setting before exit"""        
        # if widget is self.selSAO:
        #     Hint="""Use short adapter settings
        #     Remember to save setting before exit"""    
            
        self.lblHint.config(text=Hint)

    def close(self):
        #app is closing
        if self.child:
            self.master.destroy()
        else:
            if messagebox.askyesno("Exit Application", "Do you really want to end this application?", icon="warning"):
                self.master.destroy()

    def SaveFile(self):
        #save file as JSON
        #copy entries to dictionary
        self._MS['Spindle'] = {
            'stepsperunit' : float(self.entXsteps.get()),
            'homedistance' : float(self.entXHD.get()),
            'homespeed' : float(self.entXHS.get()),
            'zerooffset' : float(self.entXZO.get()),
            'zerospeed' : float(self.entXZS.get()),
            'maxspeed' : float(self.entXMS.get()),
            'accelerationtime' :float(self.entXAccTm.get()),
        }


        self._MS['Feeder'] = {
            'stepsperunit': float(self.entYsteps.get()),
            'homedistance' : float(self.entYHD.get()),
            'homespeed' : float(self.entYHS.get()),
            'zerooffset' : float(self.entYZO.get()),
            'zerospeed' : float(self.entYZS.get()),
            'maxspeed' : float(self.entYMS.get()),
            'accelerationtime' :float(self.entYAccTm.get()),
        }

        self._MS["AdapterOffsets"] ={
            'LongAdapterOffset':float(self.entLAO.get()),
            'ShortAdapterOffset':float(self.entSAO.get()),
            'Use':self.AOS.get()
            }

        
        self.save_settings(self.filename)
            
    def OpenFile(self):
        self.filename = filedialog.askopenfilename(initialdir="/", title="Select file",
                                                  filetypes=(("Settings files", "*.txt"), ("all files", "*.*")))
        #get settings from file
        try:
            with open(self.filename) as json_file:  
                self._MS = json.load(json_file)
        except:
            messagebox.showwarning("Open File", "File error?", icon="warning")


    def Set_Defaults(self):
        
        
        self._MS['Feeder'] = {
            'stepsperunit' : 135,
            'homedistance' : -65,
            'homespeed' : 500,
            'zerooffset' : 10,   
            'zerospeed' : 300,
            'maxspeed' : 500,
            'accelerationtime' : 2,
        }


        self._MS['Spindle'] = {
            'stepsperunit': 400,
            'homedistance' : -1,
            'homespeed' : 30,
            'zerooffset' : 1,
            'zerospeed' : 10,
            'maxspeed' : 1500,
            'accelerationtime' : 2,
        }

        self._MS["AdapterOffsets"] ={
            'LongAdapterOffset':54.0,
            'ShortAdapterOfffset':15.0,
            'Use':"SAO",
            }


    def save_settings(self, filename):

         with open(filename, 'w') as outfile:  
             json.dump(self._MS, outfile)

    def Revert(self):
        #reload entry boxes
        self.init_widgets()

    def DisplayHint(self, column):
        #update lblHint to reflect column use
        Hint=""
        if column=="wire":
            Hint = """Wire Diameter:

Enter actual wire diameter (including coating) in millimetres """
            

        elif column == "turns":
            Hint = """ """

        self.lblHint.config(text=Hint)

#-----------------------------------------------
if __name__ == '__main__':
     
    root=Tk()

    app = MachineSet(root)


    root.mainloop()               






