from HTMl_Tags import Element, Text, TextLayout, LineLayout
from inputLayout import InputLayout
from utils.getFonts import getFonts
import Draw
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
            self.newLine()
            self.recurse(self.node)

        for child in self.children:
            child.layout()

        self.height = sum([child.height for child in self.children])

    def layout_mode(self):
        if isinstance(self.node, Text):
            return "inline"
        elif any([isinstance(child, Element) and \
                  child.tag in BLOCK_ELEMENTS
                  for child in self.node.children]):
            return "block"
        elif self.node.children or self.node.tag == "input":
            return "inline"
        else:
            return "block"
        
    # make new line
    def newLine(self):
        self.cursor_x = 0
        lastLine = self.children[-1] if self.children else None
        newLine = LineLayout(self.node, self, lastLine)
        self.children.append(newLine)

    # gets spacing for each word, depending on size and location
    def word(self, node, word) -> None:
        weight = node.style["font-weight"]
        style = node.style["font-style"]
        if style == "normal": style = "roman"
        size = int(float(node.style["font-size"][:-2]) * .75)
        font = getFonts(size, weight, style)
        
        w = font.measure(word)
        # need to fix later, width not reaching end unless this formula \/
        if self.cursor_x + w > self.width: 
            self.newLine()

        line = self.children[-1]
        prevWord = line.children[-1] if line.children else None
        text = TextLayout(node, word, line, prevWord)
        line.children.append(text)
        self.cursor_x += w + font.measure(" ")

    # lines up text properly
    def flush(self) -> None:
        if not self.line: return
        metrics = [font.metrics() for x, word, font, color in self.line]

        # place cursor 1.25 times past point for gaps
        max_ascent = max([metric["ascent"] for metric in metrics])
        baseline = self.cursor_y + 1.25 * max_ascent

        # add the new values to the list
        for rel_x, word, font, color in self.line:
            x = self.x + rel_x
            y = self.y + baseline - font.metrics("ascent")
            self.displayList.append((x, y, word, font, color))

        self.cursor_x = 0
        self.line = []

        # return the spacing
        max_descent = max([metric["descent"] for metric in metrics])
        self.cursor_y = baseline + 1.25 * max_descent

    # create new input layout
    def input(self, node):
        w = globals.INPUT_WIDTH

        if self.cursor_x + w > self.width:
            self.newLine()

        line = self.children[-1]
        prevWord = line.children[-1] if line.children else None
        input = InputLayout(node, line, prevWord)
        line.children.append(input)

        weight = node.style["font-weight"]
        style = node.style["font-style"]
        if style == "normal": style = "roman"
        size = int(float(node.style["font-size"][:-2]) * .75)
        font = getFonts(size, weight, style)

        self.cursor_x += w + font.measure(" ")

    def recurse(self, node):
        if isinstance(node, Text):
            for word in node.text.split():
                self.word(node, word)

        else:
            if node.tag in ["i", "sup", "abbr", "b", "small", "big", "center", "br", "p", "h1", "pre"]:
                self.swapTag(node.tag)

            elif node.tag == "br":
                self.newLine()
            
            elif node.tag == "input" or node.tag == "button":
                self.input(node)
            
            for child in node.children:
                self.recurse(child)

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
            self.newLine()
            
        elif tag == "p":
            self.newLine()
            self.cursor_x += globals.VSTEP

        elif tag == "h1 class='title" or tag == "h1":
            self.newLine()
            self.titleTag.flip()

        elif tag == "<!--" or tag == "-->":
            self.commentTag.flip()

        elif tag == "pre":
            self.newLine()
            self.cursor_x = globals.HSTEP

    # determines if the node should be painted, based on tag
    def should_paint(self):
        return isinstance(self.node, Text) or (self.node.tag != "input" and self.node.tag !=  "button")

    def paint(self):
        commands = []
        backgroundColour = self.node.style.get("background-color", "transparent")

        if backgroundColour != "transparent":
            x2, y2 = self.x + self.width, self.y + self.height
            rect = Draw.DrawRectangle(Draw.Rect(self.x, self.y, x2, y2), backgroundColour)
            commands.append(rect)

        return commands