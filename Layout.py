from Text import Text
from Element import Element
import tkinter.font

class TagFlipper:
    def __init__(self, value1, value2):
       self.values = [value1, value2]
       self.current_index = 0

    def flip(self):
        current_value = self.values[self.current_index]
        self.current_index = 1 - self.current_index  # Switch index between 0 and 1
        return current_value

class Layout:
    def __init__(self, tokens, SCwidth, SCheight, HSTEP, VSTEP) -> None:
        self.displayList = []
        self.line = []
        
        # spacing
        self.HSTEP = HSTEP
        self.VSTEP = VSTEP

        # window sizes
        self.SCwidth = SCwidth
        self.SCheight = SCheight

        # font variance
        self.cursor_x = self.HSTEP
        self.cursor_y = self.VSTEP
        self.weight = "normal"
        self.style = "roman"
        self.size = 16
        self.centered = False

        #tags
        self.italics = TagFlipper("italic", "roman")
        self.superscript = TagFlipper(0.5,2)
        self.abbreviate = TagFlipper(4, -4)
        self.bold = TagFlipper("bold", "normal")
        self.small = TagFlipper(2, -2)
        self.big = TagFlipper(4, -4)
        self.center = TagFlipper(True, False)
        self.titleTag = TagFlipper(True, False)
        

        # stores fonts
        self.fonts = {}

        # parse the tree
        self.tree(tokens)

        self.flush()

    # gets spacing for each word, depending on size and location
    def word(self, word) -> None:
        font = self.getFonts(self.size, self.weight, self.style)
        w = font.measure(word)

        if self.cursor_x + w > self.SCwidth - self.HSTEP:
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
        for x, word, font in self.line:
            y = baseline - font.metrics("ascent")
            self.displayList.append((x, y, word, font))

        # return the spacing
        max_descent = max([metric["descent"] for metric in metrics])
        self.cursor_y = baseline + 1.25 * max_descent

        self.cursor_x = self.HSTEP
        self.line = []

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
            self.cursor_y += self.VSTEP

        elif tag == "h1 class='title" or tag == "h1":
            self.flush()
            self.titleTag.flip()
      
    def tree(self, tree):
        if isinstance(tree, Text):
            for word in tree.text.split():
                self.word(word)

        else:
            self.swapTag(tree.tag)
            for child in tree.children:
                self.tree(child)
            self.swapTag(tree.tag)