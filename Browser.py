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

        window.bind("<MouseWheel>", self.scroll_window)
        window.bind("<Up>", self.scroll_window)
        window.bind("<Down>", self.scroll_window)
        window.bind("<Configure>", self.resize)

    # window manipulation functions
    def scroll_window(self, e):
        if e.keysym == "Up":
            new_scroll = self.scroll - self.SCROLL_STEP
        elif e.keysym == "Down":
            new_scroll = self.scroll + self.SCROLL_STEP
        else:
            new_scroll = self.scroll - e.delta / 120 * self.SCROLL_STEP
            max_scroll = max(command.y1 for command in self.display_list) - globals.SCheight
            self.scroll = max(0, min(new_scroll, max_scroll))
            self.draw()

    def resize(self, e):
        globals.update_globals(e.width, e.height)
        self.draw()

    def draw(self):
        self.canvas.delete("all")

        #places object on canvas
        for command in self.display_list:
            if command.x1 > self.scroll + globals.SCheight: continue
            if command.y1 < self.scroll: continue
            command.execute(self.scroll, self.canvas)
 
    def load(self, url):
        body, self.tag = url.requests()
        self.nodes = HTMLParser(body).parse(self.tag)    
        self.document = DocumentLayout(self.nodes)
        self.document.layout()
        self.display_list = []
        paint_tree(self.document, self.display_list)
        self.draw()
        
# debug for tree structure
def print_tree(node, indent=0):
    print(" " * indent, node)
    for child in node.children:
        print_tree(child, indent + 2)