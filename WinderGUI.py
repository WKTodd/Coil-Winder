###########################################
# ADT winderGUI object
#
# W.K.Todd 18/10/2020
#
# winding machine GUI object
AppTitle = "Winder"
AppVersion  = "V1.22"
#
###########################################


#tkinter routines for winder GUI
from CoilTable import CoilTable
from WinderSettings import MachineSet
from BobbinSettings import  BobbinGUI, BobbinSet #, Bobbin,
import json
#import time
from datetime import date
from tkinter import Button, Entry, Frame, Label,LabelFrame, Menu, Tk,Toplevel
from tkinter import filedialog, messagebox, ttk, BooleanVar,PhotoImage
from tkinter.constants import LEFT,RIGHT,TOP,BOTTOM,SUNKEN,BOTH,RIDGE #,N,S,W,E
#from pathlib import Path
import os.path
import os
from WindingGUI import ControlForm
from OptionalDisplay import OLED
#from FileUtilities import *

from OptionalButton import PiButton    #rename file NoOptionalButtons.py to OptionalButtons.py if no buttons

class window(Frame):
    filename=""
    defaultpath = "/"
    #Coil = [] # Coil section list [Turns, Pitch]
    _MS = {}
    _Ini={}
    RecentFiles= []
    OpenPrevFile = True
    Bobbin = None #Bobbin(1)
    
    def __init__(self, master = None, Winder = None):
        Frame.__init__(self,master)
        self.master=master
        self.winder = Winder
        self.Debug = BooleanVar()
        self.PT = BooleanVar() #protect table
        self.PT.set(True)
        #if Winder is not None:            
            #self.Coil = Winder.Coil
        
        self.LoadIniFile()
        #self.rec_dicts(self.master._MS,self.master.Default_Set)
        
        
        self.SetDefaults()
        self.init_window()
        self.init_menu()
        self.init_widgets()
        self.winder.Bobbin = self.BG.CBobbin
        

        if self.OpenPrevFile and len(self.RecentFiles):
            self.OpenFile(self.RecentFiles[0])
        
        self.protect_table()


        #hardware buttons
        self.Button1 = PiButton(17)
        self.Button2 = PiButton(27)
        #OLED
        self.OLED = OLED() #optional local element display
        self.OLED.write(AppTitle  + AppVersion)



        self.btnPwrOn.focus_set()
            
    def init_window(self):
        self.master.title(AppTitle)
        #self.master.iconbitmap("windericon.ico")
        self.master.protocol('WM_DELETE_WINDOW',self.close)
        

        # set up the window size and position
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        try:
            window_width = self._Ini["window"]["width"]
            window_height =self._Ini["window"]["height"]
            
        except Exception as e:
            print(e, self._Ini)
            window_width = screen_width/1.4
            window_height = screen_height/2
        
        
        window_position_x = screen_width/2 - window_width/2
        window_position_y = screen_height/2 - window_height/2
        self.master.geometry('%dx%d+%d+%d' % (window_width, window_height, window_position_x, window_position_y))
        
  

    def init_menu(self):
        #menu

        
        self.mnuBar = Menu(self.master)
        self.master.config(menu=self.mnuBar)

        self.mnuRecent = Menu(self, tearoff = 0)
        
        self.mnuFile = Menu(self.mnuBar, tearoff=0)

        self.mnuFile.add_command(label="New" , command=self.NewFile)
        self.mnuFile.add_separator()
        self.mnuFile.add_command(label="Open" , command=self.OpenFile)


        self.mnuFile.add_cascade(label= 'Recent Files', menu = self.mnuRecent)


        self.mnuRecent.add_command(label= "1 " , command = lambda: self.OpenRecent(0) )
        self.mnuRecent.add_command(label= "2 " , command = lambda: self.OpenRecent(1) )
        self.mnuRecent.add_command(label= "3 " , command = lambda: self.OpenRecent(2) )
        self.mnuRecent.add_command(label= "4 " , command = lambda: self.OpenRecent(3) )

        self.mnuFile.add_separator()
        self.mnuFile.add_command(label="Save", command = self.SaveFile)
        self.mnuFile.add_command(label="Save As...", command = self.SaveAsFile)
        self.mnuFile.add_separator()
        self.mnuFile.add_command(label="Exit", command=self.close)
        self.mnuBar.add_cascade(label="File", menu=self.mnuFile)

        self.mnuEdit = Menu(self.mnuBar, tearoff=0)
        self.mnuEdit.add_command(label="Cut", state='disabled')
        self.mnuEdit.add_command(label="Copy", state='disabled')
        self.mnuEdit.add_command(label="Paste", state='disabled')
        self.mnuBar.add_cascade(label="Edit", menu=self.mnuEdit, state='disabled')

        self.mnuTable = Menu(self.mnuBar, tearoff=0)
        self.mnuTable.add_checkbutton(label="Protect Table",
                                      variable = self.PT,
                                      onvalue = True,
                                      offvalue=False,
                                      command = lambda: self.protect_table()
                                      )
        self.mnuTable.add_separator()
        self.mnuTable.add_command(label="Add Section", command = lambda: self.Table.InsertSection())
        self.mnuTable.add_command(label="Delete Section", command =lambda:  self.Table.DelSection(), state ='disabled')
        self.mnuBar.add_cascade(label="Table", menu=self.mnuTable, state = 'disabled')

        

        self.mnuSettings = Menu(self.mnuBar, tearoff=0)
        self.mnuSettings.add_command(label="Machine Settings", command=self.ShowSettings) #, state='disabled')
        self.mnuSettings.add_command(label="Bobbin Settings", command=self.ShowBobbins) #, state='disabled')
        self.mnuSettings.add_separator()
        self.mnuSettings.add_checkbutton(label="Debug",
                                      variable = self.Debug,
                                      onvalue = True,
                                      offvalue=False,
                                      command = lambda : self.ToggleDebug()
                                      )
        
        self.mnuBar.add_cascade(label="Settings", menu=self.mnuSettings)


    def init_widgets(self):
        #widgets
        #-------------------------define frame for buttons
        
        butfrm = Frame(self.master)

        self.btnPwrOn = Button(butfrm,text="Motors On", command=lambda : self.winder.Motor_Power(), state='normal')
        self.btnPwrOn.pack(padx =2,side = LEFT)
        #self.btnPwrOn.config( width = 32, height = 32)

        
        self.btnHome = Button(butfrm,text="Home", command = lambda : self.winder.HomeAll(), state='disabled')
        self.btnHome.pack(side = LEFT, padx =2)
        
        self.btnWind = Button(butfrm,text="Wind", command=lambda : self.WindPrep(), state='disabled')
        self.btnWind.pack(side = LEFT, padx =2)
    
        
        self.imgES=PhotoImage(file="Images/estop-ico.gif")
        self.btnPwrOff = Button(butfrm,text="E-Stop", command= lambda: self.E_Stop(), state='disabled')
        self.btnPwrOff.config(image=self.imgES)
        self.btnPwrOff.pack(side = RIGHT, padx =2)
        butfrm.pack(side= TOP, fill=BOTH, padx= 2 , pady= 5)

        

        #-------------------------define frame for job data
        
         #define frame for job descriptor
        jobfrm = Frame(self.master, relief=RIDGE, bd=1,  padx=2, pady = 2)

        self.titlab = Label(jobfrm, justify='left',  text = "Title").grid (row =0, column=0)
        
        self.titent = Entry(jobfrm,)
        self.titent.grid(row=0 , column = 1)
     
        self.Drnlab = Label(jobfrm, justify='left',  text = "    Drawing number     ").grid (row =1,column=0)
        self.Drnent = Entry(jobfrm, )
        self.Drnent.grid(row=1, column = 1)

        self.Datelab = Label(jobfrm, justify='center',text = "Date").grid (row =2,column=0)
        self.Dateent= Entry(jobfrm,)
        self.Dateent.grid(row=2, column = 1)
        self.Dateent.insert(0, date.today())

        jobfrm.pack(fill= BOTH) #, pady=5)



        #--------------------------- define frame for hardware

        hardware = LabelFrame(self.master,bd=1, relief=SUNKEN, padx=2, pady = 2, text='Hardware')
        self.BG = BobbinGUI(master = hardware,
                            App = self,
                            )
        hardware.pack(fill=BOTH)


        

        #----------------------- frame for hint panel
        self.Hint = Frame(self.master,bd=1,relief=SUNKEN, ) #packed after table
        self.lblHint = Label(self.Hint, text="Hint Panel", justify='left', bg="khaki")
        self.lblHint.pack(side="bottom", fill='x', expand='no')



        #------------------------define frame for table
        self.tabfrm = LabelFrame(self.master, text='Coil Data')
  
        #create and build table object
        self.Table = CoilTable(master =self.tabfrm,
                               Winder = self.winder,
                               menu = self.mnuBar,
                               mnuTable =self.mnuTable,
                               lblHint = self.lblHint)
        self.update_widgets()
        self.tabfrm.pack(fill= BOTH)
        
        self.Hint.pack(fill= BOTH, pady=5 , padx=5 )

        #------------frame for wind control panel
        
        self.Control = LabelFrame(self.master, text='Winding Controls')

        self.ConPanel = ControlForm(self.Control, self.winder)
        self.Control.bind("<Key>",self.KeyInterface)
        

        #----------------------- frame for Status Bar
        stsfrm = Frame(self.master,bd=1, relief=SUNKEN, padx=2, pady = 2)
        
        self.lblPTcommand = Label(stsfrm, text="PTcommand", justify='left')
        self.lblPTcommand.pack(side="bottom", fill='x', expand='no')
        self.lblPTreply = Label(stsfrm, text="PT replies" , justify='left')
        self.lblPTreply.pack(side="bottom", fill='x', expand='no')
        
        stsfrm.pack(side= BOTTOM, fill= 'x')
        

        #----------------------- frame for progress bar
        self.prbfrm = Frame(self.master,bd=1, relief=SUNKEN, padx=2,pady=2)
        self.prgbar = ttk.Progressbar(self.prbfrm, orient='horizontal', mode = 'determinate')
        self.prgbar.pack(side='bottom',fill='x')
        #self.prbfrm.pack(side = BOTTOM, fill='x')      
        
        #update widget displays
        self.update_widgets()
        #------------------------------
