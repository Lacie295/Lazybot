def elem_in_string(l, msg):
    """
    Check if an element in a list of strings is a substring of the given message
    """
    for elem in l:
        if elem in msg:
            return True
    return False

