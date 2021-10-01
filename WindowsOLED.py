#Windows subsitute OLED display class
#displays a label image for testing 

from tkinter import  Tk, Label
from PIL import Image, ImageTk
#from tkinter import filedialog, messagebox
from tkinter.constants import YES, BOTH

class Wdisp(object):
    i=None
    width = 128
    height =64
    _image = None

    def __init__(self):
        self.master = Tk()
        self.master.title("OLED Display")
        self._image = Image.new('1', (self.width, self.height))
        self._image = Image.open('ADT_LOGO.png').resize((self.width,
                                                   self.height),
                                             Image.ANTIALIAS).convert('1')
        self.i = ImageTk.BitmapImage(self._image)
        self.L= Label(self.master, text="Wdisp", )#  image=self.i)
        self.L.pack(expand=YES, fill=BOTH)

        
    def __repr__(self):
        return 'Substitute OLED for windows'
    def __del__(self):
        pass
    
    def image(self, newimage):
        self._image = newimage

    def display(self):
        #display the image
        self.i = ImageTk.BitmapImage(self._image)
        self.L.config(text = "display" ) #image=self._image) 
        
        
    def begin(self):
        pass

    def clear(self):
        self._image = Image.new('1', (self.width, self.height))
        self.display()
    

 
