from Text import Text
from Element import Element
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
        text = ""
        attribute_text = ""
        in_tag = False
        in_script_tag = False  # Flag to track if inside a <script> tag
        in_attribute = False # Flag to track if inside attribute

        if scheme == "view-source":
            return Text(self.body, None)
        
        for c in self.body:
            if c == "<":
                in_tag = True
                if not self.in_style_tag: pass
                if not in_script_tag: pass
                if attribute_text:
                    self.addText(checkEntity(attribute_text))
                    
                if text:
                    self.addText(checkEntity(text))

                text = ""

            elif c == ">":
                in_tag = False
                tag_name = text.split()[0].lower()
                if tag_name == "script":
                    in_script_tag = True
                elif tag_name == "/script":
                    in_script_tag = False
                self.addTag(text)
                text = ""

            else:
                if c == '"' or c == "'":
                    in_attribute = not in_attribute
                    attribute_text = ""

                if in_attribute: 
                    attribute_text += c

                else:
                    text += c
                    
        if not in_tag and text and not self.in_style_tag and not in_script_tag:
            self.addText(checkEntity(text))
        
        return self.finish()
    
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

    # gets attributes of text
    def getAttributes(self, text):
        textParts = text.split()
        tag = textParts[0].casefold()
        attributes = {}

        for pair in tag[1:]:
            if "=" in pair:
                key, value = pair.split("=", 1)

                if len(value) > 2 and value[0] in ["'", "\""]:
                    value = value[1:-1]

                attributes[key.casefold()] = value
            else:
                attributes[pair.casefold()] = ""

        return tag, attributes

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
