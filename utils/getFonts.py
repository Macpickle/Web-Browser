import tkinter.font
FONTS = {}

def getFonts(size, weight, style):
    # temp fix, dont know why it sets 400
    if weight == '400':
        weight = 'normal'
    key = (size, weight, style)

    if key not in FONTS:
        font = tkinter.font.Font(size=size, weight=weight, slant=style)
        label = tkinter.Label(font=font)
        FONTS[key] = (font, label)

    return FONTS[key][0]

