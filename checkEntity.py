from w3lib.html import replace_entities

def checkEntity(arg):
    # replaces entities in text using w3lib
    return replace_entities(arg)