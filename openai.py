import requests, json, os

class GPT:
	def __init__(self, apikey, id='GPT-3.5'):
		self.apikey = apikey
		self.id = id
		self.error = None
	
	def chat(self, message):
		res = requests.get('https://api.syhr.my.id/openai/chatgpt/?apikey={}&id={}&chat={}'.format(self.apikey, self.id, message))
		if res.ok:
			self.response = res.json()['message']
		else:
			self.response = res.text

class DALL_E:
	def __init__(self, apikey):
		self.apikey = apikey
	
	def generate(self, prompt):
		path = os.getcwd()
		res = requests.get(f'https://api.syhr.my.id/openai/dall_e/?apikey={}&q={}'.format(self.apikey, prompt))
		"""if res.ok:
			res = requests.get('https://api.syhr.my.id/openai/dall_e/image.jpg')"""
		if res.ok:
			open(f'{path}/image.jpg', 'wb').write(res.content)
			self.image_path = '{}/image.jpg'.format(path)
			self.image = open(f'{}/image.jpg', 'rb'.format(path))
		else:
			self.error = res.text
