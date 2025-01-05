from Layout import Layout
from globals import *

class DocumentLayout:
    def __init__(self, node):
        self.node = node
        self.parent = None
        self.children = []

        # position of document layout
        self.x = None
        self.y = None
        self.width = None
        self.height = None

    def layout(self):
        child = Layout(self.node, self, None)
        self.children.append(child)
        child.layout()

        self.width = SCwidth - 2*HSTEP
        self.x = HSTEP
        self.y = VSTEP
        child.layout()
        self.height = child.height