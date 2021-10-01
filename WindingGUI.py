###########################################
# ADT WindingGUI object
#
# W.K.Todd 02/06/21
#
# winding action GUI object.
# displays controls for threading and alignment
AppTitle = "WindingGUI"
AppVersion  = "V1.01"
#
###########################################
from tkinter import Button,Checkbutton, Entry, Frame, Label,LabelFrame, Scale,  Tk
from tkinter import  BooleanVar
from tkinter.constants import LEFT,RIGHT, BOTTOM,  BOTH, SUNKEN, N ,NS,EW, HORIZONTAL


class ControlForm(Frame):

    FeederPos = True
    
    def __init__(self, master = None, Winder = None):
        Frame.__init__(self,master)
        self.master=master
        if Winder:
            self.winder = Winder
           
        self.init_widgets()
        
    def init_widgets(self):
        #widgets
        self.ContEn = BooleanVar() #integer variable for checkbox
        #self.Turns = IntVar() # integer for spinbox

        #-----------------------------feeder frame
        FCfrm = Frame(self.master) #common frame for feed and coil
        
        feedfrm= LabelFrame(FCfrm,bd=1, relief=SUNKEN, padx=2, pady = 2, text='Feeder Positioning')

        self.chkCont = Checkbutton(feedfrm,
                                   text = "Continue from current location",
                                   variable = self.ContEn,
                                   onvalue = 1,
                                   offvalue = 0,
                                   command=lambda : self.Continue(),
                                   )
        
        self.chkCont.grid(column=0,row=0) #pack(side =TOP)
        
        self.lblFeederPos = Label(feedfrm, text = "Feeder Position : ---")
        self.lblFeederPos.grid(column=0,row=1) #pack(side =TOP)
        

        feedfrm1 = Frame(feedfrm)
        self.btnfeedfullL = Button(feedfrm1,
                                   text="|<--|",
                                   command=lambda : self.FeederPos(RHS=False),
                                   state='normal')
        self.btnfeedfullL.pack(side = LEFT, padx =2)
        
        self.btnfeedfastL = Button(feedfrm1,
                                   text="<<",
                                   command=lambda : self.winder.JogFeeder(Distance =-0.5),
                                   state='normal')
        self.btnfeedfastL.pack(side = LEFT, padx =2)
        
        self.btnfeedjogL = Button(feedfrm1,
                                  text="<",
                                  command=lambda : self.winder.JogFeeder(Distance = -0.5 * self.WireWidth),
                                  state='normal',
                                  )
        self.btnfeedjogL.pack(side = LEFT, padx =2)
        
        self.btnfeedjogR = Button(feedfrm1,text=">",
                                  command=lambda : self.winder.JogFeeder(Distance = 0.5 * self.WireWidth),
                                  state='normal',
                                  )
        self.btnfeedjogR.pack(side = LEFT, padx =2)
        self.btnfeedfastR = Button(feedfrm1,
                                   text=">>",
                                   command=lambda : self.winder.JogFeeder(Distance = 0.5),
                                   state='normal')
        self.btnfeedfastR.pack(side = LEFT, padx =2)
        
        self.btnfeedfullR = Button(feedfrm1,
                                   text="|-->|",
                                   command=lambda : self.FeederPos(RHS=True),
                                   state='normal')
        self.btnfeedfullR.pack(side = LEFT, padx =2)  
        

        feedfrm1.grid(column=0,row=2, pady=2, padx=10, sticky=N) #pack(side=BOTTOM,fill=BOTH)
        #----------------feed direction frame and buttons
        feedfrm2 = Frame(feedfrm)
        self.lblFeedDir = Label(feedfrm2, text = "Feeder Direction:" )
        self.lblFeedDir.pack(side = LEFT, padx =2) 
        self.btnFeedDir = Button(feedfrm2,
                                 text="<---",
                                 command=  self.ToggleFeedDirection,
                                 state='normal'
                                 )
        self.btnFeedDir.pack(side = LEFT, padx =2)  
        
        feedfrm2.grid(column=0, row=3, pady=10, padx=10, sticky=N)
        
        feedfrm.grid(column=0, row=0, pady=0, padx=0, sticky=NS) #pack( fill= X, pady=5)

        #----------------------------Coil frame

        coilfrm= LabelFrame(FCfrm,bd=1, relief=SUNKEN, padx=2, pady = 2,  text='Coil Position and Width')

        coilfrm1 = Frame(coilfrm)
        
        self.lblCoilOffset = Label(coilfrm1, text = "Offset: ---")
        self.lblCoilOffset.grid(column = 0 ,columnspan=2, row = 0, pady=2, padx=2)
        #lbl =  Label(coilfrm1, text = " | ")
        #lbl.grid(column=2, row=0)
        
        
        self.btnNudgeL = Button(coilfrm1,
                                text="<|--|<",
                                command=lambda : self.FeedNudge(1),
                                state='disabled')

        self.btnNudgeL.grid(column=0, row=1,pady=2, padx=5)
        
        self.btnNudgeR = Button(coilfrm1,
                                text=">|--|>",
                                command=lambda : self.FeedNudge(-1),
                                state='disabled')
        self.btnNudgeR.grid(column=1, row=1,pady=2, padx=2)
        
        #lbl =  Label(coilfrm1, text = " | ")
        #lbl.grid(column=2, row=1)

        self.lblCoilWidth = Label(coilfrm1, text = "Width: ---")
        self.lblCoilWidth.grid(column=0, columnspan=2, row=2,pady=2, padx=2)
        
        self.btnwider = Button(coilfrm1,
                               text="<|---|>",
                               command=lambda : self.FeedWidth(1),
                               state='disabled')
        self.btnwider.grid(column=0, row=3,pady=2, padx=5)
        
        self.btnnarrow = Button(coilfrm1,
                                text=">|--|<",
                                command=lambda : self.FeedWidth(-1),
                                state='disabled')
        self.btnnarrow.grid(column=1, row=3, pady=2, padx=2)

        coilfrm1.pack(fill=BOTH, pady=4, padx=5,)

        coilfrm.grid(column = 1, row=0, pady=1, padx=5, sticky = N) #pack(side =TOP, fill= X, pady=5)

        FCfrm.grid(column=0, row=0 , rowspan=2, pady=0, padx=10, sticky=NS)

        #----------------------------spindle frame

        spnfrm = LabelFrame(self.master,bd=1, relief=SUNKEN, padx=2, pady = 2, text='Spindle Threading')
        
        turnsfrm = Frame(spnfrm)
        self.lblTurns = Label(turnsfrm, text = "Turns")
        self.lblTurns.pack( side = LEFT, padx = 5, pady= 5)
        self.Turns = Entry(turnsfrm, width = 6, ) 
        self.Turns.pack( side = RIGHT, padx = 5, pady= 5)
        self.Turns.bind("<FocusOut>", self.UpdateTurns())
        turnsfrm.pack()

        speedfrm = Frame(spnfrm)
        self.lblRate = Label(speedfrm, text="Speed Adjust (%): 0 ")
        self.lblRate.pack( side = BOTTOM, padx = 5, pady= 5)
        self.sldRate = Scale(speedfrm, from_=-50 , to =50 , length = 200, orient=HORIZONTAL, state='normal' )
        self.sldRate.pack( side = BOTTOM, padx = 2, pady= 5)
        self.sldRate.bind("<ButtonRelease-1>", self.ChangeSpeed)
        speedfrm.pack()
        

        
        #--------------------------------frame for jog/nudge
        bspnfrm = Frame(spnfrm)
        self.lblJog =  Label(bspnfrm, text = "Jog")
        self.lblJog.pack( side = LEFT, padx = 5, pady= 5)
        
        self.btnFastSpindleF = Button(bspnfrm,
                                      text="<<<",
                                      command=lambda : self.JogSpindle(Distance=3,Direction = True),
                                      state='normal')
        self.btnFastSpindleF.pack(side = LEFT, padx =2)
        
        self.btnJogSpindleF = Button(bspnfrm,
                                     text="<",
                                     command=lambda : self.JogSpindle(Direction = True),
                                     state='normal')
        self.btnJogSpindleF.pack(side = LEFT, padx =2)
        
        self.btnJogSpindleB = Button(bspnfrm,
                                     text=">",
                                     command=lambda : self.JogSpindle(Direction=False),
                                     state='normal')
        self.btnJogSpindleB.pack(side = LEFT, padx =2)

        self.btnFastSpindleB = Button(bspnfrm,
                                      text=">>>",
                                      command=lambda : self.JogSpindle(Distance=3,Direction=False),
                                      state='normal')
        self.btnFastSpindleB.pack(side = LEFT, padx =2)
        bspnfrm.pack()

        spnfrm.grid(column=1, row=0,  pady=0, padx=0, sticky=NS) #pack(side = TOP, fill= X, pady=5)
        
        #-------------------------define frame for buttons
        
        butfrm = LabelFrame(self.master,bd=1, relief=SUNKEN, padx=2, pady = 2, text='Winder')

        self.btnStop = Button(butfrm,text="Cancel", command=lambda : self.winder.Stop(), state='disabled')
        self.btnStop.pack(side = LEFT, padx =5)

        self.btnWind = Button(butfrm,text="Go", command=lambda : self.WindPrep(), state='normal')
        self.btnWind.pack(side = RIGHT, padx =2)
    

        self.btnPause = Button(butfrm,text="Pause", command=lambda : self.WindPause(), state='disabled')
        self.btnPause.pack(side = RIGHT, padx =2)

        
        butfrm.grid(column=0, columnspan= 2, row=2, pady=2, padx=10, sticky=EW) #pack(side=BOTTOM, fill=X, padx= 2 , pady= 5)
        
