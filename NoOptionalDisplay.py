# Optional Local element display object boiler plate
# W.K.Todd 2021
#use this file if no display is fitted
#rename this file NoOptional.py display and replace this file with driver for local display version
#using this as a boiler plate
# e.g rename file OLEDDisplay.py to OptionalDisplay.py if using Adafruit_SSD1306 compatible display




#from PIL import Image
#from PIL import ImageDraw
#from PIL import ImageFont

class OLED(object):

    def __init__(self):
        
       pass
        
    def __del__(self):
        self.clear()

    def __repr__(self):
        return 'Optional display object winder'

    def clear(self):
        # Clear display
        pass
        


    def write(self, text, size = 18):
        print(text)
        
        
    def progressbar(self, percent):
        #draw a progress bar on top half of screen
        pass

    def buttons(self, text1, text2, size = 14):
        print(text1, text2)
        
        
    def loadimage(self, imagefile):
        #open, convert and display an image
        print(imagefile)
        pass

    def _show(self):
        # Display image.
        pass
        