#====================================================keyboard interface
    def KeyInterface(self,event):
        k = event.keysym
        if self.Debug.get(): print(event,k)    

        if k=="F8": #power
            self.winder.Motor_Power()

        elif (k=="F9" or k=="Home") and str(self.btnHome["state"])=="normal" : #home
            self.winder.HomeAll()
        elif (k=="F11" or k=="Return") and str(self.btnWind["state"])=="normal":
            self.WindPrep()
        elif (k=="F12" or k=="space"):                
            self.E_Stop()

            
        if self.Control.winfo_ismapped():
            #enable keypad controls
            
            if k == "KP_Add" :
                self.ConPanel.JogSpindle(Distance=3,Direction=False)
                self.Button1.setfunction(self.ConPanel.JogSpindle,Distance=3,Direction = True)
                self.Button2.setfunction(self.ConPanel.JogSpindle,Distance=3,Direction = False)
                self.OLED.buttons("<<<",">>>")
                self.OLED.write("Jog Spindle")
                
            elif k=="KP_Subtract":
                self.ConPanel.JogSpindle(Distance=3,Direction=True)
                self.Button1.setfunction(self.ConPanel.JogSpindle,Distance=3,Direction = True)
                self.Button2.setfunction(self.ConPanel.JogSpindle,Distance=3,Direction = False)
                self.OLED.buttons("<<<",">>>")
                self.OLED.write("Jog Spindle")
                
            elif k=="KP_8" or k=="Left": #jog feeder <
                self.winder.JogFeeder(Distance = -0.1)
                self.Button1.setfunction(self.winder.JogFeeder,Distance=-0.1)
                self.Button2.setfunction(self.winder.JogFeeder,Distance=0.1)
                self.OLED.buttons("<",">")
                self.OLED.write("Jog Feeder 0.1")
                
            elif k=="KP_2"or k=="Right": #jog feeder >
                self.winder.JogFeeder(Distance = 0.1)
                self.Button1.setfunction(self.winder.JogFeeder,Distance=-0.1)
                self.Button2.setfunction(self.winder.JogFeeder,Distance=0.1)
                self.OLED.buttons("<",">")
                self.OLED.write("Jog Feeder 0.1")
            elif k=="KP_Enter": #Go
                self.ConPanel.WindPrep()
            elif k=="Pause": 
                self.ConPanel.WindPause()
                
            elif k=="KP_4" or k=="KP_Left":#|<--
                self.ConPanel.FeederPos(RHS=False)
                self.Button1.setfunction(self.ConPanel.FeederPos,RHS=False)
                self.Button2.setfunction(self.ConPanel.FeederPos,RHS=True)
                self.OLED.buttons("|<--","-->|")
                self.OLED.write("Feeder Side")

                
            elif k=="KP_6"or k=="KP_Right":#-->|
                self.ConPanel.FeederPos(RHS=True)
                self.Button1.setfunction(self.ConPanel.FeederPos,RHS=False)
                self.Button2.setfunction(self.ConPanel.FeederPos,RHS=True)
                self.OLED.buttons("|<--","-->|")
                self.OLED.write("Feeder Side")
                
            elif k=="KP_9" or k=="KP_Prior":
                pass
            elif k=="KP_3" or k=="KP_Next":
                pass
            elif k=="KP_5" or k=="KP_Begin": #feed direction
                self.ConPanel.ToggleFeedDirection()        
            elif k=="KP_Decimal" or k=="KP_Delete": #
                pass
            elif k=="KP_0" or k=="KP_Insert": #
                pass
            elif k=="KP_7" or k=="KP_Home": #
                pass
            elif k=="Down": #home
                self.ConPanel.JogSpindle(Distance=1,Direction=False)
                self.Button1.setfunction(self.ConPanel.JogSpindle,Distance=1,Direction = True)
                self.Button2.setfunction(self.ConPanel.JogSpindle,Distance=1,Direction = False)
                self.OLED.buttons("<",">")
                self.OLED.write("Jog Spindle")
                
            elif k=="Up" : #
                self.ConPanel.JogSpindle(Distance=1,Direction=True)
                self.Button1.setfunction(self.ConPanel.JogSpindle,Distance=1,Direction = True)
                self.Button2.setfunction(self.ConPanel.JogSpindle,Distance=1,Direction = False)
                self.OLED.buttons("<",">")
                self.OLED.write("Jog Spindle")
                
            elif k=="Escape": #cancel
                self.winder.Stop()
            



