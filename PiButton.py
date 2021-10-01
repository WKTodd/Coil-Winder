#RPi button object
# w.k.todd 2019

from gpiozero import LED, Button
import RPi.GPIO as GPIO

#GPIO.setup(17, GPIO.IN, pull_up_down = GPIO.PUD_UP)
#GPIO.add_event_detect(17, GPIO.FALLING, callback = button1.function)
#GPIO.setup(27, GPIO.IN, pull_up_down = GPIO.PUD_UP)
#GPIO.add_event_detect(27, GPIO.FALLING, callback = button2.function)  

class PiButton(object):
    port = 0 #RPI port number
    _myfunction = None
    _mykwargs = None    
    OneShot = False
    def __init__(self, port):
        self.port =port
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(port, GPIO.IN, pull_up_down = GPIO.PUD_UP)
        GPIO.add_event_detect(port,
                              GPIO.RISING,
                              callback = self.dofunction,
                              bouncetime=300,
                              )
        
##    def __del__(self):
##        #close port
##        pass

    def __repr__(self):
        return 'RPi button object (port {})'.format(self.port)

    
    def dofunction(self, event):
        if self._myfunction == None:
            print('button on port {} pressed'.format(self.port))
        else:
            self._myfunction(**self._mykwargs)
            if self.OneShot:
                self._myfunction = None #one shot function

    def setfunction(self, function, once = False, **kwargs):
        self._myfunction = function
        self._mykwargs = kwargs
        #print(kwargs)
        self.OneShot = once
