import customtkinter
import tkinter
import tkinter.font
from utils.checkEntity import checkEntity
from HTMl_Tags import Element, Text
from DocumentLayout import DocumentLayout
from HTMLParser import HTMLParser
from CSSParser import CSSParser
from utils.style import style

import globals
CSS_SHEET = CSSParser(open("browser.css").read()).parse() # read and open CSS files 

# ranks each rule by priority
def cascade_priority(rule) -> int:
    selector, body = rule
    return selector.priority

# converts a tree into a list nodes
def treeToList(tree, list) -> list:
    list.append(tree)

    for child in tree.children:
        treeToList(child, list)

    return list

# needs alternate text alignment
def paint_tree(layout_object, display_list) -> None:
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

        self.canvas = tkinter.Canvas(window, bg="white")

        self.canvas.pack(fill="both", expand=True)
        
        window.update_idletasks()
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        globals.update_globals(screen_width, screen_height)

        # scrolling option
        self.scroll = 0
        self.lastY = 0
        self.SCROLL_STEP = 100

        # store urls
        self.url = None

        window.bind("<MouseWheel>", self.scroll_window)
        window.bind("<Up>", self.scroll_window)
        window.bind("<Down>", self.scroll_window)
        window.bind("<Configure>", self.resize)
        window.bind("<Button-1>", self.click)

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

    def click(self, e):
        x, y = e.x, e.y
        y += self.scroll 

        objs = [obj for obj in treeToList(self.document, [])
        if obj.x <= x < obj.x + obj.width
        and obj.y <= y < obj.y + obj.height]

        if not objs: return
        elt = objs[-1].node

        while elt:
            if isinstance(elt, Text):
                pass
            elif elt.tag == "a" and "href" in elt.attributes:
                self.scroll = 0 # reset scroll
                url = self.url.resolve(elt.attributes["href"])
                return self.load(url)

            elt = elt.parent

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
        self.url = url

        self.nodes = HTMLParser(body).parse(self.tag)   

        rules = CSS_SHEET.copy()

        links = [node.attributes["href"]
                for node in treeToList(self.nodes, [])
                if isinstance(node, Element)
                and node.tag == "link"
                and node.attributes.get("rel") == "stylesheet"
                and "href" in node.attributes
            ]
    
        for link in links:
            stylesheetURL = url.resolve(link)

            try:
                body, _ = stylesheetURL.requests()

            except:
                continue # unexpected errors, do not crash program

            rules.extend(CSSParser(body).parse())

        style(self.nodes, sorted(rules, key=cascade_priority))
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

