# Copyright 2017 Kevin Froman - MIT License - https://ChaosWebs.net/
# Plugin example
def startup(data):
	print("Hello from the hello world plugin!")
	return

def genPage(data):
	data = data.replace('[{CONTENT}]', '[{CONTENT}]<h1 style="color: red;">Hello World Plugin</h1>')
	return data

def rebuild(data):
	print('rebuild event')
	return

def deletePage(data):
	print('delete page event')
	return

def blogEdit(data):
	print('blog edit event')
	return

def blogDelete(data):
	print('blog delete event')
	return

def blogRebuild(data):
	print('blog rebuild event')
	return

def myName():
	return 'helloworld'

class Commands:
	def commands(*args):
		argCount = 0 # We do this to skip the first argument, which is just 'helloworld'
		for g in args:
			if argCount > 1:
				print('Greetings: ' + g)
			argCount = argCount + 1