#=================================== routines
    def ChangeSpeed(self,event):
        Adj = (100 + self.sldRate.get())/100
        
        if  int(self.RPM * Adj) * self.winder.Coil.Pitch > self.winder.Feeder.MaxSpeed:
            self.sldRate.config(fg="RED")
        else:
            self.sldRate.config(fg="BLACK")
            self.RPM  = int(self.InitRPM * Adj)
            self.lblRate.config(text = "Speed Adjust (%): {} RPM ".format(self.winder.Coil.RPM))
            self.winder.AdjustSpeed(Adj)
        
    def UpdateTurns(self):
        #print("spin: ",self.Turns.get())
        if self.winder.Coil:
            self.winder.Coil.Turns = float(self.Turns.get())

    def UpdateCounter(self, count):
        if self.winder.Coil:
            self.Turns.delete(0,"end")        
            self.Turns.insert(0, float(self.winder.Coil.Turns) - count)
      
        
    def Update(self):
        '''update widgets etc.'''
        if self.winder.Coil: #update coil info
            self.ContEn.set("C" in self.winder.Coil.StartPos)
            self.WireWidth = self.winder.Coil.Pitch
            self.InitRPM = int(self.winder.Coil.RPM) #rpm
            self.RPM =self.InitRPM
            self.CoilWidth = self.winder.Bobbin.InternalWidth
            self.lblCoilWidth.config(text = "Width: {:.2f}".format(self.winder.Coil.Width))
            self.lblCoilOffset.config(text = "Offset: {:.2f}".format(self.winder.Coil.Offset))
            self.Continue()
            #position feeder
            if not self.ContEn.get(): 
                self.FeederPos(self.winder.Coil.Feedtoleft)

        self.UpdateCounter(0)
        self.updatefeederpos(self.winder.Feeder.GetCurrentPosition())
        self.sldRate.set(0)
        self.lblRate.config(text = "Speed Adjust (%): {} RPM".format(self.InitRPM))
        
            
    def Continue(self):
        #set continuation mode 
        if self.ContEn.get():
            #self.chkCont.select()
            self.FeederButtonEnable("disabled")
        else:    
            #self.chkCont.deselect()
            self.FeederButtonEnable("normal")


        
    def SetState(self, Status = "Stopped"):
        '''set buttons etc, to appropriate state i.e Homing, AtHome, Wind'''
        #self.Update()
        windstate = 'normal'
        nudstate = 'disabled'
        
        if "Wind" in Status :
            self.btnPause.config(text = "Pause ",state = 'normal')
            self.lblFeederPos.config(text = "Feeder Position : <--->")
            windstate = 'disabled'
            nudstate = 'normal'
            
        elif Status == "Stopped":#power on  
            self.btnPause.config(text = " Pause ",state = 'disabled')
            windstate = 'normal'
            nudstate = 'disabled'
            
        elif "Pause" in Status :#pause
            self.btnPause.config(text = "Paused ",state = 'normal')
            windstate = 'disabled'
            nudstate = 'disabled'
            
        elif "Brak" in Status :
            self.btnPause.config(text = "Pausing",state = 'disabled')
            windstate = 'disabled'
            nudstate = 'disabled'
            
        elif "Feed" in Status:
            self.updatefeederpos(self.winder.Feeder.GetCurrentPosition())
        

        #self.spnTurns.config(state = windstate)    
        self.btnStop.config(state = windstate)
        self.btnWind.config(state = windstate)
        self.FeederButtonEnable(windstate)
        self.btnFastSpindleF.config(state = windstate)
        self.btnJogSpindleF.config(state = windstate)
        self.btnJogSpindleB.config(state = windstate)
        self.btnFastSpindleB.config(state = windstate)
        self.btnNudgeL.config(state = nudstate)
        self.btnNudgeR.config(state = nudstate)
        self.btnwider.config(state = nudstate)
        self.btnnarrow.config(state = nudstate)

    def FeederButtonEnable(self, st ="normal"):
        self.btnfeedfullL.config(state = st)   
        self.btnfeedfullR.config(state = st)
        self.btnfeedjogL.config(state = st)
        self.btnfeedjogR.config(state = st)
        self.btnfeedfastL.config(state = st)
        self.btnfeedfastR.config(state = st)
        
    def WindPrep(self):
        #update coil turns speed etc.
        #self.Turns = self.spnTurns.get()
        self.winder.Coil.Turns= float(self.Turns.get())
        self.winder.Coil.RPM = self.RPM
        self.winder.Wind()
        
    def WindPause(self):
        self.winder.Pause()

    def FeedNudge(self, Dir):
        #update lables
        self.winder.CoilOffset -= self.WireWidth * Dir
        t = "Offset: {:.2f}".format(self.CoilOffset)
        self.lblCoilPos.config(text = t )
        self.winder.NudgeFeeder(self.WireWidth * Dir)
        
    def FeedWidth(self, Dir):
        #update lables
        if self.CoilWidth >= self.WireWidth:
            self.CoilWidth += self.WireWidth * Dir
        
        t="Width: {:.2f}".format(self.CoilWidth)
        self.lblCoilWidth.config(text = t)
        self.winder.FeederWidth(self.CoilWidth)

    def FeederPos(self, RHS):
        #if hand enabled home first
            if RHS:
                #coil.width + offset
                bob = self.winder.Coil.Width + self.winder.Coil.Offset
                self.winder.Coil.Feedtoleft = True
            else:
                #coil.offset
                bob = 0 + self.winder.Coil.Offset
                self.winder.Coil.Feedtoleft = False
                
            pos = self.winder.Bobbin.AdapterOffset + bob
            self.winder.FeederPos(pos)
            self.updatefeederpos(pos)
            
    def ToggleFeedDirection(self):  
        #set feeder direction
        self.winder.Coil.Feedtoleft = not self.winder.Coil.Feedtoleft
        self.updatefeeddirection(self.winder.Coil.Feedtoleft)
        
    def updatefeeddirection(self, feedtoleft):
        if feedtoleft:
            d = "<---"
        else:
            d = "--->"
        self.btnFeedDir.config(text = d)

    def updatefeederpos(self, pos):
        #if self.winder.Coil:
        self.lblFeederPos.config(text = "Feeder Position :{:.2f} ".format(pos + self.winder.AdapterOffset))
        #self.updatefeeddirection(self.winder.Coil.Feedtoleft)

    def JogSpindle(self, Distance=1, Direction = True):
        Pitch = self.winder.Coil.Pitch
        FeedDirection = (self.winder.Coil.Feedtoleft == Direction)
        Speed = 100
        self.winder.JogSpindle(Distance, Speed, Direction, Pitch, FeedDirection)

        
    def close(self):
        #app is closing
        
        self.master.destroy()

        

#-------------------------------------------------------    

if __name__ == '__main__':
 
    root=Tk()

    app = ControlForm(root)


    root.mainloop()   
