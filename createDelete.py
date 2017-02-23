import os, configparser, sys

## Module to either create or delete a post or a page or post

def detectKind(kind):
    # Detects what kind of file we are making
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
    # Create a source file if it does not exist
    kind = detectKind(kind)
    if os.path.exists('source/' + kind + '/' + name + '.html'):
        return
    with open('source/' + kind + '/' + name + '.html', 'w') as place:
        place.write('')
    return
