#RPi button object
# w.k.todd 2019
import os

from os import uname

if uname().nodename == 'FastEddy':
    from tkinter import Tk, Button
    #from tkinter import filedialog, messagebox, ttk
    from tkinter.constants import *
else:
    from gpiozero import LED, Button
    import RPi.GPIO as GPIO




#GPIO.setup(17, GPIO.IN, pull_up_down = GPIO.PUD_UP)
#GPIO.add_event_detect(17, GPIO.FALLING, callback = button1.function)
#GPIO.setup(27, GPIO.IN, pull_up_down = GPIO.PUD_UP)
#GPIO.add_event_detect(27, GPIO.FALLING, callback = button2.function)  

class PiButton(object):
    port = 0 #RPI port number
    _myfunction = None
    OneShot = False
    
    def __init__(self, port):
        self.port =port

        if uname().nodename == 'FastEddy':
            #load a tk window and buttons
            master =Tk()
            self.Button = Button(master, text="Button:" + str(port),  command = lambda: self.dofunction(0))
            self.Button.pack()
            
        else:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(port, GPIO.IN, pull_up_down = GPIO.PUD_UP)
            GPIO.add_event_detect(port,
                                  GPIO.FALLING,
                                  callback = self.dofunction,
                                  bouncetime=200,
                                  )

            
        
    def __del__(self):
        #close port
        pass

    def __repr__(self):
        return 'RPi button object (port {})'.format(self.port)

    
    def dofunction(self, event):
        if self._myfunction == None:
            print('button on port {} pressed'.format(self.port))
        else:
            self._myfunction(**self.kwargs)
            if self.OneShot:
                self._myfunction = None #one shot function
                
    def setfunction(self, function, Once = False, **kwargs):
        self._myfunction = function
        self.OneShot = Once
        self._mykwargs = kwargs
