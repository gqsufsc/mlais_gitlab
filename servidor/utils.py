import os, fnmatch

## https://stackoverflow.com/questions/1724693/find-a-file-in-python
# return a match pattern
def find(pattern, path):
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    return result

# return all matches
def find_all(name, path):
    result = []
    for root, dirs, files in os.walk(path):
        if name in files:
            result.append(os.path.join(root, name))
    return result

# return first match
def find_first(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)