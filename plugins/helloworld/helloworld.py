class helloworld:
	def startup(data):
		print("this is a test hello world")
		return ''
	def generatePage(data):
		print('generate fired')
		try:
			genn = data.replace('[{CONTENT}]', '[{CONTENT}]<br><h1 style="color: red;">Hello World Plugin</h1>')
		except:
			print("FUCK")
		print("FIRING MY GENERATE SITE LASERS")
		#print(config['SITE']['title'])
		return genn