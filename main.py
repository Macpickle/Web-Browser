<<<<<<< HEAD
import customtkinter
import tkinter
import tkinter.font

from URL import URL

class Browser:
    def __init__(self, window, url):
        self.canvas = tkinter.Canvas(
            window,
            width=SCwidth,
            height=SCheight
        )
        self.canvas.pack(fill="both", expand=True)
        self.displayList = []
        self.scroll = 0
        self.lastY = 0
        window.bind("<Down>", self.scrolldown)
        window.bind("<Up>", self.scrollup)
        # add mouse event scroll
        window.bind("<MouseWheel>", self.on_mouse_wheel)

        window.bind("<Configure>", self.resize)

        self.load(url)

    def load(self, url):
        try:
            body = url.request()
        except Exception as e:
            print(f"Error loading URL: {e}")
            body = ""
        
        self.tokens = self.display(body)
        self.displayList = Layout(self.tokens).displayList
        self.showText()

    # display items
    def showText(self):
        self.canvas.delete("all")
        for x, y, word, font in self.displayList:
            self.lastY = y
            if y > self.scroll + SCheight:
                continue
            if y + VSTEP < self.scroll:
                continue
            self.canvas.create_text(x, y - self.scroll, text=word, font=font, anchor='nw')

    def display(self, body):
        # show the response of the url, formatted to only keep text
        tag = False
        out = []
        buffer = ""

        for item in body:
            match item:
                case "<":
                    tag = True
                    if buffer: out.append(Text(buffer))
                    buffer = ""

                case ">":
                    tag = False
                    out.append(Tag(buffer))
                    buffer = ""

                case _:
                    buffer += item

        if not tag and buffer:
            out.append(Text(buffer))
        return out

    def scrolldown(self, e):
        self.scroll += SCROLL_STEP
        self.showText()

    def scrollup(self, e):
        self.scroll -= SCROLL_STEP
        self.showText()

    def on_mouse_wheel(self, e):
        if not self.scroll < self.lastY - SCheight:
            self.scroll = self.lastY - SCheight

        if self.scroll < 100:
            self.scroll = 100

        if e.delta > 0:
            self.scroll -= SCROLL_STEP
        else:
            self.scroll += SCROLL_STEP
        self.showText()

    def resize(self, e):
        global SCwidth, SCheight
        SCwidth = e.width
        SCheight = e.height
        self.displayList = Layout(self.tokens).displayList
        self.showText()
    
class Text:
    def __init__(self,text):
        self.text = text

class Tag:
    def __init__(self, tag):
        self.tag = tag

class Layout:
    def __init__(self, tokens):
        self.displayList = []
        self.line = []

        self.cursor_x = HSTEP
        self.cursor_y = VSTEP
        self.weight = "normal"
        self.style = "roman"
        self.size = 16

        for tok in tokens:
            self.token(tok)

        self.flush()

    def flush(self):
        if not self.line: return      
        metrics = [font.metrics() for x, word, font in self.line]
        max_ascent = max([metric["ascent"] for metric in metrics])
        baseline = self.cursor_y + 1.25 * max_ascent

        for x, word, font in self.line:
            y = baseline - font.metrics("ascent")
            self.displayList.append((x, y, word, font))

        max_descent = max([metric["descent"] for metric in metrics])
        self.cursor_y = baseline + 1.25 * max_descent

        self.cursor_x = HSTEP
        self.line = []

    def word(self, word):
        font = getFonts(self.size, self.weight, self.style)
        w = font.measure(word)

        if self.cursor_x + w > SCwidth - HSTEP:
            self.flush()

        self.line.append((self.cursor_x, word, font))
        self.cursor_x += w + font.measure(" ")


    def token(self, tok):
        if isinstance(tok, Text):
            for word in tok.text.split():
                self.word(word)

                if word == "\n":
                    self.cursor_y += VSTEP  # Increment y by more than VSTEP for paragraph breaks
                    self.cursor_x = HSTEP
                    continue

        elif tok.tag == "i":
            self.style = "italic"
        elif tok.tag == "/i":
            self.style = "roman"
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
            self.cursor_y += VSTEP

def getFonts(size, weight, style):
    key = (size, weight, style)

    if key not in fonts:
        font = tkinter.font.Font(size=size, weight=weight,slant=style)
        label = tkinter.Label(font=font)
        fonts[key] = (font, label)
    return fonts[key][0]


if __name__ == "__main__":
    import sys
    window = customtkinter.CTk()

    HSTEP, VSTEP, SCROLL_STEP = 13, 18, 100
    fonts = {}

    # fullscreen with title bar
    window.geometry("%dx%d" % (0, 0))
    window.after(0, lambda: window.state("zoomed"))

    # get screen width and height
    global SCwidth, SCheight
    SCwidth = window.winfo_screenwidth()
    SCheight = window.winfo_screenheight()
=======
from URL import URL
from GUI import GUI
import tkinter;

if __name__ == "__main__":
    import sys

    HSTEP, VSTEP, SCROLL_STEP = 13, 18, 100
    tags = ""
    if len(sys.argv) >= 2:
        tags = sys.argv[2:]
    window = GUI(tags)
>>>>>>> master

    if len(sys.argv) > 1:
        url = URL(sys.argv[1])
    else:
        url = URL("about:blank")
<<<<<<< HEAD
    browser = Browser(window, url)
    window.mainloop()
=======

    window.load(url)
    tkinter.mainloop()
>>>>>>> master
