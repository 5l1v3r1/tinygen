# Copyright 2017 Kevin Froman - MIT License - https://ChaosWebs.net/
import glob

def listFiles(showType):
    files = ['']
    if showType == 'posts':
        files = glob.glob('source/posts/*.html')
    elif showType == 'pages':
        files = glob.glob('source/pages/*.html')
    elif showType == 'drafts':
        files = glob.glob('source/posts/drafts/*.html')
    for i in files:
        print(i.replace('source/pages/', '').replace('source/posts/', '').replace('drafts/', '').replace('.html', '').replace('-', ' '))
    return
