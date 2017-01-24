#!/usr/bin/env python3
# Copyright 2017 Kevin Froman - MIT License - https://ChaosWebs.net/
import configparser, os, sys, shutil, subprocess

# configparser: needed for site configuration
# os: cross platform file operations mostly
# sys: exit
# shutil: more file operations

# Detect color support (if colorama is installed):
try:
    import colorama
except ImportError:
    print('Unable to load colorama, colors will not be used')

# Version
version = '0.1'

def help():
    print('''TinyGen ''' + version + '''\n
Copyright 2017 Kevin Froman (MIT/Expat License) https://ChaosWebs.net/

''' + sys.argv[0] + ''' edit [post title] - create/edit a page
''' + sys.argv[0] + ''' help - show this help message
''' + sys.argv[0] + ''' rebuild - rebuild all pages

Creating a website:

    Do ''' + sys.argv[0] + ''' edit [post title] to start creating or editing a page

    Open & edit ''' + cfgFile + ''' to change site metadata & the pages on the navigation bar.

    Optionally edit source/theme.css to change the global styles.
    Optionally edit source/page-template.html to change global markup

''')

def createFile(name):
    # Create a source file if it does not exist
    if os.path.exists('source/pages/' + name + '.html'):
        return
    with open('source/pages/' + name + '.html', 'w') as place:
        place.write('')
    return

def fatalError(msg):
    # print a fatal error and exit with an error status code
    print(msg)
    sys.exit(1)
    return

def generatePage(title, edit):
    # (re)generate a webpage
    createFile(title)
    navBarPages = config['SITE']['navbar pages'].replace(' ', '').split(',')
    navBar = '<ul id=\'navbar\'>'
    index = False # determines if the current file is the index
    editP = '' # editor proccess
    for i in navBarPages:
        if i == 'index':
            index = True
            i = 'home'
            link = 'index'
        else:
            link = title
        navBar = navBar + '<li class="navBarItem"><a href="' + link + '.html">' + i.title() + '</a> </li>'
    navBar = navBar + '</ul>'
    if edit:
        editP = subprocess.Popen((os.getenv('EDITOR'), 'source/pages/' + title + '.html'))
        editP.wait()
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
    # Rebuild all webpages
    for file in os.listdir('source/pages/'):
        if file.endswith('.html'):
            file = file.replace('.html', '')
            generatePage(file, False)

command = ''
newPostTitle = ''

# Create a config file if it doesnt exist or just load existing one

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

# Parse commands

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
elif command == 'rebuild':
    rebuild()
else:
    help()
