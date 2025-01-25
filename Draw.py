class DrawText:
    def __init__(self, x1, y1, text, font, color):
        self.x1 = x1
        self.y1 = y1 + font.metrics("linespace")
        self.text = text
        self.font = font
        self.color = color
        self.rect = Rect(x1, y1, x1 + font.measure(text), y1 + font.metrics("linespace"))

    def execute(self, scroll, canvas):
        canvas.create_text(
            self.x1, 
            self.y1 - scroll - self.font.metrics("linespace"),
            text = self.text,
            font = self.font,
            fill = self.color,
            anchor = 'nw',
        ) 

class Rect:
    def __init__(self, left, top, right, bottom):
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom

    def contains_point(self, x, y):
        return x >= self.left and x < self.right \
            and y >= self.top and y < self.bottom

class DrawRectangle:
    def __init__(self, rect, colour):
        self.rect = rect
        self.colour = colour

    def execute(self, scroll, canvas):
        canvas.create_rectangle(
            self.rect.left, 
            self.rect.top - scroll,
            self.rect.right, 
            self.rect.bottom - scroll,
            width=0,
            fill=self.colour
        )
        
class DrawOutline:
    def __init__(self, rect, colour, thickness):
        self.rect = rect
        self.colour = colour
        self.thickness = thickness

    def execute(self, scroll, canvas):
        canvas.create_rectangle(
            self.rect.left, self.rect.top - scroll,
            self.rect.right, self.rect.bottom - scroll,
            width=self.thickness,
            outline=self.colour
        )
    
class DrawLine:
    def __init__(self, x1, y1, x2, y2, color, thickness):
        self.rect = Rect(x1, y1, x2, y2)
        self.color = color
        self.thickness = thickness

    def execute(self, scroll, canvas):
        canvas.create_line(
            self.rect.left, self.rect.top - scroll,
            self.rect.right, self.rect.bottom - scroll,
            fill=self.color, width=self.thickness
        )