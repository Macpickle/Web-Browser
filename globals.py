# globals used among several files
HSTEP = 13
VSTEP = 18
SCwidth, SCheight = 0, 0

# updates global for screenwidth and screenheight
def update_globals(width, height):
    global SCwidth, SCheight
    SCwidth, SCheight = width, height