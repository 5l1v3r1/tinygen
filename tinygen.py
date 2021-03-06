#!/usr/bin/env python3
# Copyright 2017 Kevin Froman - MIT License - https://ChaosWebs.net/

import sys

if sys.version_info.major == 2:
    sys.stderr.write('Python 2 is not supported. Please use Python 3.\n')
    sys.exit(1)

import configparser, os, shutil, subprocess, tgblog, createDelete, tgsocial, imp, tgplugins, tgls, titles, readline
try:
    import webServer
except:
    sys.stderr.write('Error loading web server module')

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
    print(RED + 'Notice: ' + RESET + ' Python Markdown library not installed. Try installing with pip.\nWill not be able to use markdown.')
    markdownSupport = False
# Version
version = '1.3'

pluginFolder = 'plugins/'
MainModule = "__init__" # Main module name for plugins

def help(helpType):
    # Show help information, site generation unless blog help is specified
    print(GREEN + '''TinyGen ''' + RESET + version + '''\n
Copyright 2017 Kevin Froman (MIT/Expat License) ''' + UNDERLINE + '''https://ChaosWebs.net/''' + RESET + '\n')

    if helpType == 'normal':
        print(GREEN + sys.argv[0] + RESET + ''' edit [page title] - create/edit a page
''' + GREEN + sys.argv[0] + RESET + ''' help - show this help message
''' + GREEN + sys.argv[0] + RESET + ''' rebuild - rebuild all pages
''' + GREEN + sys.argv[0] + RESET + ''' delete [page title] - delete a page
''' + GREEN + sys.argv[0] + RESET + ''' list - list pages
''' + GREEN + sys.argv[0] + RESET + ''' blog - show commands and info for blogs

Creating a website:

    Do ''' + GREEN + sys.argv[0] + RESET + ''' edit [post title] to start creating or editing a page

    Open & edit ''' + cfgFile + ''' to change site metadata & the pages on the navigation bar.

    Optional: edit source/theme/''' + themeName + '''/theme.css to change the global styles.
    Optional: edit source/page-template.html to change global markup\n''')

    elif helpType == 'blog':
                print(GREEN + sys.argv[0] + RESET + ''' blog edit [post title] - create/edit a page
''' + GREEN + sys.argv[0] + RESET + ''' blog rebuild - rebuild all posts
''' + GREEN + sys.argv[0] + RESET + ''' blog delete [posts title] - delete a post
''' + GREEN + sys.argv[0] + RESET + ''' blog list - list all posts

Creating a blog:

    Do ''' + GREEN + sys.argv[0] + RESET + ''' blog edit [post title] - start creating or editing a post
       ''' + GREEN + sys.argv[0] + RESET + ''' blog draft edit [draft title] - edit a draft
       ''' + GREEN + sys.argv[0] + RESET + ''' blog draft list - list drafts
       ''' + GREEN + sys.argv[0] + RESET + ''' blog draft delete [draft title] - delete a draft
       ''' + GREEN + sys.argv[0] + RESET + ''' blog draft publish [draft title] - publish a draft
       ''' + GREEN + sys.argv[0] + RESET + ''' blog draft redraft [post title] - create a draft from an existing post. Overwrites any existing drafts by the same name.

    Open & edit ''' + cfgFile + ''' to change site metadata & the links on the navigation bar.

    Optional: edit source/theme/''' + themeName + '''/theme.css to change the global styles.
    Optional: edit source/blog-index.html to change the blog index.
    Optional: edit source/blog-template.html to change global markup\n''')
    print('''Testing the site/blog:
    Either open the index.html file in your browser, or:

    Do ''' + GREEN + sys.argv[0] + RESET + ''' server - start the testing web server
        (edit the port in ''' + cfgFile + ''' if you want to host on port 80, under ETC)

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
    doMD = ''
    for i in navBarPages:
        if i == 'index':
            link = 'home'
        elif i == 'blog':
            i = './blog/index'
            link = 'Blog'
        else:
            if i != '':
                link = i # ./ is done because some characters like ':' are weird without it
            else:
                link = i
            if not i.startswith('#'):
                i = './' + i + '.html'
            else:
                link = link.replace('#', '')

        navBar = navBar + '<li class="navBarItem"><a href="' + i + '">' + titles.convTitle(link) + '</a> </li>'
    navBar = navBar + '</ul>'
    if edit:
        try:
            if config['ETC']['no-editor'] == 'false':
                if os.getenv('EDITOR') is None:
                    print('Editor environment variable not defined. Edit source/pages/' + title + '.html, then press enter to continue')
                    input()
                else:
                    editP = subprocess.Popen((os.getenv('EDITOR'), 'source/pages/' + title + '.html'))
                    editP.wait()
            elif config['ETC']['no-editor'] == 'true':
                print('no-editor is set to true, waiting for you to edit it manually.')
                input()

        except TypeError:
            print('Unable to edit: ' + title + '. reason: editor environment variable is not set')
            return False
    content = open('source/pages/' + title + '.html', 'r').read()
    if content == '':
        print('Edited file is empty, still save it? y/n')
        doSave = input('>').lower()
        if doSave in ('y', 'yes'):
            print('Saving')
        else:
            print('Not saving')
            return False
    if markdownSupport:
        if config['SITE']['markdown-prompt'] == 'true':
            print('Do you want to encode Markdown for this page? y/n')
            doMD = input('>').lower()
            if doMD in ('y', 'yes'):
                print('Using Markdown')
                content = markdown.markdown(content)
            else:
                print('Not using Markdown')
        else:
            content = markdown.markdown(content)

    template = open('source/page-template.html', 'r').read()
    if title == 'index':
        title = 'home'
        index = True
    page = tgplugins.events('genPage', template, config)
    if config['SITE']['embed-titles'] == 'false':
        page = page.replace('[{TITLE}]', titles.convTitle(title), 1)
        page = page.replace('[{TITLE}]', '')
    else:
        page = page.replace('[{TITLE}]', titles.convTitle(title))
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
    try:
        shutil.rmtree('generated/res/')
        os.mkdir('generated/res/')
    except FileNotFoundError:
        pass
    try:
        createDelete.copytree('source/pages/res/', 'generated/res/')
    except FileNotFoundError:
        pass
    except FileExistsError:
        pass
    print('Successfully generated page: ' + title)
    return True

def rebuild():
    # Rebuild all webpages
    tgplugins.events('rebuild', '', config)
    for file in os.listdir('source/pages/'):
        if file.endswith('.html'):
            file = file.replace('.html', '')
            generatePage(file, False)
    print('Copying images...')
    shutil.copytree('source/pages/images/', 'generated/images/')
    createDelete.copytree('source/theme/' + themeName + '/images/', 'generated/images/')
    return

command = ''
newPageTitle = ''

# Create a config file if it doesnt exist or just load existing one

cfgFile = 'config.cfg'

config = configparser.ConfigParser()

config['SITE'] = {'title': 'My Site', 'markdown-prompt': 'false', 'author': 'anonymous', 'description': 'Welcome to my site!', 'footer': 'Powered By TinyGen', 'navbar pages': '', 'domain': 'example.com', 'theme': 'default', 'plugins': '', 'embed-titles': 'true'}
config['BLOG'] = {'title': 'My Blog', 'markdown-prompt': 'false', 'standalone': 'false', 'rss': 'true', 'posts-per-page': '10', 'footer': 'Powered by TinyGen', 'lines-preview': '3', 'blog-intro': 'Just a random blog', 'theme': 'default', 'description': 'just a random blog', 'twitter': '', 'github': '', 'facebook': '', 'email': '', 'keybase': '', 'google': ''}
config['ETC'] = {'color-output': 'true', 'server-port': '8080', 'server-ip': '127.0.0.1', 'no-editor': 'false'}

deleteTitle = ''

helpType = ''

formatType = ''

plugins = ''
plName = ''

didEdit = False # if the page was edited successfully

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

# Turn off colors if it is false in config

if config['ETC']['color-output'] == 'false':
    GREEN = ''
    RESET = ''
    UNDERLINE = ''
    RED = ''


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
        newPageTitle = sys.argv[2].replace(' ', '-')
    except IndexError:
        fatalError('syntax: edit "page title"')
    try:
        didEdit = generatePage(newPageTitle, True)
    except Exception as e:
        fatalError('Unknown error occured (during edit): ' + str(e))
    if didEdit:
        try:
            print('Copying images...')
            shutil.copytree('source/pages/images/', 'generated/images/')
            createDelete.copytree('source/theme/' + themeName + '/images/', 'generated/images/')
        except Exception as e:
            fatalError('Unknown error while copying images: ' + str(e))
elif command == 'rebuild':
    rebuild()
elif command == 'delete':
    try:
        deleteTitle = sys.argv[2]
        deleteTitle = deleteTitle.replace(' ', '-')
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
elif command == 'list':
    print('Listing pages...')
    tgls.listFiles('pages')
elif command == 'server':
    print('Starting server')
    retData = webServer.webServer(config)
    if retData == 'port already taken':
        fatalError('Configured port for web server already taken')

elif command == 'help':
    try:
        helpType = sys.argv[2]
        help('blog')
    except IndexError:
        help('normal')
else:
    if tgplugins.events('commands', sys.argv, config) != True: # This has to be written this way because the var isn't strictly boolean
        fatalError('Unknown command: ' + command + '. Run \'' + sys.argv[0] + ' help\' for more information.')
