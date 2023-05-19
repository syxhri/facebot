import json, os

class JSON:
	def __init__(self):
		self.json = {}
	
	@classmethod
	def parse(self, data):
		if isinstance(data, str):
			try:
				data = json.loads(data)
			except Exception as e:
				raise JSONError(str(e))
		elif isinstance(data, dict):
			data = data
		else:
			raise JSONError('invalid data type')
		for k, v in data.items():
			setattr(self, k, v)
			self.json = data
	
	def __setitem__(self, key, value):
		self.json[key] = value
		setattr(self, key, value)
	
	def __getitem__(self, key):
		return self.json[key]
	
	def string(self):
		return json.dumps(self.json)

class JSONError(Exception):
	def __init__(self, message):
		self.message = message
	
	def __str__(self):
		return self.message

class QueryBuilder:
	def __init__(self):
		self.query = ''
		self.text = ''
	
	def add(self, key, value):
		if self.query.strip() == '':
			self.query += '{}={}'.format(key, value)
			self.text = self.query
		else:
			self.query += '&{}={}'.format(key, value)
			self.text = self.query
	
	def get(self, key):
		if self.query.strip() != '':
			queries = self.query.split('&')
			for query in queries:
				param = query.split('=')
				if key == param[0]:
					return param[1]
	
	def __str__(self):
		return self.query
	
	def __repr__(self):
		return self.query