from Text import Text
from Element import Element
import sys
from URL import URL

class HTMLParser:
    def __init__(self, body) -> None:
        self.body = body
        self.unfinished = []
        self.selfClosing = [ "area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr", ] # tags that dont require a closing tag
        self.headTags = [ "base", "basefont", "bgsound", "noscript", "link", "meta", "title", "style", "script"] # tags that are only allowed in the head tag

    # parse body of html
    def parse(self):
        text = ""
        in_tag = False
        for c in self.body:
            if c == "<":
                in_tag = True
                if text: self.addText(text)
                text = ""
            elif c == ">":
                in_tag = False
                self.addTag(text)
                text = ""
            else:
                text += c
        if not in_tag and text:
            self.addText(text)

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
        if text.isspace(): return
        self.implicitTags(None)

        parent = self.unfinished[-1]
        node = Text(text, parent)
        parent.children.append(node)

    # creates a tag node
    def addTag(self, tag):
        tag, attributes = self.getAttributes(tag)
        if tag.startswith("!"): return
        self.implicitTags(tag)

        if tag.startswith("/"):
            if len(self.unfinished) == 1: return
            node = self.unfinished.pop()
            parent = self.unfinished[-1]
            parent.children.append(node)

        elif tag in self.selfClosing:
            parent = self.unfinished[-1]
            node = Element(tag, parent, attributes)
            parent.children.append(node)

        else:
            parent = self.unfinished[-1] if self.unfinished else None
            node = Element(tag, parent, attributes)
            self.unfinished.append(node)

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