import configparser, sqlite3
markdownSupport = True
try:
    import markdown
except ImportError:
    markdownSupport = False

def updateRSS(config):
    conn = sqlite3.connect('.data/posts.db')
    c = conn.cursor()
    descText = ''
    rss = '''<?xml version="1.0" encoding="UTF-8" ?>
    <rss version="2.0">

    <channel>
    <title>''' + config['BLOG']['title'] + '''</title>
    <link>http://''' + config['SITE']['domain'] + '''</link>
    <description>''' + config['BLOG']['description'] + '''</description>'''
    for row in c.execute('SELECT * FROM Posts ORDER BY ID DESC'):
        if not markdownSupport:
            descText = open('source/posts/' + row[1] + '.html', 'r').read().splitlines()[0].replace('<', '&lt;').replace('>', '&gt;')
        else:
            descText = markdown.markdown(open('source/posts/' + row[1] + '.html', 'r').read().splitlines()[0]).replace('<', '&lt;').replace('>', '&gt;')
        rss = rss + '''<item>
        <title>''' + row[1].replace('<', '&lt;').replace('>', '&gt;').replace('-', ' ') + '''</title>
        <link>http://''' + config['SITE']['domain'] + '''blog/''' + row[1] + '''.html</link>
        <description>''' + descText + '''</description></item>'''
    rss = rss + '</channel></rss>'
    open('generated/blog/feed.rss', 'w').write(rss)
    conn.close()
    return