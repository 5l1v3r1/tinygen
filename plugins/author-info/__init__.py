# Copyright 2017 Kevin Froman - MIT License - https://ChaosWebs.net/
# Plugin to add author information to blog posts
import configparser, os
def startup(data):
	return

def genPage(data):
	return

def rebuild(data):
	return

def deletePage(data):
	print('delete page event')
	return

def blogEdit(data):
	cfgFile = 'plugins/author-info/config.cfg'
	config = configparser.ConfigParser()
	config['Author-Info'] = {'name': 'anonymous', 'link': '', 'picture-url': ''}
	html = ''
	if not os.path.exists(cfgFile):
	    with open(cfgFile, 'w') as configfile:
	        config.write(configfile)
	config.read(cfgFile)

	# build author info html
	html = ''
	authorLink = config['Author-Info']['link']
	pic = config['Author-Info']['picture-url']
	if authorLink != '':
		if not authorLink.startswith('http://') and not authorLink.startswith('https://'):
			authorLink = 'http://' + authorLink
		authorLink = '<a style="color: black;" href="' + authorLink + '">' + config['Author-Info']['name'] + '</a>'
	else:
		authorLink = config['Author-Info']['name']
	if pic != '':
		if not pic.startswith('http://') and not pic.startswith('https://'):
			pic = 'http://' + pic
		pic = '<img src="' + pic + '" alt="author photo" style="max-width: 25%;">'
	else:
		pic = ''

	print('Adding author information to post...')
	data = data.replace('[{PLUGINCONTENT}]', '<div class="center" style="margin-bottom: -25%; margin-top: 2em; border-radius: 5px; padding: 5px;"><span>Proudly made by ' + authorLink + '</span><br><br>' + pic + '</div>')
	return data
