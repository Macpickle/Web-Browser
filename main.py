from URL import URL
from Browser import Browser
import tkinter;

if __name__ == "__main__":
    import sys

    HSTEP, VSTEP, SCROLL_STEP = 13, 18, 100
    tags = ""
    if len(sys.argv) >= 2:
        tags = sys.argv[2:]
    window = Browser(tags)

    if len(sys.argv) > 1:
        url = URL(sys.argv[1])
    else:
        url = URL("about:blank")

    window.load(url)
    tkinter.mainloop()