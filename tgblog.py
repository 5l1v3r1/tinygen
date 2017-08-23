# Copyright 2017 Kevin Froman - MIT License - https://ChaosWebs.net/
import sys, os, configparser, createDelete, subprocess, shutil, sqlite3, time, datetime, tgsocial, tgrss, tgplugins, tgls, titles

markdownSupport = True # if the user has python markdown, which isn't standard library.
try:
    import markdown
except ImportError:
    markdownSupport = False

def getPostDate(title):
    # Get the post's date from database and return it (should be epoch format)
    conn = sqlite3.connect('.data/posts.db')
    c = conn.cursor()
    date = 0
    data = (title,)
    for row in c.execute('SELECT DATE FROM Posts where title=?', (data)):
        date = row[0]
    conn.close()
    return date

def updatePostList(title, add):
    # Add or remove a post from the database
    # add is either 'add' or 'remove'
    conn = sqlite3.connect('.data/posts.db')
    c = conn.cursor()
    if add == 'add':
        data = (title, str(int(time.time())))
        c.execute('INSERT INTO Posts (title, date) Values (?,?)', (data))
        status = ('success', 'Added post to database: ' + title)
    elif add == 'remove':
        data = (title,)
        c.execute('DELETE FROM Posts where TITLE = ?', (data))
        status = ('success', 'Removed post from database: ' + title)
    conn.commit()
    conn.close()

    return status

def rebuildIndex(config):
    # Rebuild the blog index.html file and move res folder

    indexTemplate = 'source/blog-index.html'
    indexProdFile = 'generated/blog/index.html'
    conn = sqlite3.connect('.data/posts.db')
    content = ''
    postList = ''
    linesPreview = int(config['BLOG']['lines-preview'])
    previewText = ''
    previewFile = ''
    doMD = ''
    mdAsked = []
    rowLink = ''

    currentIndex = open(indexTemplate, 'r').read()

    c = conn.cursor()
    print('Rebuilding index...')

    # Get the posts form the database then build the HTML

    for row in c.execute('SELECT * FROM Posts ORDER BY ID DESC'):
        previewFile = open('source/posts/' + row[1] + '.html')
        previewText = previewFile.read()
        print('Adding ' + row[1] + ' to index...')
        if ':' in row[1]:
            rowLink = './' + row[1]
        else:
            rowLink = row[1]
        postList = postList + '<a href="' + rowLink + '.html"><h2>' + titles.convTitle(row[1].replace('-', ' ')) + '</h2></a>'
        postList = postList + '<div class="postDate">' + datetime.datetime.fromtimestamp(int(row[2])).strftime('%Y-%m-%d') + '</div>'
        postList = postList + '<div class="postPreview">'
        try:
            for x in range(0, linesPreview):
                if markdownSupport:
                    if row[1] not in mdAsked:
                        if config['BLOG']['markdown-prompt'] == 'true':
                            print('Do you want to encode Markdown for ' + row[1] + ' in the index preview? y/n')
                            mdAsked.append(row[1])
                            doMD = input('>').lower()
                            if doMD in ('y', 'yes'):
                                print('Using Markdown')
                                postList = postList + markdown.markdown(previewText.splitlines()[x])
                            else:
                                print('Not using Markdown')
                                postList = postList + previewText.splitlines()[x]
                        else:
                            postList = postList + markdown.markdown(previewText.splitlines()[x])
                else:
                    postList = postList + previewText.splitlines()[x]
        except IndexError:
            pass
        previewFile.close()
        if linesPreview > 0:
            postList = postList + '<a href="' + row[1] + '.html">...</a>'
        postList = postList + '</div>'

    content = currentIndex.replace('[{SITETITLE}]', config['BLOG']['title'])
    content = content.replace('[{SITEDESC}]', config['BLOG']['description'])
    content = content.replace('[{AUTHOR}]', config['SITE']['AUTHOR'])
    content = content.replace('[{NAVBAR}]', '')
    content = content.replace('[{SITEFOOTER}]', config['BLOG']['footer'])
    content = content.replace('[{BLOGINTRO}]', config['BLOG']['blog-intro'])
    content = content.replace('[{POSTLIST}]', postList)
    content = tgsocial.genSocial(config, content, 'post')

    try:
        shutil.rmtree('generated/blog/res/')
        os.mkdir('generated/blog/res/')
    except FileNotFoundError:
        pass
    try:
        createDelete.copytree('source/pages/res/', 'generated/blog/res/')
    except FileNotFoundError:
        pass
    except FileExistsError:
        pass

    f = open(indexProdFile, 'w').write(content)

    conn.close()

    return ('success', 'successfully rebuilt index')

