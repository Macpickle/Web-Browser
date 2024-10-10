from URL import URL
from GUI import GUI
import tkinter;

if __name__ == "__main__":
    import sys

    HSTEP, VSTEP, SCROLL_STEP = 13, 18, 100
    tags = ""
    if len(sys.argv) >= 2:
        tags = sys.argv[2:]
    window = GUI(tags)

    if len(sys.argv) > 1:
        url = URL(sys.argv[1])
    else:
        url = URL("about:blank")

    window.load(url)
    tkinter.mainloop()