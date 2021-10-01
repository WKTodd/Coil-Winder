#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 18 15:59:52 2020
edited 02/06/21
@author: bill
"""
import time
#import tkinter
from tkinter.constants import *
from tkinter import Tk,  Label, StringVar

class Sim(object):
    '''simulates a serial connection to a PTPIC '''

    _in_waiting = 0
    res = ""
    PICS = []
    # status  = StringVar()
    def __init__(self):
        self.Xaxis = PICptg(self,"X", 0)
        self.Yaxis = PICptg(self,"Y", 768*50 ) #feeder is 768steps/mm * +/-25mm mm travel
        self.Counter = PICctr(self,"C",self.Xaxis, -400)# spindle is 400steps/rev anticlock
        self.PICS.append(self.Xaxis)
        self.PICS.append(self.Yaxis)
        self.PICS.append(self.Counter)
        
        master = Tk()
        master.title ("PTPIC Simulator")
        master.geometry("400x100")
        self.Statuslab = Label(master,text= "status")
        self.Statuslab.pack()

        pass
    
    def read(self, nob):
        tx = bytes(self.res[0:nob], 'utf-8')
        self.res = self.res[nob:-1]
        self._in_waiting = len(self.res)
        return tx
    
    def write(self, bytedata):
        mes = bytedata.decode()
        #print(len(mes))
        self.parse(mes)
        return
    
    @property
    def in_waiting(self):
        #print("in_waiting called")
        St = ""
        for P in self.PICS:
            P.Sim()
            St += P.Status() + "\n"
            
        self.Statuslab.configure(text = St)
       
        #self.Statuslab.pack()
        #print(St   )
        return self._in_waiting

    def parse(self, mes):
        for P in self.PICS:
            self.res  += P.parse(mes)
            self._in_waiting += len(self.res)
    
    def RX(self, mes):
        self.res  += mes
        self._in_waiting += len(self.res)  
        

class PICptg(object):
    '''PIC pulse train generator simulator v1'''   
    Ch = ""
    Port = None
    StepsToGo = 0
    ContSteps = False
    Distance = 0
    Running = False
    Acc = 0
    AccStepsPerSec = 0
    AccFlg =False
    DcnFlg = False
    Cyc =0
    CycPos = 0 #steps before reverse
    CycEn = False
    ContCyc = False
    AtLimit = False
    LimitEnable = False
    braking = False
    Frequency = 0
    TargetFreq =0
    CurrentFreq =0
    lasttime = 0
    DIR = False #left
    ABSPos =0
    ABSLimit = 0

   
    def __init__(self, port, ch, ABSlimit):
        self.Ch = ch
        self.Port = port
        self.ABSLimit = ABSlimit

    def Status(self):
        if self.Running:
            if self.DIR:
                d = ">>>"
            else:
                d ="<<<"
        else:
            d="---"

        if self.AccFlg:
            acc = "^"
        elif self.DcnFlg:
            acc = "v"
        else:
            acc = "-"
        
        if self.AtLimit:
            if self.DIR:
                d = ">>|"
            else:
                d ="|<<"            
            
        return f"Channel {self.Ch}: ABSPos:{int(self.ABSPos)}:{d}:{int(self.CurrentFreq)}Hz:{acc}:{int(self.Frequency)}:{self.Acc:.2f}s"
    
    def Sim(self):
        #called in loop so pic can simulate motion
        T = time.time()-self.lasttime #calc seconds passed
        self.lasttime = time.time()
        pulses = 0
        if self.Running:
            
            if self.AccFlg:
                self.CurrentFreq += self.AccStepsPerSec * T
                self.AccFlg = self.CurrentFreq < self.TargetFreq
                
            if self.DcnFlg:
                self.CurrentFreq -= self.AccStepsPerSec * T
                self.DcnFlg = self.CurrentFreq > self.TargetFreq 
                if self.CurrentFreq <=0:
                    self.Stop()
                    Pos = int(abs(self.ABSPos))
                    self.TX(f"S{Pos:08x}")                    
            
            pulses = self.CurrentFreq * T
            self.StepsToGo -= pulses
            if self.StepsToGo <=0:
                self.Stop()
                Pos = int(abs(self.ABSPos))
                self.TX(f"S{Pos:08x}")   
                
            if self.DIR:
                self.ABSPos += pulses
                if self.ABSLimit > 0 and self.ABSPos > self.ABSLimit and self.LimitEnable:
                    self.AtLimit = True
                    self.Stop()
                    self.TX("L")
                else:
                    self.AtLimit = False                    

            else:
                self.ABSPos -= pulses
                if self.ABSLimit > 0 and self.ABSPos <=0 and  self.LimitEnable:
                    self.AtLimit = True
                    self.ABSPos = 0
                    self.TX("L")
                    self.Stop()
                else:
                    self.AtLimit = False                
                
            if self.CycEn:
                self.CycPos -= pulses
                if self.CycPos <=0:
                    self.DIR = not self.DIR
                    self.CycPos = self.Cyc
                    self.TX("C")
                    
    def Stop(self):
            self.Running = False
            self.AccFlg = False
            self.DcnFlg = False        
            
    def TX(self, mes):
        tx = f"{self.Ch}{mes}:"
        self.Port.RX(tx)
        
        
    def parse(self, mes):
        #all messages are 10 chars 
        ch = mes[0]
        res =""
        if ch == "A" or ch == self.Ch:
            cmd = mes[1]
            N32 = int(mes[2:10],16)
            N16 = int(mes[6:10],16)
            
            if cmd == "A":
                #accelerate
                self.Acc = N16/100

                
            if cmd == "B":
                #brake
                self.TargetFreq = 0
                self.DcnFlg = True
                self.AccFlg = False
                
            if cmd == "C":
                #cycle
                self.Cyc = N32
                
            if cmd == "D":
                #number of steps to output
                self.Distance = N32
                
            if cmd == "F":
                #frequency
                self.DIR = mes[2]=="1"
                self.CycEn = mes[3]=="1"
                self.Frequency = N16  
                if mes[5]=="1":
                    if self.Acc:
                        self.AccStepsPerSec = abs(self.Frequency-self.CurrentFreq)/self.Acc
                        self.AccFlg = self.CurrentFreq < self.Frequency
                        self.DcnFlg = self.CurrentFreq > self.Frequency
                    else:
                        self.CurrentFreq = self.Frequency
                    
            if cmd == "G":
                #go
                self.Running = True
                if not self.ContSteps:
                    self.StepsToGo = self.Distance
                if not self.ContCyc:
                    self.CycPos = self.Cyc
                if self.Acc >0:
                    self.CurrentFreq = 0
                    self.AccStepsPerSec = self.Frequency/self.Acc
                    self.AccFlg = True
                    self.TargetFreq = self.Frequency
                else:
                    self.CurrentFreq = self.Frequency
                    
                self.LimitEnable = mes[3]=="1"
                res = "G"
                
            if cmd == "N":
                #Nudge
                self.Nudge(N32)
                res = f"P{int(self.StepsToGo):08x}"
            if cmd == "O":
                #options
                self.LimitEnable = mes[3]=="1"
                self.ContCyc = mes[4]=="1"
                self.ContSteps = mes[5]=="1"
                
            if cmd == "P":
                #StepsToGo
                if mes[9] == "0":
                    res = f"P{int(self.StepsToGo):08x}"
                else:
                    res = f"C{int(self.CycPos):08x}"
                    
            if cmd == "S":
                #options
                self.Stop()
                self.CurrentFreq = 0
                res = f"S{int(self.StepsToGo):08x}"
                
            if cmd == "V":
                #version
                res = f" PIC simulation"        
        if res=="":
            return res
        else:
            return f"{self.Ch}{res}:"
    
        def Nudge(self, N):
            self.StepsToGo +=N
            
            
class PICctr(object):
    
    Ch = ""
    Port = None
    Driver0 = None
    Driver1 = None
    ratio0 = 0
    ratio1 = 0
    Report0 = False
    Report1 = False
    Count0 = 0
    Count1 = 0
    OutCnt0 = 0
    OutCnt1 = 0
    lastpos0 = 0
    lastpos1 = 0
    
    def __init__(self, port, ch, driver0=None, ratio0=0, driver1=None, ratio1=0):
        self.Ch = ch
        self.Port = port
        self.Driver0 =driver0
        self.ratio0 = ratio0
        self.Driver1 =driver1
        self.ratio1 = ratio1
    
    def Status(self):
        return f"Count:{int(self.Count0)}"
    
    def Sim(self):
        if self.Driver0:
            D = self.Driver0.ABSPos - self.lastpos0
            self.lastpos0 = self.Driver0.ABSPos
            self.Count0 += D/self.ratio0
        if self.Driver1:
            D = self.Driver1.ABSPos - self.lastpos1
            self.lastpos1 = self.Driver1.ABSPos
            self.Count1 += D/self.ratio1                 
        
        if self.Report0 and abs(self.Count0 - self.OutCnt0 ) >0:
            if (self.Count0 - self.OutCnt0)>0:
                while self.OutCnt0 < int(self.Count0):
                    self.TX("P") 
                    self.OutCnt0 += 1
            else:
                while self.OutCnt0 > int(self.Count0):
                    self.TX("N") 
                    self.OutCnt0 -= 1                
    

    def TX(self, mes):
        tx = f"{self.Ch}{mes}:"
        self.Port.RX(tx)    
    
    def parse(self, mes):
        #all messages are 10 chars 
        ch = mes[0]
        res =""
        if ch == self.Ch:
            cmd = mes[1]
            #N32 = int(mes[2:10],16)
            #N16 = int(mes[6:10],16) 
            if cmd == "C":
                #report count
                if mes[9]=="1":
                    res = f"1{int(self.Count1):08x}"            
                else:
                    res = f"0{int(self.Count0):08x}"         
            if cmd == "O":
                #options
                self.Report1 = mes[8]=="1" 
                self.Report0 = mes[9]=="1"
            if cmd == "R":
                #options
                if mes[8]=="1":
                    self.Count0 =0
                if mes[9]=="1":
                    self.Count1 =0
            if cmd == "V":
                #version
                res = f" PIC simulation"                         
            
                
        if res=="":
            return res
        else:
            return f"{self.Ch}{res}:"
                
        