def post(title, edit, config):
    # optionally edit, then, generate a blog post
    postExists = False
    if os.path.exists('source/posts/' + title + '.html'):
        postExists = True
    else:
        createDelete.createFile(title, 'post')
    editP = ''
    result = ''
    post = ''
    doMD = ''
    status = status = ('success', '')
    if not edit:
        date = getPostDate(title)
        date = datetime.datetime.fromtimestamp(int(date)).strftime('%Y-%m-%d')
    else:
        date = datetime.datetime.fromtimestamp(int(time.time())).strftime('%Y-%m-%d')
    if edit:
        # If recieved arg to edit the file
        if config['ETC']['no-editor'] == 'false':
            if os.getenv('EDITOR') is None:
                print('EDITOR environment variable not set. Edit source/posts/' + title + '.html, then press enter to continue.')
                input()
            else:
                editP = subprocess.Popen((os.getenv('EDITOR'), 'source/posts/' + title + '.html'))
                editP.wait()
        else:
            print('no-editor is set to true, waiting for you to edit manually')
            input()

    content = open('source/posts/' + title + '.html', 'r').read()
    if content == '':
        print('Edited file is empty, still save it? y/n')
        doSave = input('>').lower()
        if doSave in ('y', 'yes'):
            print('Saving')
        else:
            print('Not saving')
            return ('sucesss', 'Did not save')
    if markdownSupport:
        if config['BLOG']['markdown-prompt'] == 'true':
            print('Do you want to encode Markdown for this post? y/n')
            doMD = input('>').lower()
            if doMD in ('y', 'yes'):
                print('Using Markdown')
                content = markdown.markdown(content)
            else:
                print('Not using Markdown')
        else:
            content = markdown.markdown(content)

    template = open('source/blog-template.html', 'r').read()
    post = '[{PLUGINCONTENT}]' + tgplugins.events('blogEdit', template, config)
    post = post.replace('[{POSTTITLE}]', titles.convTitle(title.replace('-', ' ')))
    post = post.replace('[{SITETITLE}]', config['BLOG']['title'])
    post = post.replace('[{AUTHOR}]', config['SITE']['author'])
    post = post.replace('[{POSTCONTENT}]', content)
    post = post.replace('[{SITEFOOTER}]', config['BLOG']['footer'])
    post = post.replace('[{NAVBAR}]', '')
    post = post.replace('[{BLOGINTRO}]', config['BLOG']['blog-intro'])
    post = post.replace('[{SITEDESC}]', config['BLOG']['description'])
    post = post.replace('[{POSTDATE}]', date)
    post = post.replace('[{PLUGINCONTENT}]', '')
    post = tgsocial.genSocial(config, post, 'post')
    with open('generated/blog/' + title + '.html', 'w') as result:
        result.write(post)
    if status[1] != 'error':
        if not postExists:
            status = updatePostList(title, 'add')
            print(status[1])
            status = ('success', 'Successfully generated post: ' + title)
    return status

def rebuildImages(config, themeName):
    # Rebuild blog images
    print('Rebuilding images')
    if config['BLOG']['standalone'] == 'true':
        createDelete.copytree('source/theme/' + themeName + '/images/', 'generated/blog/images/')
    else:
        createDelete.copytree('source/theme/' + themeName + '/images/', 'generated/images/')
    createDelete.copytree('source/posts/images/', 'generated/blog/images/')
    return

