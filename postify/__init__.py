import os, json, re, requests
from .utils import JSON, QueryBuilder
from urllib.parse import urlparse as parse_url
from urllib.parse import urlencode as encode_url
from http.client import HTTPConnection, HTTPSConnection

class NetError(Exception):
	def __init__(self, message):
		self.message = message
	
	def __str__(self):
		return self.message
	
	def __repr__(self):
		return '<NetError [{}]>'.format(self.message)

class Fetch:
	def __init__(self, **kwargs):
		self.kwargs = kwargs
	
	def __repr__(self):
		kwargs = self.kwargs.copy()
		kwargs['method'] = kwargs.get('method') or 'GET'
		method = kwargs['method']
		args = '<Fetch [{}]; '.format(method)
		for key, value in self.kwargs.items():
			if args == '<Fetch [{}]; '.format(method):
				args += '{}={}'.format(key, value)
			else:
				args += ', {}={}'.format(key, value)
		return args + '>'
	
	def validate(self, url):
		regex = re.compile(
				r'^https?://'
				r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
				r'localhost|'
				r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
				r'(?::\d+)?'
				r'(?:/?|[/?]\S+)$', re.IGNORECASE
		)
		return bool(regex.match(url))
	
	def send(self, url=None, method='GET'):
		try:
			url = url or self.kwargs.get('url')
			method = self.kwargs.get('method') or method
			self.kwargs['url'] = url
			self.kwargs['method'] = method
			if url is None:
				raise NetError('url not defined')
			if method == 'GET':
				del self.kwargs['method']
				res = requests.get(**self.kwargs)
				self.res = res
				return Result(self)
			elif method == 'POST':
				del self.kwargs['method']
				res = requests.post(**self.kwargs)
				self.res = res
				return Result(self)
			elif method == 'PUT':
				del self.kwargs['method']
				res = requests.put(**self.kwargs)
				self.res = res
				return Result(self)
			elif method == 'DELETE':
				del self.kwargs['method']
				res = requests.delete(**self.kwargs)
				self.res = res
				return Result(self)
			elif method == 'PATCH':
				del self.kwargs['method']
				res = requests.patch(**self.kwargs)
				self.res = res
				return Result(self)
			else:
				raise NetError('method \'{}\' not supported'.format(method))
		except Exception as e:
			raise NetError(str(e))
	
	@property
	def url(self):
		return self.kwargs.get('url')
	
	@property
	def fine(self):
		return self.res.ok
	
	@property
	def binary(self):
		return self.res.content
	
	@property
	def urls(self):
		return self.res.links
	
	@property
	def raw(self):
		return self.res.text
	
	@property
	def status_code(self):
		return self.res.status_code
	
	@property
	def json(self):
		return self.jsonify()
	
	def jsonify(self):
		return json.loads(self.res.text)

class Result:
	def __init__(self, request: Fetch):
		self.fetch = request
	
	def __repr__(self):
		args = '<Result [{}]>'.format(self.status_code)
		return args
	
	@property
	def fine(self):
		return self.fetch.fine
	
	@property
	def binary(self):
		return self.fetch.binary
	
	@property
	def urls(self):
		return self.fetch.urls
	
	@property
	def raw(self):
		return self.fetch.raw
	
	@property
	def status_code(self):
		return self.fetch.status_code
	
	@property
	def json(self):
		return self.jsonify()
	
	def jsonify(self):
		return json.loads(self.raw)

def get(url, **kwargs):
	kwargs['url'] = url
	kwargs['method'] = 'GET'
	req = Fetch(**kwargs)
	res = req.send()
	return res

def post(url, **kwargs):
	kwargs['url'] = url
	kwargs['method'] = 'POST'
	req = Fetch(**kwargs)
	res = req.send()
	return res

def put(url, **kwargs):
	kwargs['url'] = url
	kwargs['method'] = 'PUT'
	req = Fetch(**kwargs)
	res = req.send()
	return res

def delete(url, **kwargs):
	kwargs['url'] = url
	kwargs['method'] = 'DELETE'
	req = Fetch(**kwargs)
	res = req.send()
	return res

def patch(url, **kwargs):
	kwargs['url'] = url
	kwargs['method'] = 'PATCH'
	req = Fetch(**kwargs)
	res = req.send()
	return res
