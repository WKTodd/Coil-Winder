# OLED display object
# W.K.Todd 2019

#import time
#import os
Win = False

from os import uname

if uname().nodename == 'FastEddy':
    Win=True
    from WindowsOLED import Wdisp    
else:
    #import Adafruit_GPIO.SPI as SPI
    import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

class OLED(object):

    def __init__(self):
        
        # Raspberry Pi pin configuration:
        RST = 24

        if Win:
            self.disp = Wdisp()
        else:
            self.disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST)

        # Initialize library.
        self.disp.begin()

        # Create blank image for drawing.

        self.width = 128 #self.disp.width
        self.height = 64 #self.disp.height
        self._image = Image.new('1', (self.width, self.height))
        self.draw = ImageDraw.Draw(self._image)
        #Load default font.
        #self.font = ImageFont.load_default()
        self.font = ImageFont.truetype("/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf", 20)
        self.clear()
        
    def __del__(self):
        self.clear()

    def __repr__(self):
        return 'OLED display object for SSD1306 I2C'

    def clear(self):
        # Clear display
        self.disp.clear()
        self.draw.rectangle((0,0,  self.width, self.height,), outline=0, fill=0)
        self._show()
        


    def write(self, text, size = 18):
        self.font = ImageFont.truetype("/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
                                           size,
                                           )
        self.draw.rectangle((0,0,  self.width, self.height/2,), outline=0, fill=0)
        TS = self.draw.textsize(text, font=self.font)
        TX = (self.width - TS[0])/2
        self.draw.text((TX, 2),text,font=self.font, fill=255)
        self._show()
        
    def progressbar(self, percent):
        #draw a progress bar on top half of screen
        shape_width = self.width * (percent/100)
        padding =2
        top = padding
        bottom = (self.height/2) - padding
        x = padding
        self.draw.rectangle((x, top, self.width-padding, bottom), outline=255, fill=0)
        self.draw.rectangle((x, top, x+shape_width, bottom), outline=255, fill=255)
        self._show()

    def buttons(self, text1, text2, size = 14):
        bfont = ImageFont.truetype("/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
                                           size,
                                           )

        self.draw.rectangle((0, self.height/2,  self.width, self.height,), outline=0, fill=0)
        TS = self.draw.textsize(text1 , bfont)
        TY = (self.height*3/4) - TS[1]/2
        TX = (self.width/4) - TS[0]/2        
        self.draw.text((TX, TY),    text1,  font=bfont, fill=255)
        TS = self.draw.textsize(text2,bfont)
        TY = (self.height *3/4) - TS[1]/2
        TX = (self.width *3/4) - TS[0]/2 
        self.draw.text((TX, TY),    text2,  font=bfont, fill=255)
        self._show()
        
    def loadimage(self, imagefile):
        #open, convert and display an image
        self._image = Image.open(imagefile).resize((self.disp.width,
                                                   self.disp.height),
                                             Image.ANTIALIAS).convert('1')
        self._show()

    def _show(self):
        # Display image.
        self.disp.image(self._image)
        self.disp.display()

        
