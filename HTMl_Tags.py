# classes for HTML tags
class Text:
    def __init__(self, text, parent):
        self.text = text
        self.children = []
        self.parent = parent

    def __repr__(self):
        return repr(self.text)
    
class Element:
    def __init__(self, tag, parent, attributes):
        self.tag = tag
        self.attributes = attributes
        self.children = []
        self.parent = parent

    def __repr__(self):
        return repr(self.tag)
    
#Selectors for CSS parsing
class TagSelector:
    def __init__(self, tag):
        self.tag = tag
        self.priority = 1

    def matches(self, node) -> bool:
        return isinstance(node, Element) and node.tag == self.tag
    
class DescendantSelector:
    def __init__(self, ancestor, descendant):
        self.ancestor = ancestor
        self.descendant = descendant
        self.priority = ancestor.priority + descendant.priority
    
    def matches(self, node) -> bool:
        # check if the descendant matches
        if not self.descendant.matches(node): return False

        # loop through ancestors, checking for any matches
        while node.parent:
            if self.ancestor.matches(node.parent): return True
            node = node.parent 

        # no matches found
        return False