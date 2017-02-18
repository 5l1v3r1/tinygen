# Copyright 2017 Kevin Froman - MIT License - https://ChaosWebs.net/
import sys, os, configparser, createDelete, subprocess, shutil, sqlite3, time, datetime, tgsocial

markdownSupport = True
try:
    import markdown
except ImportError:
    markdownSupport = False

def getPostDate(title):
    conn = sqlite3.connect('.data/posts.db')
    c = conn.cursor()
    date = 0
    data = (title,)
    for row in c.execute('SELECT DATE FROM Posts where title=?', (data)):
        date = row[0]
    #status = ('success', 'Added post to database: ' + title)
    conn.close()
    return date

def updatePostList(title, add):
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
    indexTemplate = 'source/blog-index.html'
    indexProdFile = 'generated/blog/index.html'
    conn = sqlite3.connect('.data/posts.db')
    content = ''
    postList = ''
    linesPreview = int(config['BLOG']['lines-preview'])
    previewText = ''
    previewFile = ''

    currentIndex = open(indexTemplate, 'r').read()

    c = conn.cursor()
    print('Rebuilding index...')

    for row in c.execute('SELECT * FROM Posts ORDER BY ID DESC'):
        previewFile = open('source/posts/' + row[1] + '.html')
        previewText = previewFile.read()
        print('Adding ' + row[1] + ' to index...')
        postList = postList + '<a href="' + row[1] + '.html"><h2>' + row[1].title() + '</h2></a>'
        postList = postList + '<div class="postDate">' + datetime.datetime.fromtimestamp(int(row[2])).strftime('%Y-%m-%d') + '</div>'
        postList = postList + '<div class="postPreview">'
        try:
            for x in range(0, linesPreview):
                if markdownSupport:
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
    content = content.replace('[{POSTLIST}]', postList)
    content = tgsocial.genSocial(config, content, 'post')

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
    status = status = ('success', '')
    if not edit:
        date = getPostDate(title)
        date = datetime.datetime.fromtimestamp(int(date)).strftime('%Y-%m-%d')
    else:
        date = datetime.datetime.fromtimestamp(int(time.time())).strftime('%Y-%m-%d')
    if edit:
        # If recieved arg to edit the file
        try:
            editP = subprocess.Popen((os.getenv('EDITOR'), 'source/posts/' + title + '.html'))
            editP.wait()
        except TypeError:
            status = ('error', 'Unable to edit: ' + title + '. reason: editor environment variable is not set.')
    content = open('source/posts/' + title + '.html', 'r').read()
    if markdownSupport:
            content = markdown.markdown(content)

    template = open('source/blog-template.html', 'r').read()
    post = template.replace('[{POSTTITLE}]', title.title())
    post = post.replace('[{SITETITLE}]', config['BLOG']['title'])
    post = post.replace('[{AUTHOR}]', config['SITE']['author'])
    post = post.replace('[{POSTCONTENT}]', content)
    post = post.replace('[{SITEFOOTER}]', config['BLOG']['footer'])
    post = post.replace('[{NAVBAR}]', '')
    post = post.replace('[{SITEDESC}]', config['BLOG']['description'])
    post = post.replace('[{POSTDATE}]', date)
    post = tgsocial.genSocial(config, post, 'post')
    with open('generated/blog/' + title + '.html', 'w') as result:
        result.write(post)
    if status[1] != 'error':
        if not postExists:
            status = updatePostList(title, 'add')
            print(status[1])
            status = ('success', 'Successfully generated page: ' + title)
    return status
def blog(blogCmd, config):
    postTitle = ''
    status = ('success', '') # Return status. 0 = error or not, 1 = return message
    indexError = False # If command doesn't get an argument, don't try to generate
    fileError = False
    formatType = ''
    file = '' # file for rebuilding all operation
    if blogCmd == 'edit':
        try:
            postTitle = sys.argv[3].replace('<', '&lt;').replace('>', '&gt;')
        except IndexError:
            status = ('error', 'syntax: blog edit "post title"')
            indexError = True
        if not indexError:
            #try:
            if postTitle.lower() == 'index':
                status = ('error', 'You cannot name a blog post \'index\'.')
            else:
                status = post(postTitle, True, config)
                shutil.copyfile('source/theme/theme.css', 'generated/blog/theme.css')
                if status[0] == 'success':
                    print(status[1]) # Print the status message of the last operation, generating the post. In this case it should be similar to 'successfully generated post'
                    print('Attempting to rebuild blog index...')
                    status = rebuildIndex(config) # Rebuild the blog index page
    elif blogCmd == 'delete':
        try:
            postTitle = sys.argv[3]
        except IndexError:
            status = ('error', 'syntax: blog delete "post title"')
            indexError = True
        if not indexError:
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
    elif blogCmd == 'rebuild':
        shutil.copyfile('source/theme/theme.css', 'generated/blog/theme.css')
        try:
            shutil.rmtree('generated/images/')
        except FileNotFoundError:
            pass
        shutil.copytree('source/theme/images/', 'generated/images/')
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
        print('Successfully rebuilt all posts.')
        # Rebuild index includes its own message about rebuilding
        rebuildIndex(config)
        status = ('success', 'Rebuild successful')
    else:
        status = ('error', 'Invalid blog command')
    return status