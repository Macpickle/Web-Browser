from Text import Text
from Element import Element
import tkinter.font
import globals

# globals
BLOCK_ELEMENTS = [
    "html", "body", "article", "section", "nav", "aside",
    "h1", "h2", "h3", "h4", "h5", "h6", "hgroup", "header",
    "footer", "address", "p", "hr", "pre", "blockquote",
    "ol", "ul", "menu", "li", "dl", "dt", "dd", "figure",
    "figcaption", "main", "div", "table", "form", "fieldset",
    "legend", "details", "summary"
]

# flips state of tags to open/close each
class TagFlipper:
    def __init__(self, value1, value2):
       self.values = [value1, value2]
       self.current_index = 0

    def flip(self):
        current_value = self.values[self.current_index]
        self.current_index = 1 - self.current_index  # Switch index between 0 and 1
        return current_value

class Layout:
    def __init__(self, node, parent, previous) -> None:
        self.node = node
        self.parent = parent
        self.previous = previous
        self.children = []

        #position of layout object
        self.x = None
        self.y = None
        self.width = None
        self.height = None
        self.displayList = []

        # font variance
        self.cursor_x = 0
        self.cursor_y = 0
        self.weight = "normal"
        self.style = "roman"
        self.size = 16
        self.centered = False

        # tags
        self.italics = TagFlipper("italic", "roman")
        self.superscript = TagFlipper(0.5,2)
        self.abbreviate = TagFlipper(4, -4)
        self.bold = TagFlipper("bold", "normal")
        self.small = TagFlipper(2, -2)
        self.big = TagFlipper(4, -4)
        self.center = TagFlipper(True, False)
        self.titleTag = TagFlipper(True, False)
        self.commentTag = TagFlipper(True, False)
        
        # stores fonts
        self.fonts = {}

    # advanced layout
    def layout(self) -> None:
        self.x = self.parent.x
        self.width = self.parent.width

        if self.previous:
            self.y = self.previous.y + self.previous.height
        else:
            self.y = self.parent.y

        mode = self.layout_mode()

        if mode == "block":
            # intermediate
            previous = None
            
            for child in self.node.children:
                next = Layout(child, self, previous)
                self.children.append(next)
                previous = next

        else:
            self.cursor_x = 0
            self.cursor_y = 0
            self.weight = "normal"
            self.style = "roman"
            self.size = 12

            self.line = []
            self.recurse(self.node)
            self.flush()

        for child in self.children:
            child.layout()

        if mode == "block":
            self.height = sum([
                child.height for child in self.children])
        else:
            self.height = self.cursor_y
        
    def layout_mode(self):
        if isinstance(self.node, Text):
            return "inline"
        
        elif any([isinstance(child, Element) and \
                  child.tag in BLOCK_ELEMENTS
                  for child in self.node.children]):
            return "block"
        elif self.node.children:
            return "inline"
        else:
            return "block"

    # gets spacing for each word, depending on size and location
    def word(self, word) -> None:
        font = self.getFonts(self.size, self.weight, self.style)
        w = font.measure(word)

        if self.cursor_x + w > self.width - 2 * globals.HSTEP:
            self.flush()

        self.line.append((self.cursor_x, word, font))
        self.cursor_x += w + font.measure(" ")

    # gets fonts from tkinter
    def getFonts(self, size, weight, style) -> tkinter.font:
        key = (size, weight, style)
    
        if key not in self.fonts:
            font = tkinter.font.Font(size=size, weight=weight,slant=style) # create a font
            label = tkinter.Label(font=font)
            self.fonts[key] = (font, label)

        return self.fonts[key][0]
    
    # lines up text properly
    def flush(self) -> None:
        if not self.line: return
        metrics = [font.metrics() for x, word, font in self.line]

        # place cursor 1.25 times past point for gaps
        max_ascent = max([metric["ascent"] for metric in metrics])
        baseline = self.cursor_y + 1.25 * max_ascent

        # add the new values to the list
        for rel_x, word, font in self.line:
            x = self.x + rel_x
            y = self.y + baseline - font.metrics("ascent")
            self.displayList.append((x, y, word, font))

        self.cursor_x = 0
        self.line = []

        # return the spacing
        max_descent = max([metric["descent"] for metric in metrics])
        self.cursor_y = baseline + 1.25 * max_descent

    def swapTag(self, tag):
        if tag == "i":
            self.style = self.italics.flip()

        elif tag == "sup":
            self.size *= self.superscript.flip()

        elif tag == "abbr":
            self.size += self.abbreviate.flip()

        elif tag == "b":
            self.weight = self.bold.flip()
            
        elif tag == "small":
            self.size += self.small.flip()

        elif tag == "big":
            self.size += self.big.flip()

        elif tag == "center":
            self.centered = self.center.flip()

        elif tag == "br":
            self.flush()
            
        elif tag == "p":
            self.flush()
            self.cursor_y += globals.VSTEP

        elif tag == "h1 class='title" or tag == "h1":
            self.flush()
            self.titleTag.flip()

        elif tag == "<!--" or tag == "-->":
            self.commentTag.flip()

        elif tag == "pre":
            self.flush()
            self.cursor_x = globals.HSTEP
            self.cursor_y += globals.VSTEP
      
    def recurse(self, tree):
        if isinstance(tree, Text):
            for word in tree.text.split():
                self.word(word)

        else:
            self.swapTag(tree.tag)
            for child in tree.children:
                self.recurse(child)

            self.swapTag(tree.tag)

    def paint(self):
        return self.displayList
            