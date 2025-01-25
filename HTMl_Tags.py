from utils.getFonts import getFonts
import Draw

# classes for HTML tags
class Text:
    def __init__(self, text, parent):
        self.text = text
        self.children = []
        self.parent = parent

    def __repr__(self):
        return repr(self.text)
    
class Element:
    def __init__(self, tag, parent, attributes):
        self.tag = tag
        self.attributes = attributes
        self.children = []
        self.parent = parent

    def __repr__(self):
        return repr(self.tag)
    
#Selectors for CSS parsing
class TagSelector:
    def __init__(self, tag):
        self.tag = tag
        self.priority = 1

    def matches(self, node) -> bool:
        return isinstance(node, Element) and node.tag == self.tag
    
class DescendantSelector:
    def __init__(self, ancestor, descendant):
        self.ancestor = ancestor
        self.descendant = descendant
        self.priority = ancestor.priority + descendant.priority
    
    def matches(self, node) -> bool:
        # check if the descendant matches
        if not self.descendant.matches(node): return False

        # loop through ancestors, checking for any matches
        while node.parent:
            if self.ancestor.matches(node.parent): return True
            node = node.parent 

        # no matches found
        return False
    
# layout for each line in a page
class LineLayout:
    def __init__(self, node, parent, previous):
        self.node = node
        self.parent = parent
        self.previous = previous
        self.children = []

    def layout(self):
        self.width = self.parent.width
        self.x = self.parent.x

        if self.previous:
            self.y = self.previous.y + self.previous.height
        else:
            self.y = self.parent.y

        for word in self.children:
            word.layout()

        if not self.children:
            self.height = 0
            return

        max_ascent = max([word.font.metrics("ascent") for word in self.children])
        baseline = self.y + 1.25 * max_ascent
        for word in self.children:
            word.y = baseline - word.font.metrics("ascent")
        max_descent = max([word.font.metrics("descent") for word in self.children])
        self.height = 1.25 * (max_ascent + max_descent)

    def paint(self):
        return []

# layout for each text in a page
class TextLayout:
    def __init__(self, node, word, parent, previous):
        self.node = node
        self.word = word
        self.children = []
        self.parent = parent
        self.previous = previous

    def layout(self):
        weight = self.node.style["font-weight"]
        style = self.node.style["font-style"]
        if style == "normal": style = "roman"
        size = int(float(self.node.style["font-size"][:-2]) * .75)
        self.font = getFonts(size, weight, style)

        self.width = self.font.measure(self.word)

        if self.previous:
            space = self.previous.font.measure(" ")
            self.x = self.previous.x + space + self.previous.width
        else:
            self.x = self.parent.x

        self.height = self.font.metrics("linespace")

    def paint(self):
        color = self.node.style["color"]
        return [Draw.DrawText(self.x, self.y, self.word, self.font, color)]