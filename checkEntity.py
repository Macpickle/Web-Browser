def checkEntity(arg):
    entities = {
        "&gt;": ">",
        "&lt;": "<",
        "&amp;": "&",
        "&quot;": "\"",
        "&apos;": "\'",
        "&#39;": ".",
        "&ndash;": "-",
        "&copy;": "©",
    }

    for entity in entities:
        if entity in arg:
            arg = arg.replace(entity, entities[entity])
            
    return arg