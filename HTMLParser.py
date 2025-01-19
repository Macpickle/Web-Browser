from HTMl_Tags import Element, Text
from checkEntity import checkEntity
from URL import URL

class HTMLParser:
    def __init__(self, body) -> None:
        self.body = body
        self.unfinished = []
        self.selfClosing = [ "area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr", ] # tags that dont require a closing tag
        self.headTags = [ "base", "basefont", "bgsound", "noscript", "link", "meta", "title", "style", "script"] # tags that are only allowed in the head tag
        self.in_style_tag = False  # Flag to track if inside a <style> tag

    # parse body of html 
    def parse(self, scheme):
        text = "" # contains current text (not in a tag)
        inTag = False # Flag to track if inside a tag
        inScriptTag = False # Flag to track if inside a <script> tag

        # special case for view-source
        if scheme == "view-source": 
            return Text(self.body, None)
        
        for char in self.body:
            if char == "<":
                inTag = True
                if text: self.addText(checkEntity(text))
                text = ""

            elif char == ">":
                inTag = False
                self.addTag(text)
                text = ""
                
            else:
                text += char

        if not inTag and not inScriptTag and text:
            self.addText(checkEntity(text))
        return self.finish()
    
        # gets attributes of text
    def getAttributes(self, text):
        textParts = text.split()
        tag = textParts[0].casefold()
        attributes = {}
        for part in textParts[1:]:
            if "=" in part:
                key, value = part.split("=",1)
                attributes[key.casefold()] = value.strip("\"'")

            else:
                attributes[part.casefold()] = None
                
        return tag, attributes
    
    # checks for header tags if they are not present
    def implicitTags(self, tag):
        while True:
            openTags = [node.tag for node in self.unfinished]

            if openTags == [] and tag != "html":
                self.addTag("html")

            elif tag == ["html"] and tag not in ["head", "body", "/html"]:
                if tag in self.headTags:
                    self.addTag("head")

                else:
                    self.addTag("body")

            elif openTags == ["html", "head"] and tag not in ["/head"] + self.headTags:
                self.addTag("/head")

            else:
                break

    # creates a text node
    def addText(self, text):
        if text.isspace() or self.in_style_tag: return
        self.implicitTags(None)

        parent = self.unfinished[-1]
        node = Text(text, parent)
        parent.children.append(node)

    # creates a tag node
    def addTag(self, tag):
        tag, attributes = self.getAttributes(tag)  
        if tag.startswith("!doctype"): return
        self.implicitTags(tag)

        if tag.startswith("/"):
            if len(self.unfinished) == 1: return
            node = self.unfinished.pop()
            parent = self.unfinished[-1]
            parent.children.append(node)
            if tag == "/style":
                self.in_style_tag = False  # Exiting a <style> tag

        elif tag in self.selfClosing:
            parent = self.unfinished[-1]
            node = Element(tag, parent, attributes)
            parent.children.append(node)

        else:
            parent = self.unfinished[-1] if self.unfinished else None
            node = Element(tag, parent, attributes)
            self.unfinished.append(node)
            if tag == "style":
                self.in_style_tag = True  # Entering a <style> tag

    # finishes tree
    def finish(self):
        if not self.unfinished:
            self.implicitTags(None)

        while len(self.unfinished) > 1:
            node = self.unfinished.pop()
            parent = self.unfinished[-1]
            parent.children.append(node)
        return self.unfinished.pop()

    # debug print
    def print_tree(self, node, indent=0):
        print(" " * indent, node)
        for child in node.children:
            self.print_tree(child, indent + 2)
