from utils.getFonts import getFonts
import Draw
import globals
from URL import URL

# colour theming
navbarBackground = "#131717"
navbarBackgroundActive = "#303030"
navbarOutline = "#b5b5b5"
navbarText = "#b5b5b5"

class Chrome:
    def __init__(self, browser):
        self.browser = browser

        self.font = getFonts(20, "normal", "roman")
        self.fontHeight = self.font.metrics("linespace")

        self.focus = None
        self.address_bar_text = ""
        self.topPadding = 5
        self.tabbarTop = 0
        self.tabbarBottom = self.fontHeight + 2*self.topPadding

        plusWidth = self.font.measure("+") + 2*self.topPadding
        self.newTabRectangle = Draw.Rect(
           self.topPadding, 
           self.topPadding,
           self.topPadding + plusWidth,
           self.topPadding + self.fontHeight
        )

        self.urlTop = self.tabbarBottom
        self.urlBottom = self.urlTop + self.fontHeight + 2*self.topPadding
        self.bottom = self.urlBottom

        backWidth = self.font.measure("<") + 2 * self.topPadding
        self.backRectangle = Draw.Rect(
            self.topPadding, 
            self.urlTop + self.topPadding,
            self.topPadding + backWidth, 
            self.urlBottom - self.topPadding
        )

        forwardWidth = self.font.measure(">") + 2 * self.topPadding
        self.forwardRectangle = Draw.Rect(
            self.backRectangle.right + self.topPadding,
            self.urlTop + self.topPadding,
            self.backRectangle.right + self.topPadding + forwardWidth,
            self.urlBottom - self.topPadding
        )

        self.address_bar = Draw.Rect(
            self.backRectangle.right + self.topPadding + forwardWidth + self.topPadding,
            self.urlTop + self.topPadding,
            globals.SCwidth - self.topPadding,
            self.urlBottom - self.topPadding
        )

        self.bottom = self.urlBottom
    def tabRectangle(self, index):
        tabStart = self.newTabRectangle.right + self.topPadding
        tabWidth = self.font.measure("XXXXXXXXXXXXXXX") + 2*self.topPadding
        return Draw.Rect(
            tabStart + tabWidth * index, self.tabbarTop,
            tabStart + tabWidth * (index + 1), self.tabbarBottom
        )

    def click(self, x, y):
        self.focus = None
        
        if self.newTabRectangle.contains_point(x, y):
            self.browser.new_tab(URL("https://browser.engineering/"))
        
        elif self.backRectangle.contains_point(x, y):
            self.browser.active_tab.go_back()

        elif self.forwardRectangle.contains_point(x, y):
            self.browser.active_tab.go_forward()
        
        elif self.address_bar.contains_point(x, y):
            self.focus = "address bar"
            self.address_bar_text = ""
        
        else:
            for i, tab in enumerate(self.browser.tabs):
                if self.tabRectangle(i).contains_point(x, y):
                    self.browser.active_tab = tab
                    break

    def keypress(self, char):
        if self.focus == "address bar":
            if char == "BACKSPACE":
                self.address_bar_text = self.address_bar_text[:-1]
            else:
                self.address_bar_text += char
            return True
        return False

    def enter(self):
        if self.focus == "address bar":
            self.browser.active_tab.load(URL("https://google.com/search?q={}".format(self.address_bar_text)))
            self.focus = None

    def blur(self):
        self.focus = None
                
    def paint(self):
        commands = []

        # draw main navbar
        commands.append(Draw.DrawRectangle(Draw.Rect(0, 0, globals.SCwidth, self.urlBottom), navbarBackground))
        # change colour behind searchbar
        commands.append(Draw.DrawRectangle(Draw.Rect(0, self.urlTop, globals.SCwidth, self.urlBottom), navbarBackgroundActive))
        commands.append(Draw.DrawLine(0, self.urlBottom, globals.SCwidth, self.urlBottom, navbarOutline, 1))

        # draw new tab button
        commands.append(Draw.DrawRectangle(self.newTabRectangle, navbarBackground))
        commands.append(Draw.DrawText(
                self.newTabRectangle.left + self.topPadding, 
                self.newTabRectangle.top, 
                "+", 
                self.font, 
                navbarText
            )
        )

        # draw tabs in browsertabs
        for x, tab in enumerate(self.browser.tabs):
            bounds = self.tabRectangle(x)

            commands.append(Draw.DrawRectangle(bounds, navbarBackgroundActive if tab == self.browser.active_tab else navbarBackground))
            commands.append(Draw.DrawLine(
                bounds.left,
                0,
                bounds.left,
                bounds.bottom,
                navbarOutline,
                1,
            ))

            commands.append(Draw.DrawLine(
                bounds.right,
                0,
                bounds.right,
                bounds.bottom,
                navbarOutline,
                1,
            ))

            commands.append(Draw.DrawText(
                bounds.left + self.topPadding,
                bounds.top + self.topPadding,
                tab.tabName,
                self.font,
                navbarText
            ))

            if tab == self.browser.active_tab:
                commands.append(Draw.DrawLine(
                    0,
                    bounds.bottom,
                    bounds.left,
                    bounds.bottom,
                    navbarOutline,
                    1
                ))

                commands.append(Draw.DrawLine(
                    bounds.right,
                    bounds.bottom,
                    globals.SCwidth,
                    bounds.bottom,
                    navbarOutline,
                    1
                ))

        # draw back button
        commands.append(Draw.DrawOutline(
            self.backRectangle,
            navbarOutline,
            1
        ))

        commands.append(Draw.DrawText(
            self.backRectangle.left + self.topPadding,
            self.backRectangle.top,
            "<",
            self.font,
            navbarText
        ))

        # draw forward button
        commands.append(Draw.DrawOutline(
            self.forwardRectangle,
            navbarOutline,
            1
        ))

        commands.append(Draw.DrawText(
            self.forwardRectangle.left + self.topPadding,
            self.forwardRectangle.top,
            ">",
            self.font,
            navbarText
        ))

        commands.append(Draw.DrawOutline(self.address_bar, navbarOutline, 1))
        if self.focus == "address bar":
            commands.append(Draw.DrawText(
                self.address_bar.left + self.topPadding,
                self.address_bar.top,
                self.address_bar_text,
                self.font,
                navbarText
            ))

            w = self.font.measure(self.address_bar_text)

            commands.append(Draw.DrawLine(
                self.address_bar.left + self.topPadding + w,
                self.address_bar.top,
                self.address_bar.left + self.topPadding + w,
                self.address_bar.bottom,
                navbarText,
                1
            ))

        else:
            url = str(self.browser.active_tab.url)
            commands.append(Draw.DrawText(
                self.address_bar.left + self.topPadding,
                self.address_bar.top,
                url,
                self.font,
                navbarText
            ))

        return commands



