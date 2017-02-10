#!/usr/bin/env python3
# Copyright 2017 Kevin Froman - MIT License - https://ChaosWebs.net/

import sys

if sys.version_info.major == 2:
    sys.stderr.write('Python 2 is not supported. Please use Python 3.\n')
    sys.exit(1)

import configparser, os, shutil, subprocess, tgblog, createDelete

# configparser: needed for site configuration
# os: cross platform file operations mostly
# sys: exit & version info
# shutil: more file operations

# Ansi codes
GREEN = '\033[92m'
RESET = '\033[0m'
UNDERLINE = '\033[04m'
RED = '\033[31m'

# Version
version = '0.1'

def help():
    print(GREEN + '''TinyGen ''' + RESET + version + '''\n
Copyright 2017 Kevin Froman (MIT/Expat License) ''' + UNDERLINE + '''https://ChaosWebs.net/''' + RESET + '''

''' + GREEN + sys.argv[0] + RESET + ''' edit [page title] - create/edit a page
''' + GREEN + sys.argv[0] + RESET + ''' help - show this help message
''' + GREEN + sys.argv[0] + RESET + ''' rebuild - rebuild all pages
''' + GREEN + sys.argv[0] + RESET + ''' delete [page title] - delete a page

Creating a website:

    Do ''' + GREEN + sys.argv[0] + RESET + ''' edit [post title] to start creating or editing a page

    Open & edit ''' + cfgFile + ''' to change site metadata & the pages on the navigation bar.

    Optional: edit source/theme.css to change the global styles.
    Optional: edit source/page-template.html to change global markup

''')
    return

def fatalError(msg):
    # print a fatal error and exit with an error status code
    print(RED + msg + RESET)
    sys.exit(1)
    return

def generatePage(title, edit):
    # (re)generate a webpage
    createDelete.createFile(title, 'page')
    navBarPages = config['SITE']['navbar pages'].replace(' ', '').split(',')
    navBar = '<ul id=\'navbar\'>'
    index = False # determines if the current file is the index
    editP = '' # editor proccess
    for i in navBarPages:
        if i == 'index':
            link = 'home'
        else:
            link = i
        navBar = navBar + '<li class="navBarItem"><a href="' + i + '.html">' + link.title() + '</a> </li>'
    navBar = navBar + '</ul>'
    if edit:
        editP = subprocess.Popen((os.getenv('EDITOR'), 'source/pages/' + title + '.html'))
        editP.wait()
    content = open('source/pages/' + title + '.html', 'r').read()
    template = open('source/page-template.html', 'r').read()
    if title == 'index':
        title = 'home'
        index = True
    page = template.replace('[{TITLE}]', title.title())
    page = page.replace('[{SITETITLE}]', config['SITE']['title'])
    page = page.replace('[{AUTHOR}]', config['SITE']['author'])
    page = page.replace('[{CONTENT}]', content)
    page = page.replace('[{SITEFOOTER}]', config['SITE']['footer'])
    page = page.replace('[{NAVBAR}]', navBar)
    page = page.replace('[{SITEDESC}]', config['SITE']['description'])
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
    return

command = ''
newPageTitle = ''

# Create a config file if it doesnt exist or just load existing one

cfgFile = 'config.cfg'

config = configparser.ConfigParser()

config['SITE'] = {'title': 'My Site', 'author': 'anonymous', 'description': 'Welcome to my site!', 'footer': '', 'navbar pages': ''}
config['BLOG'] = {'title': 'My Blog', 'footer': '', 'lines-preview': '', 'blog intro': 'welcome to my blog!', 'description': ''}

deleteTitle = ''

# Blog variables, argument (command) and its return status
blogArg = ''

blogReturn = ''

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
        newPageTitle = sys.argv[2]
    except IndexError:
        fatalError('syntax: edit "page title"')
    try:
        generatePage(newPageTitle, True)
    except:
        fatalError('Unknown error occured')
elif command == 'rebuild':
    rebuild()
elif command == 'delete':
    try:
        deleteTitle = sys.argv[2]
    except IndexError:
        fatalError('syntax: delete "page title"')
    createDelete.deleteFile(deleteTitle, 'page')
elif command == 'blog':
    try:
        blogArg = sys.argv[2]
    except IndexError:
        fatalError('Blog takes at least 1 more argument')

    blogReturn = tgblog.blog(blogArg, config)
    if blogReturn[0] == 'error':
        fatalError(blogReturn[1])
    else:
        print(blogReturn[1])
else:
    help()