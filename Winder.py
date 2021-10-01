###########################################
# adt winder object
#
# W.K.Todd 02/06/21
#
# winding machine object encapsulates
# Homing , Start , validation etc.
#
############################################
from  PTPIC import PTPIC #,  Counter #Axis
from BobbinSettings import Tk ,Bobbin , BobbinGUI
#import time
import queue
#from WinderGUI import window
import WinderGUI
import json
#from gpiozero import LED, Button
#import RPi.GPIO as GPIO
Looptime = 150



#--------------------------
class Winder(object):
    Default_set = {"window": {"width": 901, "height": 660}, 
                   "recentfiles": ["", 
                                   "", 
                                   "", 
                                   "",
                                   ], 
                   "openpreviousfile": True}
    _CS="" #CurrentState string
    _pause = False

    MQ = queue.Queue() #move queue for async operation
    CQ = None #current queued instruction

    _MS = {}

    Coil = None # Coil section list [Turns, Pitch, layers, Cont, RPM, CoilWidth, Offset]

    Bobbin = None
    
    InnerLimit = 13.0
    OuterLimit = InnerLimit + 36 #=49
    #FZOffset = 15.0 #distance from side of frame to centre of feeder @ zero
    #FeederPosition =0
    def __init__(self):

        self.PT = PTPIC()

        self.PT.DEBUG = True
        
        self.Spindle = self.PT.GetXaxis() #assign the X channel to spindle
        self.Feeder = self.PT.GetYaxis(self.FeederCB)
        self.Counter = self.PT.GetCounter0(self.CounterCB)

        self.Init_Settings()
        
        
    def __del__(self):
        pass

    def Init_Settings(self, Settings = None):
 
        if Settings == None:
            with open('MachineSet.txt') as json_file:  
                self._MS = json.load(json_file)
        else:
            self._MS = Settings
                   
            
        self.Spindle.Name = "Spindle"
        self.Spindle.Unit="Revs"
        self.Spindle.StepsPerUnit = self._MS['Spindle']['stepsperunit']
        self.Spindle.AccelerationTime = self._MS['Spindle']['accelerationtime'] 
        self.Spindle.MaxSpeed = self._MS['Spindle']['maxspeed']
        
        self.Feeder.Name = "Feeder"
        self.Feeder.Unit = "mm"
        self.Feeder.StepsPerUnit = self._MS['Feeder']['stepsperunit'] 
        self.Feeder.AccelerationTime = self._MS['Feeder']['accelerationtime']
        self.Feeder.MaxSpeed = self._MS['Feeder']["maxspeed"]
        #self.Feeder.EnablePolarity(True)
        self.Feeder.SetOptions(LimitPolarity = True,
                               MotorEnable = False,
                               )


        self.Counter.Name = "Turns Count"
        self.Counter.Unit = "Turns"
        self.Counter.SetOptions(MPT = True)
        
        if not 'AdapterOffsets' in self._MS.keys():
            self._MS["AdapterOffsets"] ={
            'LongAdapterOffset':54.0,
            'ShortAdapterOffset':15.0,
            'Use':"SAO",
            }
        
        if self._MS["AdapterOffsets"]["Use"] == "SAO":
            AO = self._MS["AdapterOffsets"]["ShortAdapterOffset"]
        elif self._MS["AdapterOffsets"]["Use"] == "LAO":
            AO = self._MS["AdapterOffsets"]["LongAdapterOffset"]
        else:
            AO = 15 #default
        self.AdapterOffset = AO    
        self.InnerLimit  = AO - self._MS["Feeder"]["zerooffset"]
        self.OuterLimit = self.InnerLimit + 36

        
    def Wind(self):
        self._CS = "Winding - Initialise"
        app.SetState(self._CS)
        self.CQ = self.WindDone
        self._pause = False
        SpindleRPM = self.Coil.RPM
        WireDiameter = self.Coil.Pitch
        Turns = self.Coil.Turns
        coilwidth = self.Coil.Width

        #set autoreverse for distance to first reverse
        self.Feeder.SetOptions( ContSteps = False,
                                ContCycle = False,
                                CycleEnable = True,
                                )

        FeedDirection = not self.Coil.Feedtoleft
        FeederDistance = WireDiameter * Turns
        FeederSpeed = WireDiameter * SpindleRPM
        
        self.Feeder.AccelerationTime = self._MS['Feeder']['accelerationtime']  
        self.Feeder.SetMove(FeederDistance, FeederSpeed, FeedDirection)
        self.Feeder.CycleCount = 0


        CP = self.Feeder.GetCurrentPosition()
        RP = self.Bobbin.AdapterOffset + self.Coil.Offset 
        RP += (self.Coil.Width * int( FeedDirection))
        self.Feeder.SetAutoReverse(abs(CP - RP))

        #set autoreverse full 
        self.Feeder.SetOptions( ContCycle = True,
                                LimitEnable = True
                                )

        self.Feeder.SetAutoReverse(coilwidth)

        self.Spindle.AccelerationTime = self._MS['Spindle']['accelerationtime']
        self.Spindle.SetOptions(Contsteps = False, Contcycle = False)
        self.Spindle.SetMove(Turns, SpindleRPM, False) #anticlockwise
        self.Counter.Reset()        
        self.PT.StartAll()
        return True


    def WindDone(self):
        self._CS = "Winding - {} of {} Turns ".format(self.Counter.Count(), self.Coil.Turns)
        app.SetState(self._CS)
        if  self.Spindle.IsRunning  or self.Feeder.IsRunning:
            app.updateprogress(self.Counter.Count() , self.Coil.Turns)
            return False
        else:
            self._CS = "Layer Complete"
            app.SetState(self._CS)
            return True
             
    def HomeAll(self):
        #homes all axes to limits + offset
        app.SetState("Homing All")
        self.CQ = self.HomeFeeder
        self.MQ.put(self.ZeroFeeder)
        self.MQ.put(self.HomeDone)
        return True


    def HomeDone(self):
        if self.Feeder.IsRunning:
            return False
        else:
            
            cpos =self.Feeder.GetCurrentPosition()
            fao = self.AdapterOffset
            self._CS =f"At Home Ready [Nozzle @ {cpos+fao}mm]"
            
            app.SetState(self._CS)
            #self.FeederPosition = self.FZOffset
            return True
        


    def CheckLimitFeeder(self):
        #check if feeder is at limit
        self.Feeder.Stop(False,True) # check limit
        

            
    def HomeFeeder(self):
        self._CS = 'Homing Feeder to stop'
        app.SetState(self._CS)
        # limits on
        self.Feeder.AccelerationTime =1
        self.Feeder.LimitEnable()
        self.Feeder.SetAutoReverse(0)
        self.Feeder.SetOptions(ContCycle = False,
                               CycleEnable = False,
                               MotorEnable = True,
                               )
        
        # fast reverse to limit
        D = self._MS['Feeder']['homedistance']
        S = self._MS['Feeder']['homespeed']
        self.Feeder.SetMove(D, S)
        self.Feeder.Start()
        return True

    def ZeroFeeder(self):
        if self.Feeder.AtLimit:
            self.Feeder.SetABSPosition(self.InnerLimit)
            # limits off
            self.Feeder.LimitEnable(False)
            # slow fwd to offset
            D = self._MS['Feeder']['zerooffset']
            S = self._MS['Feeder']['zerospeed']
            self.Feeder.SetMove(D, S)
            self.Feeder.Start()
            self._CS ='Zeroing Feeder'
            app.SetState(self._CS)
            return False
        else:
            return not self.Feeder.IsRunning

    def JogSpindle(self, Distance =1, Speed = 100 ,Direction=True, Pitch = 0, FeedDirection = True):
        
        if Direction:
            D = "Back"
        else:
            D = "Forward"
        self._CS ='Jogging Spindle ' + D
        app.SetState(self._CS)
        
        if Direction != self.Spindle.Clockwise:
            self.PT.StopAll()

        if not Pitch == 0:
            self.Feeder.SetOptions()
            self.Feeder.AccelerationTime =0.5
            FS = Pitch * Speed
            FD = Pitch * Distance
            self.Feeder.SetMove(FD,FS,FeedDirection)
            self.Feeder.Start()
            
        self.Spindle.SetOptions(MotorEnable=False)
        self.Spindle.AccelerationTime =0.5
        self.Spindle.SetMove(Distance, Speed, Direction)       
        self.Spindle.Start()
          

    def JogFeeder(self, Distance = 1, Speed= 500 ,Clockwise = True):
        Direction = Clockwise == (Distance >0)
        
        if self.Feeder.AtLimit:
            if Direction:
                #outer limit hit
                self.FeederPosition = self.OuterLimit
            else:
                self.FeederPosition = self.InnerLimit
                
            if Direction == self.Feeder.Clockwise:
                #at limit can't move in this direction
                return
        if Direction != self.Feeder.Clockwise:
            self.Feeder.Stop()
        #jog feeder left or right
        self.Feeder.SetOptions(LimitEnable =not self.Feeder.AtLimit,
                               ContCycle = False,
                               CycleEnable = False,
                               )
        
        self.Feeder.AccelerationTime =0.1
        self.Feeder.SetMove(Distance, Speed, Direction)
        self.Feeder.Start()
        if Direction:
            D = "Right"
        else:
            D = "Left"
        self._CS ='Jogging Feeder {} by {:.2f} mm'.format( D, abs(Distance))
        app.SetState(self._CS)


    def NudgeFeeder(self, Distance):
        if self.Feeder.HaveReply:
            self.Feeder.CycleNudge(Distance)

    def FeederWidth(self, Distance):
        self.Feeder.SetAutoReverse(Distance)
        

    def FeederPos(self, pos):
        #position feeder
        cpos =self.Feeder.GetCurrentPosition() + self.AdapterOffset
        S = self._MS['Feeder']['homespeed']

        self.Feeder.SetOptions(LimitEnable =not self.Feeder.AtLimit,
                       ContCycle = False,
                       CycleEnable = False,
                       )
        
        self.Feeder.SetMove(pos-cpos,S)
        self.Feeder.Start()
         
        self._CS ='Positioning Feeder from {:.1f} to {:.1f}'.format(cpos, pos)
        app.SetState(self._CS)
        return True
        
        
    def AdjustSpeed(self, Adjust):
        SpindleRPM = float(self.Coil.RPM) * Adjust
        WireDiameter = self.Coil.Pitch
        FeederSpeed = WireDiameter * SpindleRPM
        self.Spindle.SpeedChange(SpindleRPM)
        self.Feeder.SpeedChange(FeederSpeed)

    def IsPaused(self):
            return self._pause and not (self.Spindle.IsRunning or self.Feeder.IsRunning)

    def Pause(self):
        # brake to stop - set Cont before AllStart
        #print(self._pause , self.Spindle.IsRunning , self.Feeder.IsRunning)   
        if self.IsPaused(): 
            self._pause = False
            self.Feeder.SetOptions(ContCycle = True, ContSteps = True)
            self.Spindle.SetOptions(ContSteps = True)
            self.PT.StartAll()
            self.CQ = self.WindDone
            self._CS ="Winding - Resume"
            app.SetState(self._CS)
        else:        
            self._pause =True
            self.PT.BrakeAll() #decelerate to stop
            self.CQ = self.WaitPause

            
    def WaitPause(self):
        if self.Spindle.IsRunning or self.Feeder.IsRunning:
            self._CS = "Braking - {:d} of {:d} Turns ".format(self.Counter.Count() , int(self.Coil.Turns))
            app.SetState(self._CS)
            return False
        else:
            #stop at pause
            self._CS = "Paused - {:d} of {:d} Turns ".format(self.Counter.Count() , int(self.Coil.Turns))
            app.SetState(self._CS)
            return True

    def Stop(self):
        self._CS ='Stopped' #motors disabled
        app.SetState(self._CS)
        self.Spindle.MotorEnable = False
        self.Feeder.MotorEnable = False
        self.Feeder.Stop()
        self.Spindle.Stop()
        #self.PT.StopAll()
        self.MQ.queue.clear()                                    

    def Motor_Power(self, enable = True):
        if enable:
            #GPIO.output(19,False)
            self._CS ='Stopped'
            app.SetState(self._CS)
            
        else:
            self.Stop()
            self._CS ='Motors Off'
            app.SetState(self._CS)
            #GPIO.output(19,True)


    def CounterCB(self):
        '''called from PTPIC when reply received'''
        app.updateturnscounter(self.Counter.Count())
        

    def FeederCB(self):
        #print("feeder callback")
        app.updatefeederposition(self.Feeder.GetCurrentPosition())
        

    def DoQueue(self):            
        #gets Move function from Queue and repeats call until True returned
        if self.CQ != None:
            if self.CQ(): #call function
                if not self.MQ.empty():
                    self.CQ = self.MQ.get()
                else:
                    self.CQ = None

            
#-------------------------------------------------------

        
def  PT_update():
    #called every looptime 
    Res = w.PT.Pollport
    t = ''
    if Res & 1:
        t=''
    if Res & 2:
        #limits hit
        t +='limits hit:'
    if Res & 4:
        t +='BufferEmpty:'
    if Res & 8:
        t +='E Stop (PTPIC):'

    app.lblPTreply.config(text=t)



    #check callback
    w.DoQueue()


    #window.update()   
    app.after(Looptime, PT_update)

    #print(Looptime)


    
###################################### main code
root=Tk()

w = Winder()
app = WinderGUI.window(root, w)
app.after(Looptime, PT_update)


root.mainloop()


        
