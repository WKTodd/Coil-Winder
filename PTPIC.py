#-------------------------------------------------------------
#       PTPIC pyserial test object
#       Pulse Train PIC (12F1572)
#       (c) W.K..Todd 2018/19 - 10/10/2021 - port defined on init
ModuleVersion = "1.22"
PICVersion = "1.60"
PythonVersion  = "3.7.6"
#-----------------------------------------------------------
#  Axis pic commands (10chars plus  colon terminator) x=axis (X,Y,Z etc) or A=all
#
#   xDhhhhhhhh:     32bits hex number of steps
#   xChhhhhhhh:     32bits hex steps before reverse (cycle)
#   xFdc0Ihhhh:     d - initial direction 0 or 1
#                   c - cycle enable 0 or 1
#                   I - immediate (update now - accelerate or decelerate as set)
#                   hhhh - 16bits hex Frequency (Hz) - max 20kHz
#
#   xA0000hhhh:     hhhh - 16bits hex Acceleration time (CentiSeconds [10mS])
#
#   xB00000000:     Brake (decelerate to stop if set)
#
#   xSel000000:     Stop (stop immediate)
#                   e = 0 or 1 motor enable/disabled 
#		            l - 0 or 1 check if at limit (returns xL: if at limit)
#
#   xGel000000:     Go (from stop)
#                   e = 0 or 1 motor enabled/disabled when stopped
#                   l = Limit input enabled 1 /disabled 0
#
#   xNhhhhhhhh:     Nudge - move cycle left or right (32bit Hex)
#       	    <=7fffffff = positive = left = dir 0
#                   >7fffffff = negative = right =dir 1
#
#   xOelnk0pms	    Options
#   		    e - 0 or 1 motor enable  
#   		    l - 0 or 1 limit enable
#   		    n - continue  cycle count and direction
#               k - continue from pause (steps not reset)
#   		    p = polarity 0 falling edge or 1) rising edge
#   		    m - Motor enable active 1= high 0=low
#   		    s - limit Sensor active 1=high 0=low
#
#   XP0000000n:     Position
#                   n=0 report current steps
#                   n=1 report cycle position (from left side)
#
#   xV00000000:     Version string
#
# Responces:
#   PTPIC vx.xx:
#   xShhhhhhhh: - axis has stopped
#                   hhhhhhhh= ABS position (32bit hex) 
#   xNhhhhhhhh: - Cycle Position
#                   hhhhhhhh= position (32bit hex)
#   xG: - axis is running
#   xC: - Cycle has reversed
#   xL: - Limit hit (when enabled or checked)
####################################################################

#-------------------------------------------------------------

import serial

