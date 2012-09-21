
def createOrAppend(container, key, el):
    if key in container:
        container[key].append(el)
        return
    container[key] = [el]
    
def normalizeFileLines(filename):
    """Cleans up a file removing unwanted newlines and carriage returns.
    Removes '\r's and extra newline characters. Necessary so analysis is consistent
    """

    with open(filename, 'rb') as fin:
        data = fin.read()
    #TODO: Would regex be quicker?
    while data.count(b'\r'):
        idx = data.index(b'\r')
        data = data[:idx] + data[idx + 1:]
    while data.startswith(b'\n'):
        data = data[1:]
    while data.endswith(b'\n\n'):
        data = data[:-1]
    if not data.endswith(b'\n'):
        data += b'\n'
    return data
