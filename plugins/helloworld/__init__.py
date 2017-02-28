def startup(data):
	print("Hello from the hello world plugin!")
	return

def genPage(data):
	data = data.replace('[{CONTENT}]', '[{CONTENT}]<h1 style="color: red;">Hello World Plugin</h1>')
	print('data ' + data)
	return data