#----------------------------------------------------

    
class Axis(object):
    '''PTPIC Axis object to handle axis interactions:
      variables
      Name="" #user name for axis channel e.g. Wrist, Elbow, Shoulder
    __channel = "" #channel used for ptpic  X,Y,Z or E readonly
    Units anything you like (e.g. Revs, metres ,mm, inches, feet )
    Speed in Units per Minute
    AccelerationTime in seconds (float)
    __ptpic # reference back to PTPIC object
    '''

    limitenabled = False
    Clockwise=True
    StepsPerUnit =1.0 #steps per unit  (e.g 1045.67/mm , 12800/Revolution, or 25400/inch)
    Unit ="" #user unit variable (e.g. Revs, mm, Inch)
    StepsToDo = 0 #number of steps (integer) to do in Move
    StepsDone = 0 #number of steps so far (current position)
    Freq=0 #calculated frequency of Move
    AccelerationTime = 0.0 #seconds (float)
    MaxSpeed = 0
    Polarity = False
    CycleEnable = False
    CycleCount=0
    CycleSteps = 0 #number of steps to each cycle
    CycleDirection = False #current direction - toggled by cycle change xC
    ABSPos = 0 #absolute position  set by xShhhhhhhhhh reply
    contcycle = False  #
    contsteps = False
    MotorEnable = False
    IsRunning = False
    AtLimit = False
    Paused = False
    Distance = 0 #to move in units

    ClockwiseIsNegative = False #reverse motor direction
    enablepolarity = False # false = motorenabled low
    limitpolarity = False  #false = falling edge
    Update = False
    CallBack = None
    
    def __init__(self, channel, ptpic, callback=None):
        #save ptpic object for callbacks
        self.__channel = channel
        self.Name = channel + "axis" #default name
        self.__ptpic = ptpic #refernce the creator object
        if callback:
            self.CallBack = callback
        

        #print(channel , ptpic, self,callback ) #debug

    def __del__(self):
        #log out of ptpic

        pass
    def __repr__(self):
        return 'Pulse Train PIC {} Axis Object: {}'.format( self.__channel , self.Name )
    
    @property
    def GetChannel(self):
            return self.__channel

    #@property
    def GetCurrentPosition(self):
        #only valid when stopped
        return self.ABSPos /self.StepsPerUnit
            

    @property
    def GetLimitEnable(self):
        return self.limitenabled

    def SetOptions(self, **Options):
        #set all options = keyword args
        for key, value in Options.items():
            if key == "ContCycle":
                self.contcycle = value
            elif key == "ContSteps":
                self.contsteps = value
            elif key == "LimitEnable":
                self.limitenabled = value
                self.AtLimit = False
            elif key == "LimitPolarity":
                self.limitpolarity = value
            elif key == "EnablePolarity":
                self.enablepolarity = value
            elif key == "CycleEnable":
                self.CycleEnable = value
            elif key == "MotorEnable":
                self.MotorEnable = value
                
        self.__ptpic.SetAxisOptions(self)
            

    def ContCycle(self, enable=True):
        self.contcycle = enable
        self.__ptpic.SetAxisOptions(self)

    def ContSteps(self, enable=True):
        self.contsteps = enable
        self.__ptpic.SetAxisOptions(self)

        
    def LimitEnable(self, enable=True):
        self.AtLimit = False
        self.limitenabled = enable
        self.__ptpic.SetAxisOptions(self)
        
    def EnablePolarity(self, enable):
        self.enablepolarity = enable
        self.__ptpic.SetAxisOptions(self)

    def LimitPolarity(self, enable):
        self.limitpolarity = enable
        self.__ptpic.SetAxisOptions(self)    

    def SetMove(self, Units, UnitsPerMin, Clockwise =True): #speed in units per minute
        """SetMove:
Units : distance to move (can be negative to reverse moves)
UnitsPerMin : Speed (will alway take asb() value
Clockwise : True is one way , False the other way"""
        self.Distance = Units
        #calculate steps
        self.StepsToDo = abs(int(Units * self.StepsPerUnit))
        #calculate frequency
        self.Freq = UnitsPerMin * self.StepsPerUnit / 60
        if self.Freq > 20000:
            #raise exception
            print("Error - Axis.SetMove: Frequency too high (max 20kHz for 12F1572 @32Mhz) ")
        
        if Units < 0:
            self.Clockwise = False != self.ClockwiseIsNegative #xor with CW=Neg
        else:
            self.Clockwise = Clockwise != self.ClockwiseIsNegative
            
        self.CycleDirection = self.Clockwise
        
        #call ptpic
        self.__ptpic.SetAxisMove(self.__channel,self.StepsToDo,self.Freq ,self.AccelerationTime, self.ControlWord())

    def SetABSPosition(self, Position): 
        '''SetABSPosition: set absolute postion counter in chip'''
        self.ABSPos = int(Position * self.StepsPerUnit)
        self.__ptpic.SetABSPosition(self.__channel, self.ABSPos)
        
        
    def ControlWord(self, Immediate = False):
        CW =str(int(self.Clockwise))
        CW+=str(int(self.CycleEnable))           
        CW+="0"
        CW+=str(int(Immediate))     
        return CW
            
    def SetAutoReverse(self, Units):
        """ SetAutoReverse: number of units before direction is reversed (CycleEnable must be True)"""
        #calculate steps
        self.CycleSteps = abs(int(Units * self.StepsPerUnit))  
        self.CycleEnable = Units >0
        #call ptpic
        self.__ptpic.SetAxisAutoReverse(self.__channel, self.CycleSteps)


    def Start(self):
        """ Start: start axis moving as set by SetMove"""
        if not self.IsRunning:
            self.Update = False
            self.__ptpic.StartAxis(self)            
            self.IsRunning = True
            
    def Stop(self):
        """ Stop: Immediate"""
        self.Update = False
        self.__ptpic.StopAxis(self, False)
        

    def Brake(self):
        """ Brake: slow to stop"""
        
        self.Update = False
        self.__ptpic.StopAxis(self, True)
        

    def CycleNudge(self, Units):
        """CycleNudge: signed adjustment to cycle position"""
        steps = int(Units * self.StepsPerUnit)
        self.Update = False
        self.__ptpic.Nudge(self.__channel, steps)        


    def SpeedChange(self, UnitsPerMin):
        """SpeedChange: instant speed change"""
        self.Freq = UnitsPerMin * self.StepsPerUnit / 60
        CW = self.ControlWord(True) 
        self.__ptpic.AxisSpeedChange(self.__channel, self.Freq, CW)
        
    def HaveReply(self, state):
        self.Updated= state
        if self.CallBack:
            self.__ptpic.CBQ.append(self.CallBack)

