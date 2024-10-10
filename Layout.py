from Text import Text
from Tag import Tag
import tkinter.font

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

        # stores fonts
        self.fonts = {}

        for tok in tokens:
            self.token(tok)

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

    def token(self, tok):
        # changes spacing based on inputs
        if isinstance(tok, Text):
            for word in tok.text.split():
                self.word(word)

                if word == "\n":
                    self.cursor_y += self.VSTEP  # Increment y by more than VSTEP for paragraph breaks
                    self.cursor_x = self.HSTEP
                    continue

        elif tok.tag == "i":
            self.style = "italic"
        elif tok.tag == "/i":
            self.style = "roman"
        elif tok.tag == "sup":
            self.size /= 2
        elif tok.tag == "/sup":
            self.size *= 2
        elif tok.tag == "abbr":
            self.size -= 4
        elif tok.tag == "/abbr":
            self.size += 4
        elif tok.tag == "b":
            self.weight = "bold"
        elif tok.tag == "/b":
            self.weight = "normal"
        elif tok.tag == "small":
            self.size -= 2
        elif tok.tag == "/small":
            self.size += 2
        elif tok.tag == "big":
            self.size += 4
        elif tok.tag == "/big":
            self.size -= 4
        elif tok.tag == "br":
            self.flush()
        elif tok.tag == "/p":
            self.flush()
            self.cursor_y += self.VSTEP
        elif tok.tag == 'h1 class="title"':
            self.flush()
            self.centered = True
        elif tok.tag == "/h1":
            self.flush()
            self.centered = False
        elif tok.tag == "center":
            self.flush()
            self.centered = True
        elif tok.tag == "/center":
            self.flush()
            self.centered = False