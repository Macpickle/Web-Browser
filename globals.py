# globals used among several files
HSTEP = 13
VSTEP = 18
SCwidth, SCheight = 0, 0

def update_globals(width, height):
    global SCwidth, SCheight
    SCwidth, SCheight = width, height