#====================================================button and widget actions=
    def BobbinChanged(self):
        self.BG.init_Bobbins
        self.winder.Bobbin = self.BG.CBobbin
        self.Table.Recalc()
        #print("Bobbin changed")
        
    def WindPause(self):
            self.winder.Pause()    
        
    def WindPrep(self):
        #self.btnPwrOff.focus_set()
        
        if not self.update_coillist() :
            #print(self.winder.Coil)
            #table error
            warn = messagebox.showwarning(
                title = 'Coil Layer  Error',
                message = "There is nothing to wind! Open file or enter data",
                )
        
        else:
            if self.winder.Coil.RPM * self.winder.Coil.Pitch > self.winder.Feeder.MaxSpeed:
                newrpm = int(self.winder.Feeder.MaxSpeed/self.winder.Coil.Pitch)
                self.winder.Coil.RPM = newrpm
                warn = messagebox.showwarning( title = 'Coil Layer  Error',
                                               message = """Feeder's maximum speed exceeded: RPM reduced to {}""".format(newrpm),
                                               )

            #show the threading and positioning window
            self.btnWind.config(state = 'disabled')
            self.Hint.pack_forget()
            self.winder.Counter.Reset()

            self.Button1.setfunction(self.ConPanel.JogSpindle,Distance=3,Direction = True)
            self.Button2.setfunction(self.ConPanel.JogSpindle,Distance=3,Direction = False)
            self.OLED.buttons("<<<",">>>")
            self.OLED.write("Jog Spindle")
            
            #self.winder.Bobbin = self.Bobbin
            self.Control.pack(fill=BOTH)
            
            self.ConPanel.focus_set()
            self.ConPanel.Update()
            self.Control.focus_set()
            
    def update_coillist(self):
        self.winder.Coil = self.Table.GetCoilObject()
        self.winder.Coil.Width = self.winder.Bobbin.InternalWidth - (2*self.winder.Coil.Pitch)
        #self.winder.Coil.append(self.winder.Bobbin.InternalWidth - (2*self.winder.Coil[1]))
        #print(self.winder.Coil)
        return self.winder.Coil
        
    def update_widgets(self):
        self.titent.delete(0,'end')
        self.titent.insert(0, self._MS['Descriptor']['Title'])
        self.Drnent.delete(0,'end')
        self.Drnent.insert(0, self._MS['Descriptor']['DrawNo'])
        self.Dateent.delete(0,'end')
        self.Dateent.insert(0, self._MS['Descriptor']['Date'])
 
        self.BG.SelectBobbin(Sel=int(self._MS['Hardware']['BobbinType']))
        self.winder.Bobbin = self.BG.CBobbin

        #build table from _MS['Winding']
        #self.Table.clear_table()
        self.Table.build_table(self._MS)

    def update_MS(self):
        #copy table entries to dictionary

        self._MS['Windings'] = self.Table.GetCoilList()
        self._MS['Descriptor']['Title'] = self.titent.get()
        self._MS['Descriptor']['DrawNo'] = self.Drnent.get()
        self._MS['Descriptor']['Date'] = self.Dateent.get()
        self._MS['Hardware']['BobbinType'] = self.BG.CBobbin.Type

        #self.update_coillist()
        


    def Hard_EStop (self,ch):
        self.winder.Motor_Power(False)    
        warn = messagebox.showwarning(
                title = 'E-STOP pressed',
                message = "Release button then, Cut wire and home before restarting")        
    
         
    def E_Stop(self): #soft e-stop
        self.winder.Motor_Power(False)    
        warn = messagebox.showwarning(
                title = 'E-STOP pressed',
                message = "Home before restarting")        
    
    def updateprogress(self, progress, total):
        self.prgbar['maximum']= total
        self.prgbar['value']=progress
        self.OLED.progressbar((progress/total)*100)
            
    def updateturnscounter(self, count):
        #update turns counters
        self.ConPanel.UpdateCounter(count)

    def updatefeederposition(self, pos):
        self.ConPanel.updatefeederpos(pos)

