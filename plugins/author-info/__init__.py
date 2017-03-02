# Copyright 2017 Kevin Froman - MIT License - https://ChaosWebs.net/
# Plugin to add author information to blog posts
import configparser, os
def startup(data):
	print('Running author info plugin')
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
	config['Author Info'] = {'name': 'anonymous', 'link': '', 'picture url': ''}
	print('Adding author information to post...')
	data = data.replace('[{PLUGINCONTENT}]', '<span style="color: red;">made by kevin froman</span>')
	return data
