#!/usr/bin/env python3
# Copyright 2017 Kevin Froman - MIT License - https://ChaosWebs.net/
import configparser, os, sys, shutil

# Detect color support:
try:
    import colorama
except ImportError:
    print('Unable to load colorama, colors will not be used')

version = '0.1'

def help():
    print('''Cement ''' + version + '''\n
Copyright 2017 Kevin Froman (MIT/expat License) https://ChaosWebs.net/

''' + sys.argv[0] + ''' edit [post title] - create/edit a post
''' + sys.argv[0] + ''' help - show this help message
''' + sys.argv[0] + ''' rebuild - rebuild all pages
''')

def createFile(name):
    if os.path.exists('source/pages/' + name + '.html'):
        return
    with open('source/pages/' + name + '.html', 'w') as place:
        place.write('')
    return

def fatalError(msg):
    print(msg)
    sys.exit(1)
    return

def generatePage(title, edit):
    navBarPages = config['SITE']['navbar pages'].replace(' ', '').split(',')
    navBar = '<ul id=\'navbar\'>'
    index = False
    for i in navBarPages:
        if i == 'index':
            index = True
            i = 'home'
        navBar = navBar + '<li class="navBarItem"><a href="' + i + '.html">' + i.title() + '</a> </li>'
    navBar = navBar + '</ul>'
    createFile(title)
    if edit:
        os.system('sensible-editor source/pages/' + title + '.html')
    content = open('source/pages/' + title + '.html', 'r').read()
    template = open('source/page-template.html', 'r').read()
    if title == 'index':
        title = 'home'
    page = template.replace('[{TITLE}]', title.title())
    page = page.replace('[{SITETITLE}]', config['SITE']['title'])
    page = page.replace('[{AUTHOR}]', config['SITE']['author'])
    page = page.replace('[{SITETITLE}]', config['SITE']['title'])
    page = page.replace('[{CONTENT}]', content)
    page = page.replace('[{SITEFOOTER}]', config['SITE']['footer'])
    page = page.replace('[{NAVBAR}]', navBar)
    if index:
        title = 'index'
    with open('generated/' + title + '.html', 'w') as result:
        result.write(page)
    shutil.copyfile('source/theme.css', 'generated/theme.css')
    print('Successfully generated page: ' + title)
    return

def rebuild():
    for file in os.listdir('source/pages/'):
        if file.endswith('.html'):
            file = file.replace('.html', '')
            generatePage(file, False)

command = ''
newPostTitle = ''

cfgFile = 'config.cfg'

config = configparser.ConfigParser()

config['SITE'] = {'title': 'My Site', 'author': 'anonymous', 'description': 'Welcome to my site!', 'footer': '', 'navbar pages': ''}

if not os.path.exists(cfgFile):
    try:
        with open(cfgFile, 'w') as configfile:
            config.write(configfile)
    except PermissionError:
        fatalError('Unable to load config, no permission.')
try:
    config.read(cfgFile)
except PermissionError:
    fatalError('Unable to load config, no permission.')

try:
    command = sys.argv[1]
except IndexError:
    command = 'help'

if command == 'edit':
    try:
        newPostTitle = sys.argv[2]
    except IndexError:
        fatalError('syntax: edit "page title"')
    generatePage(newPostTitle, True)
if command == 'rebuild':
    rebuild()
else:
    help()
