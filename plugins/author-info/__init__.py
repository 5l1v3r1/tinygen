# Copyright 2017 Kevin Froman - MIT License - https://ChaosWebs.net/
# Plugin to add author information to blog posts
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
    print('blog edit event')
    data = data.replace('[{PLUGINCONTENT}]', '[{PLUGINCONTENT}]<span style="color: red;">made by kevin froman</span>')
    return data
