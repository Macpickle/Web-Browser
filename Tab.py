from HTMl_Tags import Element, Text
from DocumentLayout import DocumentLayout
from HTMLParser import HTMLParser
from CSSParser import CSSParser
from utils.style import style
import urllib.parse

import globals
CSS_SHEET = CSSParser(open("browser.css").read()).parse() # read and open CSS files 

# ranks each rule by priority
def cascade_priority(rule) -> int:
    selector, _ = rule
    return selector.priority

# converts a tree into a list nodes
def treeToList(tree, list) -> list:
    list.append(tree)

    for child in tree.children:
        treeToList(child, list)

    return list

# needs alternate text alignment
def paint_tree(layout_object, display_list) -> None:
    if layout_object.should_paint():
        display_list.extend(layout_object.paint())

    for child in layout_object.children:
        paint_tree(child, display_list)

class Tab:
    def __init__(self, tabHeight) -> None:
        # scrolling option
        self.scroll = 0
        self.lastY = 0
        self.history = []
        self.historyIndex = 0

        self.historyLinks = []
        self.tabHeight = tabHeight
        self.tabName = ""

        self.nodes = None
        self.focus = None

        # store urls
        self.url = None

    # window manipulation functions
    def scroll_window(self, e):
        if e.delta > 0:
            new_scroll = self.scroll - globals.SCROLLSTEP
        else:
            new_scroll = self.scroll + globals.SCROLLSTEP

        max_scroll = max(0, self.document.height - self.tabHeight)
        self.scroll = min(max_scroll, max(0, new_scroll))

    # submit form function
    def submit_form(self, elt):
        inputs = [node for node in treeToList(elt, [])
                  if isinstance(node, Element)
                  and node.tag == "input"
                  and "name" in node.attributes]
        
        body = ""

        for input in inputs:
            name = input.attributes['name']
            value = input.attributes.get('value', '')
            name = urllib.parse.quote(name)
            value = urllib.parse.quote(value)
            body += f"&{name}={value}"

            url = self.url.resolve(elt.attributes["action"])
            self.load(url, body)

        body = body[1:]

    # deals with clicks on tab
    def click(self, x, y, middle):
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
                url = self.url.resolve(elt.attributes["href"])

                if middle:
                    return url
                else:
                    return self.load(url)
                
            elif elt.tag == "input":
                elt.attributes["value"] = ""
                if self.focus:
                    self.focus.focused = False
                self.focus = elt
                elt.focused = True
                return self.render()
            
            elif elt.tag == "button":
                while elt:
                    if elt.tag == "form" and "action" in elt.attributes:
                        return self.submit_form(elt)
                    elt = elt.parent
                elt = elt.parent

    # draw tab components
    def draw(self, canvas, offset):
        for cmd in self.display_list:
            if cmd.rect.top > self.scroll + self.tabHeight:
                continue
            if cmd.rect.bottom < self.scroll: continue
            try:
                cmd.execute(self.scroll - offset, canvas)
            except  Exception as e:
                if "unknown color name" in str(e):
                    continue
                else:
                    raise

    # go back in history
    def go_back(self):
        if self.historyIndex > 0:
            self.historyIndex -= 1
            self.load(self.history[self.historyIndex])

        else:
            self.load(self.history[self.historyIndex])

    # go forward in history
    def go_forward(self):
        if self.historyIndex < len(self.history) - 1:
            self.historyIndex += 1
            self.load(self.history[self.historyIndex])
    
    # load a new tab
    def load(self, url, payload=""):
        self.history.append(url)
        self.historyLinks.append(url.url)
        self.url = url
        self.scroll = 0

        body, self.tag = url.requests(3, payload)
    
        self.nodes = HTMLParser(body).parse(self.tag)   
        self.rules = CSS_SHEET.copy()
        
        links = [node.attributes["href"]
                for node in treeToList(self.nodes, [])
                if isinstance(node, Element)
                and node.tag == "link"
                and node.attributes.get("rel") == "stylesheet"
                and "href" in node.attributes
            ]
        
        # get title of tab
        title_node = next((node for node in treeToList(self.nodes, [])
                   if isinstance(node, Element) and node.tag == "title" and node.children), None)
        if title_node:
            self.tabName = title_node.children[0].text
            self.tabName = self.tabName[:15] + "..." if len(self.tabName) > 15 else self.tabName

    
        for link in links:
            stylesheetURL = url.resolve(link)

            try:
                body, _ = stylesheetURL.requests(3, payload)

            except:
                continue # unexpected errors, do not crash program

            self.rules.extend(CSSParser(body).parse())

        self.render()

    # keypress function
    def keypress(self, char):
        if self.focus:
            self.focus.attributes["value"] += char
            self.render()

    # render the tab
    def render(self):
        style(self.nodes, sorted(self.rules, key=cascade_priority))
        self.document = DocumentLayout(self.nodes)
        self.document.layout()
        self.display_list = []
        paint_tree(self.document, self.display_list)
        
# debug for tree structure
def print_tree(node, indent=0):
    print(" " * indent, node)
    for child in node.children:
        print_tree(child, indent + 2)

