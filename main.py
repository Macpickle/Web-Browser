from URL import URL
from Browser import Browser
import tkinter;

if __name__ == "__main__":
    import sys

    tags = ""
    if len(sys.argv) >= 2:
        tags = sys.argv[2:]
    Browser(tags).new_tab(URL(sys.argv[1]))

    if len(sys.argv) > 1:
        url = URL(sys.argv[1])
    else:
        url = URL("about:blank")

    tkinter.mainloop()