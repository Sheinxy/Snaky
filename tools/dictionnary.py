
def find_all(collection, key, value, case_sensitive=True):
    '''
        Finds all the elements with the asked key-value pair in a list of elements
    '''
    match = []
    if not case_sensitive:
        value = value.lower()
    for element in collection:
        attribute = getattr(element, key)
        if not case_sensitive:
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
        attribute = getattr(element, key)
        if not case_sensitive:
            attribute = attribute.lower()
        if attribute == value:
            match = element
            break
    return match