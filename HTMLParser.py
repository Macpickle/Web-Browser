class HTMLParser:
    def __init__(self, body) -> None:
        self.body = body
        self.unfinished = []

    def parse(self):
        text = ""
        inTag = False

        for character in self.body:
            if character == "<":
                inTag = True
                if text: self.add_text(text)
                text = ""
            elif character == ">":
                inTag = False
                self.add_tag(text)
                text = ""
            else:
                text += character
            if not inTag and text:
                self.add_text(text)

        return self.finish()

