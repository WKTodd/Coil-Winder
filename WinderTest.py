#!/usr/bin/python3

#simple PTHserial module test - single axis test

from PTPIC import *
import time

PT = PTPIC() #create a PTPic object
PT.DEBUG = True
#S = PT.GetVersion
#print(S)


Spindle = PT.GetXaxis
Spindle.StepsPerUnit =  1000
Spindle.Name = "Spindle"
Spindle.Units = "Revs"
Feeder = PT.GetYaxis
Feeder.StepsPerUnit = (96 * 32) /(15*1.5) #steps per rev/(Teeth * Module)
Feeder.MotorEnable = False
Feeder.EnablePolarity(False) #motor enable = low

Feeder.Name = "Spindle"
Feeder.Units = "mm"

#PT.ToggleMotorEnable()




while input("Winder Test [input Q to quit] ") != "Q": # Q to quit
    Cont = input("Continue? :") in "Yy"
    Feeder.Continuation(Cont)
    Feeder.MotorEnable = Cont #lock the motors if continuing
    Spindle.MotorEnable = Cont
    
    BobbinWidth = float(input("Bobbin Width: ")) # 9 
    SpindleRPM = float(input("RPM: ")) #300 
    
    Turns = float(input("Number of Turns: " ))
    WireDiameter = float(input("Wire diameter (mm): "))
    Spindle.AccelerationTime = 5
    Feeder.AccelerationTime = 5
    
    TPL = int(BobbinWidth / WireDiameter)
    Feeder.SetAutoReverse((TPL-1) * WireDiameter)
    FeederDistance = WireDiameter * Turns
    FeederSpeed = WireDiameter * SpindleRPM
    
    Spindle.SetMove(Turns, SpindleRPM)
    Feeder.SetMove(FeederDistance, FeederSpeed,True)

    PT.StartAll()
    print('Running')
    #X=True
    while Spindle.IsRunning and Feeder.IsRunning:
        x = PT.Pollport # must poll the port to read the serial data
        if x : print(">>",x) # PT.pollport returns a fault code
        

    print('Stopped')
              
