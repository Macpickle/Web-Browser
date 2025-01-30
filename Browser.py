import customtkinter
import tkinter
from Tab import Tab
from Chrome import Chrome
import globals

class Browser:
    def __init__(self, tags):
        self.tags = tags
        self.tabs = []
        self.links = []
        self.active_tab = None
        self.initialize()

        self.window.bind("<MouseWheel>", self.handle_scroll)
        self.window.bind("<Configure>", lambda e: self.draw())
        self.window.bind("<Button-1>", self.handle_click)
        self.window.bind("<Key>", self.handle_key)
        self.window.bind("<BackSpace>", self.handle_backspace)
        self.window.bind("<Return>", self.handle_enter)
        self.window.bind("<Button-2>", self.handle_middle_click)
        self.chrome = Chrome(self)

        
    def initialize(self):
        self.window = customtkinter.CTk()
        self.window.geometry("%dx%d" % (1000, 1000))                
        self.window.after(0, lambda: self.window.state("zoomed"))
        self.canvas = tkinter.Canvas(self.window, bg="white")
        self.canvas.pack(fill="both", expand=True)
        
        self.window.update_idletasks() 
        screen_width = self.window.winfo_screenwidth() + 400 # bad fix, but it works
        screen_height = self.window.winfo_screenheight()
        globals.update_globals(screen_width, screen_height)

    def new_tab(self, url):
        new_tab = Tab(globals.SCheight - self.chrome.bottom)
        new_tab.load(url)
        self.active_tab = new_tab
        self.tabs.append(new_tab)
        self.draw()

    def draw(self):
        self.canvas.delete("all")
        self.active_tab.draw(self.canvas, self.chrome.bottom)

        for command in self.chrome.paint():
            command.execute(0, self.canvas)

    def handle_scroll(self, e):
        self.active_tab.scroll_window(e)
        self.draw()

    def handle_middle_click(self, e):
        tab_y = e.y - self.chrome.bottom
        res = self.active_tab.click(e.x, tab_y, True)
        
        if res:
            self.new_tab(res)
        
    def handle_click(self, e):
        if e.y < self.chrome.bottom:
            self.chrome.click(e.x, e.y)
        else:
            tab_y = e.y - self.chrome.bottom
            self.active_tab.click(e.x, tab_y, False)
        self.draw()

    def handle_key(self, e):
        self.chrome.keypress(e.char)
        self.draw()

    def handle_backspace(self, e):
        self.chrome.keypress("BACKSPACE")
        self.draw()

    def handle_key(self, e):
        if len(e.char) == 0: return
        if not (0x20 <= ord(e.char) < 0x7f): return
        self.chrome.keypress(e.char)
        self.draw()

    def handle_enter(self, e):
        self.chrome.enter()
        self.draw()