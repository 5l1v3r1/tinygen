import sys, os, configparser, createDelete, subprocess, shutil, sqlite3, time
# Copyright 2017 Kevin Froman - MIT License - https://ChaosWebs.net/

def updatePostList(title, add):
    # add is either 'add' or 'remove'
    conn = sqlite3.connect('.data/posts.db')
    c = conn.cursor()
    if add == 'add':
        data = (title, str(int(time.time())))
        c.execute('INSERT INTO Posts (title, date) Values (?,?)', (data))
        status = ('success', 'Added post to database: ' + title)
    elif add == 'remove':
        data = (title)
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
    linesPreview = config['BLOG']['lines-preview']

    currentIndex = open(indexTemplate, 'r').read()

    c = conn.cursor()
    print('Rebuilding index...')


    for row in c.execute('SELECT * FROM Posts ORDER BY ID DESC'):
        print('Adding ' + row[1] + ' to index...')
        postList = postList + '<a href="' + row[1] + '.html"><h1>' + row[1] + '</h1></a>'

    content = currentIndex.replace('[{SITETITLE}]', config['BLOG']['title'])
    content = content.replace('[{SITEDESC}]', config['BLOG']['description'])
    content = content.replace('[{AUTHOR}]', config['SITE']['AUTHOR'])
    content = content.replace('[{NAVBAR}]', '')
    content = content.replace('[{SITEFOOTER}]', config['BLOG']['footer'])
    content = content.replace('[{POSTLIST}]', postList)

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
    status = ''
    if edit:
        # If recieved arg to edit the file
        editP = subprocess.Popen((os.getenv('EDITOR'), 'source/posts/' + title + '.html'))
        editP.wait()
    content = open('source/posts/' + title + '.html', 'r').read()
    template = open('source/blog-template.html', 'r').read()
    post = template.replace('[{POSTTITLE}]', title.title())
    post = post.replace('[{SITETITLE}]', config['BLOG']['title'])
    post = post.replace('[{AUTHOR}]', config['SITE']['author'])
    post = post.replace('[{POSTCONTENT}]', content)
    post = post.replace('[{SITEFOOTER}]', config['BLOG']['footer'])
    content = content.replace('[{NAVBAR}]', '')
    post = post.replace('[{SITEDESC}]', config['BLOG']['description'])
    with open('generated/blog/' + title + '.html', 'w') as result:
        result.write(post)

    if not postExists:
        status = updatePostList(title, 'add')


    return ('success', 'Successfully generated page: ' + title)
def blog(blogCmd, config):
    postTitle = ''
    status = ('success', '') # Return status. 0 = error or not, 1 = return message
    indexError = False # If command doesn't get an argument, don't try to generate
    fileError = False
    file = '' # file for rebuilding all operation
    if blogCmd == 'edit':
        try:
            postTitle = sys.argv[3]
        except IndexError:
            status = ('error', 'syntax: blog edit "post title"')
            indexError = True
        if not indexError:
            #try:
            status = post(postTitle, True, config)
            shutil.copyfile('source/theme.css', 'generated/blog/theme.css')
            if status[0] == 'success':
                print(status[1]) # Print the status message of the last operation, generating the post. In this case it should be similar to 'successfully generated post'
                print('Attempting to rebuild blog index...')
                status = rebuildIndex(config) # Rebuild the blog index page
            #except:
                #status = ('error', 'An unknown error occured')
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
                status = ('error', 'Error encountered while deleting: ' + postTitle + ' reason: File does not exist')
                fileError = True
            except:
                status = ('error', 'Unknown error encountered while deleting: ' + postTitle)
                fileError = True
            if not fileError:
                try:
                    status = updatePostList(postTitle, 'remove')
                except:
                    status = ('error', 'unknown error occured removing post from database')
    elif blogCmd == 'rebuild':
        print('Rebuilding posts')
        for file in os.listdir('generated/blog/'):
            if file.endswith('.html'):
                if file != 'index.html':
                    file = file[:-5].strip().replace(' ','')
                    post(file, False, config)
        print('Successfully rebuilt all posts.')
        # Rebuild index includes its own message about rebuilding
        rebuildIndex(config)
        status = ('success', 'Rebuild successful')
    else:
        status = ('error', 'Invalid blog command')
    return status