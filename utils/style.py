from CSSParser import CSSParser
from HTMl_Tags import Element
INHERITED_PROPERTIES = {
    "font-size": "16px",
    "font-style": "normal",
    "font-weight": "normal",
    "color": "black",
    "font-family": "Arial, sans-serif",
}

# css styling of node
def style(node, rules):
    node.style = {}

    # apply styles of inherited style
    for prop, default_value in INHERITED_PROPERTIES.items():
        if node.parent:
            node.style[prop] = node.parent.style[prop]
        else:
            node.style[prop] = default_value

    # apply properties and values to node styling
    for selector, body in rules:
        if not selector.matches(node): continue
        for prop, val in body.items():
            node.style[prop] = val

    # checks if node is an element, and if its in style attribute
    if isinstance(node, Element) and "style" in node.attributes:
        pairs = CSSParser(node.attributes["style"]).body()
        for prop, val in pairs.items():
            node.style[prop] = val

    # deal with special cases (eg. % size from parent)
    if node.style["font-size"].endswith("%"):
        if node.parent:
            parent_font_size = node.parent.style["font-size"]
        else:
            parent_font_size = INHERITED_PROPERTIES["font-size"]
        node_pct = float(node.style["font-size"][:-1]) / 100
        parent_px = float(parent_font_size[:-2])
        node.style["font-size"] = str(node_pct * parent_px) + "px"

    # Ensure <code> elements use a monospaced font
    if isinstance(node, Element) and node.tag == "code":
        node.style["font-family"] = "Courier, monospace"
            
    for child in node.children:
        style(child, rules)