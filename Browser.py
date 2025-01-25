import customtkinter
import tkinter
import tkinter.font
from checkEntity import checkEntity
from HTMl_Tags import Element
from DocumentLayout import DocumentLayout
from HTMLParser import HTMLParser
from CSSParser import CSSParser

import globals
CSS_SHEET = CSSParser(open("browser.css").read()).parse() # read and open CSS files 

INHERITED_PROPERTIES = {
    "font-size": "16px",
    "font-style": "normal",
    "font-weight": "normal",
    "color": "black",
    "font-family": "Arial, sans-serif",
}

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

# css styling of node
def style(node, rules):
    node.style = {}

    # apply styles of inherited style
    for prop, default_value in INHERITED_PROPERTIES.items():
        if node.parent:
            node.style[prop] = node.parent.style[prop]
        else:
            node.style[prop] = default_value

    # apply properties and values to node styling
    for selector, body in rules:
        if not selector.matches(node): continue
        for prop, val in body.items():
            node.style[prop] = val

    # checks if node is an element, and if its in style attribute
    if isinstance(node, Element) and "style" in node.attributes:
        pairs = CSSParser(node.attributes["style"]).body()
        for prop, val in pairs.items():
            node.style[prop] = val

    # deal with special cases (eg. % size from parent)
    if node.style["font-size"].endswith("%"):
        if node.parent:
            parent_font_size = node.parent.style["font-size"]
        else:
            parent_font_size = INHERITED_PROPERTIES["font-size"]
        node_pct = float(node.style["font-size"][:-1]) / 100
        parent_px = float(parent_font_size[:-2])
        node.style["font-size"] = str(node_pct * parent_px) + "px"

    # Ensure <code> elements use a monospaced font
    if isinstance(node, Element) and node.tag == "code":
        node.style["font-family"] = "Courier, monospace"
            
    for child in node.children:
        style(child, rules)

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
        screen_width = window.winfo_screenwidth() * 1.25
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

