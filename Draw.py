class DrawText:
    def __init__(self, x1, y1, text, font, color):
        self.x1 = x1
        self.y1 = y1 + font.metrics("linespace")
        self.text = text
        self.font = font
        self.color = color

    def execute(self, scroll, canvas):
        canvas.create_text(
            self.x1, 
            self.y1 - scroll,
            text = self.text,
            font = self.font,
            fill = self.color,
            anchor = 'nw',
        ) 

class DrawRectangle:
    def __init__(self, x1, y1, x2, y2, colour):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.colour = colour

    def execute(self, scroll, canvas):
        canvas.create_rectangle(
            self.x1, 
            self.y1 - scroll,
            self.x2, 
            self.y2 - scroll,
            width=0,
            fill=self.colour
        )
        