import os, configparser, sys
def detectKind(kind):
    if kind == 'page':
        kind = 'pages'
    elif kind == 'post':
        kind = 'posts'
    return kind

def deleteFile(name, kind):
    # Deletes a page or post from a site
    kind = detectKind(kind)
    try:
        os.remove('source/' + kind + '/' + name + '.html')
    except PermissionError:
        print('Could not delete source file: ' + name + '. Reason: PermissionError')
    try:
        if kind == 'posts':
            os.remove('generated/blog/' + name + '.html')
        elif kind == 'pages':
            os.remove('generated/' + name + '.html')
    except PermissionError:
        print('Could not delete generated file: ' + name + '. Reason: PermissionError')
    print('Successfully deleted: ' + name)
    return

def createFile(name, kind):
    kind = detectKind(kind)
    # Create a source file if it does not exist
    if os.path.exists('source/' + kind + '/' + name + '.html'):
        return
    with open('source/' + kind + '/' + name + '.html', 'w') as place:
        place.write('')
    return