from utils.getFonts import getFonts
import Draw
import globals
from URL import URL

class Chrome:
    def __init__(self, browser):
        self.browser = browser

        self.font = getFonts(20, "normal", "roman")
        self.fontHeight = self.font.metrics("linespace")

        self.topPadding = 5
        self.tabbarTop = 0
        self.tabbarBottom = self.fontHeight + 2*self.topPadding

        plusWidth = self.font.measure("+") + 2*self.topPadding
        self.newTabRectangle = Draw.Rect(
           self.topPadding, self.topPadding,
           self.topPadding + plusWidth,
           self.topPadding + self.fontHeight
        )

        self.bottom = self.tabbarBottom

    def click(self, x, y):
        if self.newTabRectangle.contains_point(x, y):
            self.browser.new_tab(URL("https://browser.engineering/"))
        else:
            for i, tab in enumerate(self.browser.tabs):
                if self.tabRectangle(i).contains_point(x, y):
                    self.browser.active_tab = tab
                    break

    def tabRectangle(self, index):
        tabStart = self.newTabRectangle.right + self.topPadding
        tabWidth = self.font.measure("Tab X") + 2*self.topPadding
        return Draw.Rect(
            tabStart + tabWidth * index, self.tabbarTop,
            tabStart + tabWidth * (index + 1), self.tabbarBottom
        )

    def paint(self):
        commands = []

        commands.append(Draw.DrawRectangle(Draw.Rect(0, 0, globals.SCwidth, self.bottom), "white"))
        commands.append(Draw.DrawLine(0, self.bottom, globals.SCwidth, self.bottom, "black", 1))

        commands.append(Draw.DrawOutline(self.newTabRectangle, "black", 1))
        commands.append(Draw.DrawText(
            self.newTabRectangle.left + self.topPadding,
            self.newTabRectangle.top,
            "+", self.font, "black")
        )

        for i, tab in enumerate(self.browser.tabs):
            bounds = self.tabRectangle(i)

            commands.append(Draw.DrawLine(bounds.left, 0, bounds.left, bounds.bottom, "black", 1))
            commands.append(Draw.DrawLine(bounds.right, 0, bounds.right, bounds.bottom, "black", 1))
            commands.append(Draw.DrawText(bounds.left + self.topPadding, bounds.top + self.topPadding, "Tab {}".format(i), self.font, "black"))

            if tab == self.browser.active_tab:
                commands.append(Draw.DrawLine(0, bounds.bottom, bounds.left, bounds.bottom, "black", 1))
                commands.append(Draw.DrawLine(bounds.right, bounds.bottom, globals.SCwidth, bounds.bottom, "black", 1))

        return commands