#**********************************************************************
#  Serial control commands					      *
#  All commands are 10 ascii chars				      *
#    (Axis, Command, and 8 hex) terminated with colon (:)	      *
#**********************************************************************  
#   CC0000000c: Report current count
#		c = 0 or 1 transmit count 0 or 1 as 32bit hex
#   CO000000BA: Options
#		A = 1 enable per turn message om REV0
#		B = 1 enable per turn message om REV1    
#   CR000000xy: Reset
#		x = 1 reset count 0
#		y = 1 reset count 1
#   CV00000000:	Get version string
#    
# Responces:
#   CounterPICx.xx: - x.xx = version
#   Cchhhhhhhh: - current count
#               c = channel 0 or 1 
#               hhhhhhhh= position (32bit hex)
#**********************************************************************

class Counter(object):
    '''PTPIC Counter object to handle Counter actions:
      variables
      Name="" #user name for axis channel e.g. Revs, Widgets etc
    __channel = "" #channel used for ptpic  X,Y,Z or E readonly
    Unit anything you like (e.g. Revs, metres ,mm, inches, feet )
    __ptpic # reference back to PTPIC object
    '''

    _count = 0 #current count
    Unit ="" #user unit variable (e.g. Revs, mm, Inch)
    Update = False
    CallBack = None
    MPT = False #message per turn
    def __init__(self, channel, ptpic, callback = None):
        #save ptpic object for callbacks
        self.__channel = channel
        self.Name = channel + "axis" #default name
        self.__ptpic = ptpic #refernce the creator object
        self.CallBack = callback
        #print(channel , ptpic, self,callback) #debug

    def __del__(self):
        #log out of ptpic

        pass
    def __repr__(self):
        return 'Pulse Train PIC {} Counter Object: {}'.format( self.__channel , self.Name )
    
    @property
    def GetChannel(self):
            return self.__channel

    def GetCount(self):
        self.Update = False
        self.__ptpic.GetCount(self.__channel)
        return self._count

    def Count(self):
        self.Update = False
        return self._count

    def Reset(self):
        #send reset command
        self._count=0
        self.__ptpic.ResetCounter(self.__channel)

    def SetOptions(self, **Options):
        #set all options = keyword args
        for key, value in Options.items():
            #print(key,value)
            if key=="MPT":
                self.MPT = value

        self.__ptpic.SetCounterOptions(self.__channel)

    def HaveReply(self, state):
        self.Updated= state
        if self.CallBack:
            self.__ptpic.CBQ.append(self.CallBack)
#---------------------------------------------------------------

class PTPIC(object):
    '''ptpic object to handle ptpic interactions'''
    
    __SP = None #object() #place holder for serial port object for ptpic
    __Baud = 19200 #9600
    __port='com7' #for windows
    #__port='/dev/serial0' #for RPi
    RS = "" #response string from hat
    Limit = False
    Estop = False
    DEBUG = False #enable prints debug statements
    PTOs = {}  #dictionary to hold pt objects like ADCs, AUXs  Axes etc.
    Buffering = False
    BufferEmpty = True
    BufferCount = 0
    CBQ=[]
    def __init__(self, SerialPort = 'Simulation', Baud = 19200):
        #print("ptpic created")

        #create my serial port object and open it
        self.__port = SerialPort  
        self.__Baud = Baud   
        
        if 'Sim' in self.__port:
            from PTPICsim import Sim
            self.__SP = Sim()
        else:
            Sim = None
            self.__SP = self.init_serial()    
            
        #reset ptpic
        self.sendtohat("AS00000000")

        
    def __del__(self):
        #send all stop to hat here
        self.sendtohat("AS00000000")
        self.__SP.close()
        
    def __repr__(self):
        return 'Pulse Train PIC Object: {}'.format(ModuleVersion )
    

