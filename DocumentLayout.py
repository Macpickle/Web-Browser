from Layout import Layout

class DocumentLayout:
    def __init__(self, node):
        self.node = node
        self.parent = None
        self.children = []

    def layout(self):
        child = Layout(self.node, self, None)
        self.children.append(child)
        child.layout()