#======================== GUI status update from winder


    def SetState(self, Status = None):
        #set buttons etc, to appropriate state i.e Homing, AtHome, Wind
        self.lblPTcommand.config(text=Status)
        self.ConPanel.SetState(Status)
        
        if Status == "Winding - Initialise":
            
            self.btnWind.config(state = 'disabled')
            self.btnWind.config(text = "Wind")
            self.btnHome.config(state = 'disabled')

            self.btnPwrOn.config(state = 'disabled')
            self.btnPwrOff.config(state = 'normal')

            self.prbfrm.pack(side= BOTTOM, fill= 'x')
            
            self.Button1.setfunction(self.winder.Stop)
            self.Button2.setfunction(self.WindPause , once=True)
            
            self.OLED.buttons("STOP","PAUSE")
            self.OLED.progressbar(0)
    
        elif "Paused" in Status:
            self.Button1.setfunction(self.winder.Stop)
            self.Button2.setfunction(self.WindPause , once = True)
            self.OLED.buttons("STOP","PAUSED")
            

        elif Status =="Layer Complete":
            if self.Table.CurrentHLR == None:
                #winding complete
                self.Control.pack_forget()
                self.Hint.pack(fill= BOTH, pady=5 , padx=5 )
                self.btnWind.config(state = 'disabled')
                self.btnHome.config(state = 'normal')

                self.btnPwrOn.config(state = 'disabled')
                self.btnPwrOff.config(state = 'normal')
                self.prbfrm.pack_forget()
                self.Table.HighLightOff()

                self.OLED.progressbar(0)
                self.Button1.setfunction(self.winder.Stop)
                self.Button2.setfunction(None)
                self.OLED.write("Finished Winding")
                self.OLED.buttons("STOP","")
                
            else:
                self.btnWind.config(state = 'normal')
                self.btnWind.config(text = "Next")
                self.btnHome.config(state = 'disabled')
                self.Control.pack_forget()
                self.Hint.pack(fill= BOTH, pady=5 , padx=5 )
                self.btnPwrOn.config(state = 'disabled')
                self.btnPwrOff.config(state = 'normal')
                self.prbfrm.pack_forget()
                self.Table.HighLightNext()

                self.OLED.progressbar(100)
                self.Button1.setfunction(self.winder.Stop)
                self.Button2.setfunction(self.WindPrep, True)
                
                self.OLED.buttons("STOP","NEXT")
            

            
        elif Status == "Homing All":
            
            self.btnWind.config(state = 'disabled')
            self.btnHome.config(state = 'disabled')

            self.btnPwrOn.config(state = 'disabled')
            self.btnPwrOff.config(state = 'normal')
            self.prbfrm.pack_forget()
            self.OLED.write("Homing Feeder")

        elif  "At Home Ready" in Status:
            
            self.btnWind.config(state = 'normal')
            self.btnWind.config(text = "Wind")
            self.btnHome.config(state = 'disabled')
            
            self.btnPwrOn.config(state = 'disabled')
            self.btnPwrOff.config(state = 'normal')
            self.Table.HighLightOff()
            self.Button1.setfunction(self.winder.Stop)
            self.Button2.setfunction(self.WindPrep, True)
            
            self.OLED.clear()
            self.OLED.write("Home ready")          
            self.OLED.buttons("STOP","WIND")

        elif Status == "Stopped":#power on
            self.Control.pack_forget()
            self.Hint.pack(fill= BOTH, pady=5 , padx=5 )
            self.btnWind.config(state = 'normal')
            self.btnWind.config(text = "Wind")
            self.btnHome.config(state = 'normal')
            self.btnPwrOn.config(state = 'disabled')
            self.btnPwrOff.config(state = 'normal')
            self.prbfrm.pack_forget()
            self.Table.HighLightOff()
            self.OLED.buttons("","")
            self.OLED.write("Stopped")


        elif Status == "Motors Off":
            
            self.btnWind.config(state = 'disabled')
            self.btnHome.config(state = 'disabled')
            
            self.btnPwrOn.config(state = 'normal')
            self.btnPwrOff.config(state = 'disabled')
            self.prbfrm.pack_forget()
            self.Table.HighLightOff()


        
