import customtkinter
import tkinter
import tkinter.font
from checkEntity import checkEntity
from Text import Text
from Tag import Tag
from Layout import Layout
# needs alternate text alignment

class GUI:
    def __init__(self, tags) -> None:
        #window settings
        window = customtkinter.CTk()
        self.textalignTag = tags[0] if tags else ""

        # fullscreen with title bar
        window.geometry("%dx%d" % (0, 0))
        window.after(0, lambda: window.state("zoomed"))

        self.canvas = tkinter.Canvas(window)

        self.canvas.pack(fill="both", expand=True)

        self.SCwidth = window.winfo_screenwidth()
        self.SCheight = window.winfo_screenheight()

        # scrolling option
        self.scroll = 0
        self.lastY = 1
        self.SCROLL_STEP, self.HSTEP, self.VSTEP = 100, 13, 18

        window.bind("<Down>", self.scrolldown)
        window.bind("<Up>", self.scrollup)
        window.bind("<MouseWheel>", self.on_mouse_wheel)

        #resizing window
        window.bind("<Configure>", self.resize)

    # checks if the scroll is is in range of text
    def checkInRange(self, y):
        if not self.scroll < self.lastY - self.SCheight:
            self.scroll = self.lastY - self.SCheight

        if self.scroll < 100:
            self.scroll = 100

    def scrolldown(self, e):
        self.checkInRange(self.lastY)
        self.scroll += self.SCROLL_STEP
        self.draw()

    def scrollup(self, e):
        self.checkInRange(self.lastY)
        self.scroll -= self.SCROLL_STEP
        self.draw()

    def on_mouse_wheel(self, e):
        self.checkInRange(self.lastY)
        self.scroll -= e.delta
        self.draw()

    def draw(self):
        self.canvas.delete("all")

        # adds text to canvas
        for x, y, text, font in self.displayList:
            if y > self.scroll + self.SCheight: continue
            if y + self.VSTEP < self.scroll: continue
            
            self.canvas.create_text(x, y - self.scroll, font=font, text=text, anchor='nw')
            self.lastY = y
 
    def load(self, url):
        body, tag = url.requests()
        self.tokens = self.displayContent(body, tag)
        self.displayList = Layout(self.tokens, self.SCwidth, self.SCheight, self.HSTEP, self.VSTEP).displayList
        self.draw()

    def displayContent(self, body, scheme):
        tag = False
        out = []
        buffer = ""
        putUppercase = False
        
        if scheme == "view-source":
            return body
        
        for item in body:
            match item:
                case "<":
                    tag = True
                    if buffer and not putUppercase:
                        out.append(Text(buffer))
                    if buffer and putUppercase:
                        out.append(Text(buffer.upper()))
                    if buffer == "center":
                        out.append(Tag("br"))

                    buffer = ""

                case ">":
                    tag = False
                    if buffer == "abbr":
                        putUppercase = True
                    elif buffer == "/abbr":
                        putUppercase = False
                    out.append(Tag(buffer))
                    buffer = ""

                case _:
                    buffer += item
                    buffer = checkEntity(buffer)

        if not tag and buffer:
            out.append(Text(buffer))
        return out
    # called when window is resized
    def resize(self, e):
        self.SCwidth = e.width
        self.SCheight = e.height
        self.displayList = Layout(self.tokens, self.SCwidth, self.SCheight, self.HSTEP, self.VSTEP).displayList
        self.draw()