#### ptpic read only properties
        
    @property   
    def Pollport(self):
        """Pollport: should be call regularly to ensure status is updated"""    
        response = None
        w = self.__SP.in_waiting 
        if  w:
                sbyte = self.__SP.read(w) #read serial buffer

                self.RS += sbyte.decode() #convert bytes to string
                
                C = self.RS.rfind(":")
                response = self.RS[0:C].split(":") #create list of responses
                self.RS = self.RS[C:] # buffer incomplete reponses
                #Parse response to set ADCs, Version etc.
                self.parse_responses(response)
                #print(self.CBQ)
                for CB in self.CBQ:
                    if CB:
                        CB() #do call backs

                self.CBQ=[]
                    
        #return response #return list
        Flag =0       
        if self.Estop:
            Flag += 8
        if self.Buffering and self.BufferEmpty:
            Flag += 4
        if self.Limit:
            Flag += 2
        if w:
            Flag += 1
        return Flag
    
    @property
    def GetVersion(self):
        #send version string
        if self.version == "":
            #if version is empty then wait for version to be assigned by pollport
            self.sendtohat("XV00000000")
                
            while self.version == "":
                _ = self.Pollport
            
        return self.version
    
    #@property
    def GetXaxis(self, callback = None):
        return self._getaxis("X", callback)
    
    #@property
    def GetYaxis(self, callback = None):
        return self._getaxis("Y",callback)
    
    #@property
    def GetZaxis(self, callback = None):
        return self._getaxis("Z",callback)
    
    #@property
    def GetEaxis(self, callback = None):
        return self._getaxis("E",callback)
    
    #@property
    def GetCounter0(self, callback = None):
        return self._getcounter("0",callback)    


############ Axis Methods ##########################

        
    
    def _getaxis(self,ch,cb):
        if not ch in self.PTOs:
            self.PTOs[ch] = Axis(ch, self,cb) #add to pto dictionary
        return self.PTOs[ch]       

    def GetAxisSteps(self, ch, Cycle):
        #request steps or cycle position
        self.sendtohat(ch + "P0000000" + str(int(Cycle)))
        

    def StartAxis(self, Axis):
        '''Start single axis X,Y,Z, or All A'''
        Axis.IsRunning = True
        self.Limit = False
        
        if Axis.limitenabled:
            CW = "1000000"
        else:
            CW = "0000000"
            
        if Axis.MotorEnable:
            self.sendtohat(Axis.GetChannel + "G1" + CW)
        else:
            self.sendtohat(Axis.GetChannel + "G0" + CW)

    def StopAxis(self, Axis, Brake = False):
        '''Start single axis X,Y,Z, or All A'''
        if Brake:
            CW = "B" #slow to stop
        else:
            CW = "S" #stop immediately
            
        if Axis.MotorEnable:
            self.sendtohat(Axis.GetChannel + CW + "10000000")
        else:
            self.sendtohat(Axis.GetChannel + CW + "00000000")
            
    def StartAll(self):
        '''start all axes'''
        self.sendtohat("AG00000000")
        self.__setrunflags()
        
    def StopAll(self):
        '''stop all axes'''
        self.sendtohat("AS00000000")
        self.__setrunflags(False)

    def BrakeAll(self):
        '''brake all axes'''
        self.sendtohat("AB00000000")
        #self.__setrunflags(False)        


    def SetAxisMove(self, ch, steps, freq, acctime, CW):
        '''create formatted strings and pass to serial'''
        
        self.sendtohat(ch + 'D{:08x}'.format(steps))
        self.sendtohat(ch + 'A0000{:04x}'.format(int(acctime*100))) #convert seconds (float) to centiseconds
        self.sendtohat(ch + 'F'+ CW +'{:04x}'.format(int(freq)))

    def SetABSPosition(self, ch, steps):
        if steps >=0:
            command = ch + 'P{:08x}'.format(steps)
        else:
            command = ch + 'P{:08x}'.format(0x100000000 + steps)
        self.sendtohat(command)

    def Nudge(self,ch, steps):
        if steps >=0:
            command = ch + 'N{:08x}'.format(steps)
        else:
            command = ch + 'N{:08x}'.format(0x100000000 + steps)
        self.sendtohat(command)

    def SetAxisAutoReverse(self,ch, steps):
        command = ch + 'C{:08x}'.format(steps)
        self.sendtohat(command)
        
    def AxisSpeedChange(self,ch, freq, CW):
        #change speed now
        self.sendtohat( ch +'F'+CW+'{:04x}'.format(int(freq)))

    def SetAxisOptions(self, Axis):
        #send option string
        OS = self.GetOptionString(Axis)
        self.sendtohat(Axis.GetChannel + "O" + OS) #set options
        pass
        
    def Reset(self):
        self.sendtohat("AS00000000")
        self.__setrunflags(False)

    def GetOptionString(self, Axis):
            OS = str(int(Axis.MotorEnable))
            OS += str(int(Axis.limitenabled))
            OS += str(int(Axis.contcycle))
            OS += str(int(Axis.contsteps))
            OS += "0"
            OS += str(int(Axis.Polarity))
            OS += str(int(Axis.enablepolarity))
            OS += str(int(Axis.limitpolarity))
            return OS

