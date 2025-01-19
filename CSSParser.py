class CSSParser:
    def __init__(self, s):
        self.s = s
        self.index = 0 # starting index of whitespace

    # add to index for all whitespaces
    def whitespace(self):
        while self.index < len(self.s) and self.s[self.index].isspace():
            self.index += 1

    # parse property names
    def word(self):
        start = self.index

        while self.index < len(self.s):
            if self.s[self.index].isalnum() or self.s[self.index] in "#-.%":
                self.index += 1

            else:
                break

        if not (self.index > start):
            raise Exception("Whitespace Parsing Error")
        
        return self.s[start:self.index]

    # check for literal punctuation
    def literal(self, literal):
        if not (self.index < len(self.s) and self.s[self.index] == literal):
            raise Exception("Parsing error")
        self.index += 1

    def pair(self):
        prop = self.word()
        self.whitespace()
        self.literal(":")
        self.whitespace()
        val = self.word()
        return prop.casefold(), val
    
    def body(self):
        pairs = {}

        while self.index < len(self.s):
            try:
                prop, val = self.pair() 
                pairs[prop.casefold()] = val # set hash val
                self.whitespace()
                self.literal(";")
                self.whitespace()

            except Exception:
                reason = self.ignore([";"])

                if reason == ";":
                    self.literal(";")
                    self.whitespace()

                else:
                    break

        return pairs
    
    # deals with error from author or non supported items
    def ignore(self, chars):
        while self.index < len(self.s):
            if self.s[self.index] in chars:
                return self.s[self.index]
            
            else:
                self.index += 1

        # no errors
        return None

        