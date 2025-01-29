from HTMl_Tags import Element, Text
from DocumentLayout import DocumentLayout
from HTMLParser import HTMLParser
from CSSParser import CSSParser
from utils.style import style

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
    display_list.extend(layout_object.paint())

    for child in layout_object.children:
        paint_tree(child, display_list)

class Tab:
    def __init__(self, tabHeight) -> None:
        # scrolling option
        self.scroll = 0
        self.lastY = 0
        self.history = []
        self.tabHeight = tabHeight

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

    def click(self, x, y):
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
                return self.load(url)
            elt = elt.parent

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
 
    def load(self, url):
        self.history.append(url)
        body, self.tag = url.requests()
        self.url = url
        self.scroll = 0

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

    def go_back(self):
        if len(self.history) > 1:
            self.history.pop()
            back = self.history.pop()
            self.load(back)
        
# debug for tree structure
def print_tree(node, indent=0):
    print(" " * indent, node)
    for child in node.children:
        print_tree(child, indent + 2)

