import customtkinter
import tkinter
from Tab import Tab
from Chrome import Chrome
import globals

class Browser:
    def __init__(self, tags):
        self.tags = tags
        self.tabs = []
        self.active_tab = None

        #window settings
        window = customtkinter.CTk()
        self.textalignTag = tags[0] if tags else ""

        # fullscreen with title bar
        window.geometry("%dx%d" % (0, 0))
        window.after(0, lambda: window.state("zoomed"))

        self.canvas = tkinter.Canvas(window, bg="white")

        self.canvas.pack(fill="both", expand=True)
        
        window.update_idletasks()
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        globals.update_globals(screen_width, screen_height)

        # scrolling option
        self.scroll = 0
        self.lastY = 0
        self.SCROLL_STEP = 100

        # store urls
        self.url = None
        self.chrome = Chrome(self)


        window.bind("<MouseWheel>", self.handle_down)
        window.bind("<Up>", self.handle_down)
        window.bind("<Down>", self.handle_down)
        window.bind("<Configure>", self.resize)
        window.bind("<Button-1>", self.handle_click)
        
    def draw(self):
        self.canvas.delete("all")
        self.active_tab.draw(self.canvas, self.chrome.bottom)

        for command in self.chrome.paint():
            command.execute(0, self.canvas)

    def resize(self, e):
        globals.update_globals(e.width, e.height)
        self.draw()

    def new_tab(self, url):
        new_tab = Tab(globals.SCheight - self.chrome.bottom)
        new_tab.load(url)
        self.active_tab = new_tab
        self.tabs.append(new_tab)
        self.draw()

    def handle_down(self, e):
        self.active_tab.scroll_window(e)
        self.draw()

    def handle_click(self, e):
        if e.y < self.chrome.bottom:
            self.chrome.click(e.x, e.y)
        else:
            tab_y = e.y - self.chrome.bottom
            self.active_tab.click(e.x, tab_y)
        self.draw()