## counter methods

    def _getcounter(self, ch, cb):
        if not ch in self.PTOs:
            self.PTOs[ch] = Counter(ch, self, cb) #add to pto dictionary
        return self.PTOs[ch]

    def ResetCounter(self, channel):
        self.sendtohat("CR00000001")

    def GetCount(self, channel):
        self.sendtohat("CC0000000" + channel)

    def SetCounterOptions(self,ch):
        OS = "0000000" + str(int(self.PTOs[ch].MPT))
        self.sendtohat("CO" + OS) #set options
        
#### Private object methods ########################
        
#initialise serial port for ptpic
#
#Returns: serial port object
#
    def init_serial(self):
        try:
            SP = serial.Serial(
                    port= self.__port,
                    baudrate = self.__Baud,
                    bytesize = serial.EIGHTBITS,
                    parity = serial.PARITY_NONE,
                    stopbits = serial.STOPBITS_ONE,
                    xonxoff = False,
                    rtscts = False,
                    write_timeout = 2,
                    timeout = 2,
                    ) 
            return(SP)
        except Exception as e:
            #error handler 
            print('init serial - Error opening serial port /n/l %s' % e)
            return(False)

    
    def sendtohat(self,command):  #make private after debugging __sendtohat
        #send command to serial port
        sth = command + ":"
             
        self.__SP.write(bytes(sth, 'utf-8'))
        #time.sleep(0.012 * len(command))
        if self.DEBUG: print("sendtohat>>>",sth) #debug

        

    def parse_responses(self,response_list):
        #search list for useful replies
        for res in response_list:
            
            if res !="":
                if self.DEBUG : #*****
                    print("parser>>>" + res) #debug

                if res[0] == "C": #counter responce
                    ch = "0" #res[1]
                    self.PTOs[ch].HaveReply(True)
                    if res[1] == "0": 
                        self.PTOs[ch]._count = int(res[2:10],16)                    
                        
                    elif res[1] == "P":
                        self.PTOs[ch]._count +=1
                        
                    elif res[1] == "N":
                        self.PTOs[ch]._count -=1

                    

                else: #axis responces

                    if res[1] == "C": #cycle
                        ch = res[0]
                        #increment cycle count
                        self.PTOs[ch].CycleCount +=1
                        self.PTOs[ch].CycleDirection  = not self.PTOs[ch].CycleDirection
                        #self.PTOs[ch].HaveReply(True)
                    if res[1] == "G": # running
                        ch = res[0]
                        self.PTOs[ch].IsRunning = True
                        self.PTOs[ch].HaveReply(True)
                        
                    if res[1] == "L": #limits hit
                        ch = res[0]
                        self.PTOs[ch].IsRunning = False
                        self.PTOs[ch].AtLimit = True
                        self.Limit = True

                    if res[1] == "N": #Nudged or Position'1'
                        ch = res[0]
                        self.PTOs[ch].CyclePos = int(res[2:10],16)
                        self.PTOs[ch].HaveReply(True)
                        
                        
                    if res[1] == "S": #stop
                        #axis stopped and position reported
                        ch = res[0]
                        self.PTOs[ch].IsRunning = False
                        self.PTOs[ch].ABSPos = int(res[2:10],16)
                        self.PTOs[ch].HaveReply(True)


                if "PIC" in res:
                    self.version = res
                               
    def __setrunflags(self,F=True):
        for ch in "XYZE":
            try:
                self.PTOs[ch].IsRunning = F
            except:
                pass

    def __extractnum(self, res):
        #print(res)
        c=''
        for s in res:
            if s.isdigit():
                c += s
        return int(c)
    
#----------------------------------------------------------------    
