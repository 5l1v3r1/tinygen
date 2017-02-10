import sys, os, configparser, createDelete, subprocess, shutil
# Copyright 2017 Kevin Froman - MIT License - https://ChaosWebs.net/

def rebuildIndex(config):
    return ('success', 'successfully rebuilt index')

def post(title, edit, config):
    # optionally edit, then, generate a blog post
    createDelete.createFile(title, 'post')
    editP = ''
    result = ''
    post = ''
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
    #post = post.replace('[{NAVBAR}]', navBar)
    post = post.replace('[{SITEDESC}]', config['BLOG']['description'])
    with open('generated/blog/' + title + '.html', 'w') as result:
        result.write(post)
    shutil.copyfile('source/theme.css', 'generated/blog/theme.css')
    return ('success', 'Successfully generated page: ' + title)
def blog(blogCmd, config):
    postTitle = ''
    status = ('success', '') # Return status. 0 = error or not, 1 = return message
    indexError = False # If command doesn't get an argument, don't try to generate
    if blogCmd == 'edit':
        try:
            postTitle = sys.argv[3]
        except IndexError:
            status = ('error', 'syntax: blog edit "post title"')
            indexError = True
        if not indexError:
            try:
                status = post(postTitle, True, config)
                if status[0] == 'success':
                    print(status[1]) # Print the status message of the last operation, generating the post. In this case it should be similar to 'successfully generated post'
                    print('Attempting to rebuild blog index...')
                    status = rebuildIndex(config) # Rebuild the blog index page
            except:
                status = ('error', 'An unknown error occured')
    else:
        status = ('error', 'Invalid blog command')
    return status