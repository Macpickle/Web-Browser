import customtkinter
import tkinter
import tkinter.font
from checkEntity import checkEntity
from Text import Text
from Element import Element
from Layout import Layout
from HTMLParser import HTMLParser

from globals import *
# needs alternate text alignment

class GUI:
    def __init__(self, tags) -> None:
        #window settings
        window = customtkinter.CTk()
        self.textalignTag = tags[0] if tags else ""

        # fullscreen with title bar
        window.geometry("%dx%d" % (0, 0))
        window.after(0, lambda: window.state("zoomed"))

        self.canvas = tkinter.Canvas(window)

        self.canvas.pack(fill="both", expand=True)

        update_globals(window.winfo_screenwidth(), window.winfo_screenheight())

        # scrolling option
        self.scroll = 0
        self.lastY = 1
        self.SCROLL_STEP = 100

        window.bind("<Down>", self.scrolldown)
        window.bind("<Up>", self.scrollup)
        window.bind("<MouseWheel>", self.on_mouse_wheel)

        #resizing window
        window.bind("<Configure>", self.resize)

    # checks if the scroll is is in range of text
    def checkInRange(self, y):
        if not self.scroll < self.lastY - SCheight:
            self.scroll = self.lastY - SCheight

        if self.scroll < 100:
            self.scroll = 100

    def scrolldown(self, e):
        self.checkInRange(self.lastY)
        self.scroll += self.SCROLL_STEP
        self.draw()

    def scrollup(self, e):
        self.checkInRange(self.lastY)
        self.scroll -= self.SCROLL_STEP
        self.draw()

    def on_mouse_wheel(self, e):
        self.checkInRange(self.lastY)
        self.scroll -= e.delta
        self.draw()

    def draw(self):
        self.canvas.delete("all")

        # adds text to canvas
        for x, y, text, font in self.displayList:
            if y > self.scroll + SCheight: continue
            if y + VSTEP < self.scroll: continue
            
            self.canvas.create_text(x, y - self.scroll, font=font, text=text, anchor='nw')
            self.lastY = y
 
    def load(self, url):
        body, self.tag = url.requests()
        self.nodes = HTMLParser(body).parse(self.tag)    
        #print_tree(self.nodes, 0)        
        self.displayList = Layout(self.nodes, None, None).displayList
        self.draw()

    # called when window is resized
    def resize(self, e):
        update_globals(e.width, e.height)
        self.displayList = Layout(self.nodes, None, None).displayList
        self.draw()
        
        


def print_tree(node, indent=0):
    print(" " * indent, node)
    for child in node.children:
        print_tree(child, indent + 2)