#!/usr/bin/python3

#simple PTHserial module test - single axis test

from PTPIC import *
import time

PT = PTPIC() #create a PTPic object
PT.DEBUG = True
#S = PT.GetVersion
#print(S)




#PT.ToggleMotorEnable()

while input("test axis [input Q to quit] ") != "Q": # Q to quit

    A = input("Axis  (X,Y,Z,E) ")

    if A in "xX":
        axis = PT.GetXaxis
        axis.StepsPerUnit =  1000
        
    elif A in "yY":
        axis = PT.GetYaxis
        axis.StepsPerUnit = 135 #(96 * 32 ) /(15*1.5)
        axis.EnablePolarity(False) #motor enable = low
        
    elif A in "zZ":
        axis = PT.GetZaxis
        axis.StepsPerUnit = 400 * 8 #16 
    elif A in "eE":
        axis = PT.GetEaxis
        axis.StepsPerUnit = 100 * 32 # 200 * 16

    axis.ADCLink = 0

    AD = input("Acceleration Time (Seconds) ")
    if  AD !="":
        Ramp = AD

    sRPM=input(" RPM ")
    
    if sRPM !="":
        RPM = float(sRPM)

    sRevs = input(" REVS ")
    if sRevs !="" :
         Revs= float(sRevs)
         
    D = input(' Direction (or A for auto reverse) ')
    AR=0
    if D in "aA":
        AR = float(input(" Reverse after Revs " ))
        Direction = False #True

    else:
        Direction = float(D) >0 

    #ZMotorEnable = PT.GetAUX3 #used as a Z enable on testbox
    #ZMotorEnable.SetAux()

    if AR >0 :
        axis.SetAutoReverse(AR)
    else:
        axis.SetAutoReverse(0)

    x = PT.Pollport #clear any false messages
    print(">>",x)
    
    #axis.MotorEnable =False #disable motor when stopped
    axis.MotorEnable =True  #motor enabled when stopped
    axis.AccelerationTime = float(Ramp)
    axis.SetMove(Revs, RPM, bool(Direction))
    
    axis.LimitEnable(True)
    axis.Start()
    #PT.StartAll()
    print('Running')
    #X=True
    while axis.IsRunning:
        x = PT.Pollport # must poll the port to read the serial data
        if x : print(">>",x) # PT.pollport returns a fault code
        #print(axis.IsRunning)
        
    #axis.MotorEnable = False #disable motors while waitiing for user
    
    #axis.SetMove(0,0,False)
    
    print('Stopped')

    #PT.Reset()
    




