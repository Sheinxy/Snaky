
def find_all(collection, key, value, case_sensitive=True):
    '''
        Finds all the elements with the asked key-value pair in a list of elements
    '''
    match = []
    if not case_sensitive:
        value = value.lower()
    for element in collection:
        attribute = None
        if isinstance(element, dict) and key in element:
            attribute = element[key]
        else:
            attribute = getattr(element, key, None)
        if attribute and not case_sensitive:
            attribute = attribute.lower()
        if attribute == value:
            match.append(element)
    return match

def find(collection, key, value, case_sensitive=True):
    '''
        Finds the first element with the asked key-value pair in a list of elements
    '''
    match = None
    if not case_sensitive:
        value = value.lower()
    for element in collection:
        attribute = None
        if isinstance(element, dict) and key in element:
            attribute = element[key]
        else:
            attribute = getattr(element, key, None)
        if attribute and not case_sensitive:
            attribute = attribute.lower()
        if attribute == value:
            match = element
            break
    return match

def get_all(collection, key):
    '''
        Finds all the attributes of all the elements with the asked key in a list of elements
    '''
    match = []
    for element in collection:
        attribute = None
        if isinstance(element, dict) and key in element:
            attribute = element[key]
        else:
            attribute = getattr(element, key, None)
        if attribute:
            match.append(attribute)
    return match

def get(collection, key):
    '''
        Finds the attribute of the first element with the asked key in a list of elements
    '''
    match = None
    for element in collection:
        attribute = None
        if isinstance(element, dict) and key in element:
            attribute = element[key]
        else:
            attribute = getattr(element, key, None)
        if attribute:
            match = attribute
            break
    return match