def blog(blogCmd, config):
    # Main blog command handler
    postTitle = ''
    status = ('success', '') # Return status. 0 = error or not, 1 = return message
    indexError = False # If command doesn't get an argument, don't try to generate
    fileError = False
    formatType = ''
    themeName = config['BLOG']['theme']
    startRebuildTime = 0
    rebuildElapsed = 0
    draftConfirm = 'yes'
    file = '' # file for rebuilding all operation
    if blogCmd == 'edit':
        try:
            postTitle = sys.argv[3].replace('<', '&lt;').replace('>', '&gt;')
            # Strip spaces from posts & replace with dashes, but only if the post does not already exist to preserve backwards compatability
            if not os.path.exists('source/posts/' + postTitle + '.html'):
                postTitle = postTitle.replace(' ', '-')
        except IndexError:
            status = ('error', 'syntax: blog edit "post title"')
            indexError = True
        if not indexError:
            #try:
            if postTitle.lower() == 'index':
                status = ('error', 'You cannot name a blog post \'index\'.')
            else:
                status = post(postTitle, True, config)
                shutil.copyfile('source/theme/' + themeName + '/theme.css', 'generated/blog/theme.css')
                if status[0] == 'success':
                    print(status[1]) # Print the status message of the last operation, generating the post. In this case it should be similar to 'successfully generated post'
                    print('Attempting to rebuild blog index...')
                    status = rebuildIndex(config) # Rebuild the blog index page
                    print('Rebuilding RSS feed')
                    print('Rebuilding images')
                    rebuildImages(config, themeName)
                    tgrss.updateRSS(config)
    elif blogCmd == 'delete':
        try:
            postTitle = sys.argv[3]
        except IndexError:
            status = ('error', 'syntax: blog delete "post title"')
            indexError = True
        if not indexError:
            postTitle = postTitle.replace(' ', '-')
            tgplugins.events('blogDelete', postTitle, config)
            try:
                createDelete.deleteFile(postTitle, 'posts')
            except FileNotFoundError:
                status = ('error', 'Error encountered while deleting: ' + postTitle + ' reason: post does not exist')
                fileError = True
            except Exception as e:
                status = ('error', 'Error encountered while deleting: ' + postTitle + ': ' + str(e))
                fileError = True
            if not fileError:
                try:
                    status = updatePostList(postTitle, 'remove')
                except Exception as e:
                    status = ('error', 'error occured removing post from database: ' + str(e))
                status = rebuildIndex(config)
    elif blogCmd == 'list':
        print('Listing posts...')
        tgls.listFiles('posts')
    elif blogCmd == 'rebuild':
        # Rebuild all blog posts and assets
        tgplugins.events('blogRebuild', '', config)
        shutil.copyfile('source/theme/' + themeName + '/theme.css', 'generated/blog/theme.css')
        startRebuildTime = time.clock()
        print('Rebuilding images')
        rebuildImages(config, themeName)
        print('Rebuilding posts')
        for file in os.listdir('generated/blog/'):
            if file.endswith('.html'):
                if file != 'index.html':
                    file = file[:-5].strip()
                    try:
                        post(file, False, config)
                    except PermissionError:
                        print('Could not rebuild ' + file + '. Reason: Permission error')
                    except Exception as e:
                        print('Could not rebuild ' + file + '. Reason: ' + str(e))
        print('Rebuilding RSS feed')
        tgrss.updateRSS(config)
        print('Successfully rebuilt all posts.')
        # Rebuild index includes its own message about rebuilding
        rebuildIndex(config)
        rebuildElapsed = time.clock() - startRebuildTime
        status = ('success', 'Rebuild successful in ' + str(rebuildElapsed) + ' seconds')
    elif blogCmd == 'draft':
        try:
            draftCmd = sys.argv[3]
        except IndexError:
            draftCmd = None
            status = ('error', 'No draft command specified. Do help for more information')
        if draftCmd != None:
            try:
                draftArg = sys.argv[4].replace('/', '').replace('\\', '')
                draftArg = draftArg.replace(' ', '-')
            except IndexError:
                draftArg = None
            if draftCmd == 'list':
                tgplugins.events('draftList', '', config)
                tgls.listFiles('drafts')
                status = ('success', '')
            elif draftCmd == 'edit':
                tgplugins.events('draftEdit', '', config)
                if draftArg == None:
                    status = ('error', 'No draft to edit specified.')
                else:
                    if os.getenv('EDITOR') is None:
                        print('EDITOR environment variable not set. Edit source/posts/drafts/' + draftArg + '.html, then press enter to continue.')
                        input()
                    else:
                        editP = subprocess.Popen((os.getenv('EDITOR'), 'source/posts/drafts/' + draftArg + '.html'))
                        editP.wait()
            elif draftCmd == 'redraft':
                if draftArg == None:
                    status = ('error', 'No post to redraft specified.')
                else:
                    draftArg = draftArg + '.html'
                    if not os.path.exists('source/posts/' + draftArg):
                        status = ('error', 'That post does not exist')
                    else:
                        shutil.copyfile('source/posts/' + draftArg, 'source/posts/drafts/' + draftArg)
                        print('Successfully redrafted the post.')
            elif draftCmd == 'delete':
                tgplugins.events('draftDelete', '', config)
                if draftArg == None:
                    status = ('error', 'No draft to edit specified.')
                else:
                    if os.path.exists('source/posts/drafts/' + draftArg + '.html'):
                        os.remove('source/posts/drafts/' + draftArg + '.html')
                        status = ('success', 'Deleted draft')
                    else:
                        status = ('error', 'That draft already does not exist')
            elif draftCmd == 'publish':
                    tgplugins.events('draftPublish', '', config)
                    if draftArg == None:
                        status = ('error', 'No draft to publish specified.')
                    else:
                        if os.path.exists('source/posts/' + draftArg + '.html'):
                            print('A post by that name has already been published, would you like to overwrite it?')
                            draftConfirm = input('>').lower()
                            if not draftConfirm in ('y', 'yes'):
                                status = ('error', 'A post by that name has already been published, and will not be overwritten')
                        if draftConfirm in ('y', 'yes'):
                            if os.path.exists('source/posts/drafts/' + draftArg + '.html'):
                                updatePostList(draftArg, 'add')
                                shutil.copyfile('source/posts/drafts/' + draftArg + '.html', 'source/posts/' + draftArg + '.html')
                                status = post(draftArg, False, config)
                                shutil.copyfile('source/theme/' + themeName + '/theme.css', 'generated/blog/theme.css')
                                print(status[1])
                                status = rebuildIndex(config)
                                print(status[1])
                                rebuildImages(config, themeName)
                                status = tgrss.updateRSS(config)
                            else:
                                status = ('error', 'That draft does not exist')
    elif blogCmd == '':
        status = ('success', '')
    else:
        status = ('error', 'Invalid blog command')
    return status
