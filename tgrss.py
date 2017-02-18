import configparser, sqlite3

def updateRSS(config):
    conn = sqlite3.connect('.data/posts.db')
    c = conn.cursor()
    rss = '''<?xml version="1.0" encoding="UTF-8" ?>
    <rss version="2.0">

    <channel>
    <title>''' + config['BLOG']['title'] + '''</title>
    <link>http://''' + config['SITE']['domain'] + '''</link>
    <description>''' + config['BLOG']['description'] + '''</description>'''
    for row in c.execute('SELECT * FROM Posts ORDER BY ID DESC'):
        rss = rss + '''<item>
            <title>''' + row[1].replace('<', '&lt;').replace('>', '&gt;') + '''</title>
            <link>http://''' + config['SITE']['domain'] + '''/''' + row[1] + '''/blog/''' + row[1] + '''.html</link>
            <description>''' + open('source/posts/' + row[1] + '.html', 'r').read().splitlines()[0].replace('<', '&lt;').replace('>', '&gt;') + '''</description></item>'''
    rss = rss + '</channel></rss>'
    open('generated/blog/feed.rss', 'w').write(rss)
    conn.close()
    return