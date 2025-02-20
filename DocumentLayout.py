from Layout import Layout
import globals

class DocumentLayout:
    def __init__(self, node):
        self.node = node
        self.parent = None
        self.previous = None
        self.children = []
        self.height = 0

    def layout(self):
        child = Layout(self.node, self, None)
        self.children.append(child)

        self.width = globals.SCwidth - 2 * globals.HSTEP
        self.x = globals.HSTEP
        self.y = globals.VSTEP
        child.layout()
        self.height = child.height

    def should_paint(self):
        return True

    def paint(self):
        return []