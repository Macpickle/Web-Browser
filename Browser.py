import customtkinter
import tkinter
import tkinter.font
from checkEntity import checkEntity
from Text import Text
from Element import Element
from DocumentLayout import DocumentLayout
from Layout import Layout
from HTMLParser import HTMLParser

import globals

# needs alternate text alignment
def paint_tree(layout_object, display_list):
    display_list.extend(layout_object.paint())

    for child in layout_object.children:
        paint_tree(child, display_list)

class Browser:
    def __init__(self, tags) -> None:
        #window settings
        window = customtkinter.CTk()
        self.textalignTag = tags[0] if tags else ""

        # fullscreen with title bar
        window.geometry("%dx%d" % (0, 0))
        window.after(0, lambda: window.state("zoomed"))

        self.canvas = tkinter.Canvas(window)

        self.canvas.pack(fill="both", expand=True)
        
        window.update_idletasks()
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        globals.update_globals(screen_width, screen_height)

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
        if not self.scroll < self.lastY - globals.SCheight:
            self.scroll = self.lastY - globals.SCheight

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
        for x, y, text, font in self.display_list:
            if y > self.scroll + globals.SCheight: continue
            if y + globals.VSTEP < self.scroll: continue
            
            self.canvas.create_text(x, y - self.scroll, font=font, text=text, anchor='nw')
            self.lastY = y
 
    def load(self, url):
        body, self.tag = url.requests()
        self.nodes = HTMLParser(body).parse(self.tag)    
        self.document = DocumentLayout(self.nodes)
        self.document.layout()
        self.display_list = []
        paint_tree(self.document, self.display_list)
        self.draw()

    # called when window is resized
    def resize(self, e):
        globals.update_globals(e.width, e.height)
        self.draw()
        
def print_tree(node, indent=0):
    print(" " * indent, node)
    for child in node.children:
        print_tree(child, indent + 2)