# File I/O ============================================
    def NewFile(self):
        self.SetDefaults()
        self.filename =""
        title = "Winder - {}".format(self.filename)
        self.master.title(title)
        self.update_widgets()
        self.PT.set(False)
        self.protect_table()
        self.titent.focus_set()

    def OpenFile(self, filename =""):
        if filename =="":    
            self.filename = filedialog.askopenfilename(initialdir=self.defaultpath, title="Select file",
                                                  filetypes=(("Settings files", "*.job"), ("all files", "*.*")))
        else:
            self.filename = filename
            
            
        #get settings from file
        try:
            with open(self.filename) as json_file:  
                self._MS = json.load(json_file)
        
                self.update_widgets()
                title = "Winder - {}".format(self.filename)
                self.master.title(title)  
                self.AddToRecent(self.filename)
                self.defaultpath = os.path.dirname(self.filename)
                
        except IOError as e:
            messagebox.showwarning("Open File", "File error: " + str(e) , icon="warning")
            
        
        
    def SaveFile(self):
        if self.filename =="":
            self.SaveAsFile()
        else:
            self.save_settings()            

    def SaveAsFile(self, filename = ""):

        filename = filedialog.asksaveasfilename(initialdir=os.sys.path[0], title="Select file",
                                                filetypes=(("Settings files", "*.job"), ("all files", "*.*")))
        
        file_name, file_ext = os.path.splitext(filename) 
        
        if file_ext =='' :
            filename +=".job"
            
        self.save_settings(filename)
        self.AddToRecent(filename)

    def save_settings(self, filename =None):

        self.update_MS()

        if filename == None:
            filename = self.filename
        elif not filename == "":
            self.filename = filename


        with open(filename , 'w') as outfile:  
             json.dump(self._MS, outfile)
        title = "Job Settings - {}".format(filename)
        self.master.title(title)



    def OpenRecent(self, Index):
        if Index < len(self.RecentFiles):
            self.OpenFile(self.RecentFiles[Index])

    def AddToRecent(self, filename):
        New = True
        for FN in self.RecentFiles:
            if FN == filename:
                New = False
                
        if New:
            self.RecentFiles.insert(0,filename)
            if len(self.RecentFiles) >4:
                self.RecentFiles.pop()
            #print(filename, New)
                
            
        self.update_recentfilemenu()
        
    def update_recentfilemenu(self):
        try:

            self.mnuRecent.entryconfig(0, label= "1 " + self.RecentFiles[0])
            self.mnuRecent.entryconfig(1, label= "2 " + self.RecentFiles[1])
            self.mnuRecent.entryconfig(2, label= "3 " + self.RecentFiles[2])
            self.mnuRecent.entryconfig(3, label= "4 " + self.RecentFiles[3])
        except Exception as e:
            #print('update_recentfilemenu', str(e))
            pass
        
        
        
    def rec_dicts(self, ED, DD):
        for key in DD:
            if  key in ED:
                if type(DD[key]) is dict:
                    self.rec_dicts(ED[key],DD[key])
            else:
                ED[key]=DD[key]

    def LoadIniFile(self):
        #load recent file list from json
        try:
            with open('Winder.ini') as json_file:  
                self._Ini= json.load(json_file)
                self.RecentFiles = self._Ini['recentfiles']
                self.OpenPrevFile = self._Ini['openpreviousfile']


        except:
            #use defaults                    
            self._Ini['recentfiles'] = self.RecentFiles
            self._Ini['openpreviousfile'] = self.OpenPrevFile
            self._Ini['window'] ={}
            self._Ini['window']['width'] = self.master.winfo_screenwidth()
            self._Ini['window']['height'] = self.master.winfo_screenheight()



    def SetDefaults(self):
        today = date.today()
        currentdate = "%s/%s/%s" %(today.day,today.month,today.year)
        self._MS['Descriptor'] = {'Title': '', 'DrawNo': '', 'Date': currentdate }
        self._MS['Hardware'] = {'BobbinType': 0, 'BobbinWidth': 0.00, 'BobbinHeight': 0.00, }
        self._MS['Windings'] = []
        #print(self._MS)

    def Revert(self):
        #reload entry boxes
        self.update_widgets()
 #============================================================menu functions
    def ToggleDebug(self):
            self.winder.PT.DEBUG = self.Debug.get()
            print("Debug = {}".format(self.winder.PT.DEBUG))
    
    def ShowSettings(self):
        #show setting windows
        MS = MachineSet(Toplevel(self.master), True)
        self.master.wait_window(MS.master)
        self.winder.Init_Settings()
        self.master.focus_set()

    def ShowBobbins(self):
        BS = BobbinSet(Toplevel(self.master), True)
        self.master.wait_window(BS.master)
        #refresh bobbins
        self.BG.refresh_Blist()
        self.winder.Init_Settings()        
        self.master.focus_set()
        #print("bobbin settings closed - main focused")
        
    def unprotect_table(self):
        self.Table.lock_table(False)
        self.mnuTable.entryconfig("Add Section", state = 'normal')
        self.mnuTable.entryconfig("Delete Section", state = 'normal')

    def protect_table(self):
        l = self.PT.get()
        #print (l)
        if l == True:
            self.Table.lock_table(True)
            self.mnuTable.entryconfig("Add Section", state = 'disabled')

            self.mnuTable.entryconfig("Delete Section", state = 'disabled')
        else:
            self.unprotect_table()

    def test(self):
        #for testing stuff
        
        #pass
        self.Hard_EStop(0)

    def close(self):
        #app is closing
        if messagebox.askyesno("Exit Application", "Do you really want to end this application?", icon="warning"):


            #save ini as file
            #print("saving ini file")
            self._Ini['recentfiles'] = self.RecentFiles
            self._Ini['openpreviousfile'] = self.OpenPrevFile
            self._Ini['window']['width']  = self.master.winfo_width()
            self._Ini['window']['height'] = self.master.winfo_height()


            try:
                with open('Winder.ini' , 'w') as outfile:  
                    json.dump(self._Ini, outfile)
            except Exception as e:
                print("ini save failed", e)
                pass
            #self.winder.destroy()
            self.master.destroy()
        
#-------------------------------------------------------    

 

if __name__ == '__main__':
 
    root=Tk()

    app = window(root)


    root.mainloop()   

