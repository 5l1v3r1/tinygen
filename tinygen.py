#!/usr/bin/env python3
# Copyright 2017 Kevin Froman - MIT License - https://ChaosWebs.net/

import sys

if sys.version_info.major == 2:
    sys.stderr.write('Python 2 is not supported. Please use Python 3.\n')
    sys.exit(1)

import configparser, os, shutil, subprocess, tgblog, createDelete, tgsocial, imp, tgplugins

# configparser: needed for site configuration
# os: cross platform file operations mostly
# sys: exit & version info
# shutil: more file operations
# markdown: self explainatory. Not in standard libs.

# Ansi codes
GREEN = '\033[92m'
RESET = '\033[0m'
UNDERLINE = '\033[04m'
RED = '\033[31m'

markdownSupport = True

try:
    import markdown
except ImportError:
    print(RED + 'Notice: ' + RESET + ' markdown library not installed. Try installing with pip.\nWill not be able to use markdown.')
    markdownSupport = False
# Version
version = '0.2'

pluginFolder = 'plugins/'
MainModule = "__init__" # Main module name for plugins

def help(helpType):
    # Show help information
    print(GREEN + '''TinyGen ''' + RESET + version + '''\n
Copyright 2017 Kevin Froman (MIT/Expat License) ''' + UNDERLINE + '''https://ChaosWebs.net/''' + RESET + '\n')

    if helpType == 'normal':
        print(GREEN + sys.argv[0] + RESET + ''' edit [page title] - create/edit a page
''' + GREEN + sys.argv[0] + RESET + ''' help - show this help message
''' + GREEN + sys.argv[0] + RESET + ''' rebuild - rebuild all pages
''' + GREEN + sys.argv[0] + RESET + ''' delete [page title] - delete a page ''' +
'''

Creating a website:

    Do ''' + GREEN + sys.argv[0] + RESET + ''' edit [post title] to start creating or editing a page

    Open & edit ''' + cfgFile + ''' to change site metadata & the pages on the navigation bar.

    Optional: edit source/theme/''' + themeName + '''/theme.css to change the global styles.
    Optional: edit source/page-template.html to change global markup\n''')

    elif helpType == 'blog':
                print(GREEN + sys.argv[0] + RESET + ''' blog edit [post title] - create/edit a page
        ''' + GREEN + sys.argv[0] + RESET + ''' blog rebuild - rebuild all posts
        ''' + GREEN + sys.argv[0] + RESET + ''' blog delete [posts title] - delete a post ''' +
        '''

        Creating a blog:

            Do ''' + GREEN + sys.argv[0] + RESET + ''' edit [post title] to start creating or editing a post

            Open & edit ''' + cfgFile + ''' to change site metadata & the links on the navigation bar.

            Optional: edit source/theme/''' + themeName + '''/theme.css to change the global styles.
            Optional: edit source/blog-index.html to change the blog index.
            Optional: edit source/blog-template.html to change global markup\n''')
    return
