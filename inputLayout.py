import Draw
from HTMl_Tags import Text
from utils.getFonts import getFonts
import globals

class InputLayout:
    def __init__(self, node, parent, previous):
        self.node = node
        self.parent = parent
        self.previous = previous
        self.children = []
        self.width = globals.INPUT_WIDTH

    def layout(self):
        weight = self.node.style["font-weight"]
        style = self.node.style["font-style"]
        if style == "normal": style = "roman"
        size = int(float(self.node.style["font-size"][:-2]) * .75)
        self.font = getFonts(size, weight, style)

        if self.previous:
            space = self.previous.font.measure(" ")
            self.x = self.previous.x + space + self.previous.width
        else:
            self.x = self.parent.x

        self.height = self.font.metrics("linespace")

    def should_paint(self):
        return True

    def paint(self):
        commands = []
        
        backgroundColour = self.node.style.get("background-color", "transparent") 

        if backgroundColour != "transparent":
            rect = Draw.DrawRectangle(
                Draw.Rect(self.x, self.y, self.x + self.width, self.y + self.height),
                backgroundColour
            )
            commands.append(rect)

        if self.node.tag == "input":
            text = self.node.attributes.get("value", "")

        elif self.node.tag == "button":
            if len(self.node.children) == 1 and \
               isinstance(self.node.children[0], Text):
                text = self.node.children[0].text
            else:
                print("Ignoring HTML Content")
                text = ""

        if self.node.focused:
            cx = self.x + self.font.measure(text)
            commands.append(Draw.DrawLine(cx, self.y, cx, self.y + self.height, "black", 1))

        color = self.node.style["color"]
        commands.append(Draw.DrawText(self.x, self.y, text, self.font, color))

        return commands