'''
def getPlugins():
    # Loads gets a plugin from the plugin folder
    # based on: https://lkubuntu.wordpress.com/2012/10/02/writing-a-python-plugin-api/
    plugins = []
    possiblePlugins = config['SITE']['plugins'].replace(' ', '').split(',')
    for i in possiblePlugins:
        location = os.path.join(pluginFolder, i)
        if not os.path.isdir(location) or not MainModule + ".py" in os.listdir(location):
            continue
        info = imp.find_module(MainModule, [location])
        plugins.append({"name": i, "info": info})
    return plugins

def loadPlugin(plugin):
    # Loads a plugin
    return imp.load_module(MainModule, *plugin["info"])

def events(event, data):
    retData = ''
    for i in getPlugins():
        plugin = loadPlugin(i)
        if event == 'startup':
            retData = plugin.startup(data)
        elif event == 'genPage':
            retData = plugin.genPage(data)
        elif event == 'deletePage':
            retdata = plugin.deletePage(data)
        else:
            print('Attempted to call unknown event: ' + event)
    return retData
'''

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
        elif i == 'blog':
            i = './blog/index'
            link = 'Blog'
        else:
            link = i
        navBar = navBar + '<li class="navBarItem"><a href="' + i + '.html">' + link.title() + '</a> </li>'
    navBar = navBar + '</ul>'
    if edit:
        try:
            editP = subprocess.Popen((os.getenv('EDITOR'), 'source/pages/' + title + '.html'))
            editP.wait()
        except TypeError:
            print('Unable to edit: ' + title + '. reason: editor environment variable is not set')
            return
    content = open('source/pages/' + title + '.html', 'r').read()

    if markdownSupport:
        content = markdown.markdown(content)

    template = open('source/page-template.html', 'r').read()
    if title == 'index':
        title = 'home'
        index = True
    page = tgplugins.events('genPage', template, config)
    page = page.replace('[{TITLE}]', title.title())
    page = page.replace('[{SITETITLE}]', config['SITE']['title'])
    page = page.replace('[{AUTHOR}]', config['SITE']['author'])
    page = page.replace('[{CONTENT}]', content)
    page = page.replace('[{SITEFOOTER}]', config['SITE']['footer'])
    page = page.replace('[{NAVBAR}]', navBar)
    page = page.replace('[{SITEDESC}]', config['SITE']['description'])
    page = tgsocial.genSocial(config, page, 'page')
    if index:
        title = 'index'
    with open('generated/' + title + '.html', 'w') as result:
        result.write(page)
    shutil.copyfile('source/theme/' + themeName + '/theme.css', 'generated/theme.css')
    try:
        shutil.rmtree('generated/images/')
    except FileNotFoundError:
        pass
    shutil.copytree('source/theme/' + themeName + '/images/', 'generated/images/')
    print('Successfully generated page: ' + title)
    return

def rebuild():
    # Rebuild all webpages
    tgplugins.events('rebuild', '', config)
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

config['SITE'] = {'title': 'My Site', 'author': 'anonymous', 'description': 'Welcome to my site!', 'footer': 'Powered By TinyGen', 'navbar pages': '', 'domain': 'example.com', 'theme': 'default', 'plugins': ''}
config['BLOG'] = {'title': 'My Blog', 'standalone': 'false', 'footer': 'Powered by TinyGen', 'lines-preview': '3', 'blog intro': 'welcome to my blog!', 'description': 'just a random blog', 'twitter': '', 'github': '', 'facebook': '', 'email': '', 'keybase': '', 'google': ''}

deleteTitle = ''

helpType = ''

formatType = ''

plugins = ''
plName = ''

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

# Set the theme name
themeName = config['SITE']['theme']

# run plugin startup event

tgplugins.events('startup', '', config)

# Parse commands

try:
    command = sys.argv[1].lower()
except IndexError:
    command = 'help'

if command == 'edit':
    try:
        newPageTitle = sys.argv[2]
    except IndexError:
        fatalError('syntax: edit "page title"')
    try:
        generatePage(newPageTitle, True)
    except Exception as e:
        fatalError('Unknown error occured (during edit): ' + str(e))
elif command == 'rebuild':
    rebuild()
elif command == 'delete':
    try:
        deleteTitle = sys.argv[2]
    except IndexError:
        fatalError('syntax: delete "page title"')
    tgplugins.events('deletePage', 'delete', config)
    try:
        createDelete.deleteFile(deleteTitle, 'page')
    except FileNotFoundError:
        fatalError('Could not delete page: ' + deleteTitle + ' reason: page does not exist.')
elif command == 'blog':
    try:
        blogArg = sys.argv[2].lower()
    except IndexError:
        help('blog')
    blogReturn = tgblog.blog(blogArg, config)
    if blogReturn[0] == 'error':
        fatalError(blogReturn[1])
    else:
        print(blogReturn[1])
elif command == 'help':
    try:
        helpType = sys.argv[2]
        help('blog')
    except IndexError:
        help('normal')
else:
    help('normal')