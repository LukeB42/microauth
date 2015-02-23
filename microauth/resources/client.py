import requests
import pprint
import json
import cmd
import os
os.environ['no_proxy'] = '127.0.0.1,localhost'
requests.packages.urllib3.disable_warnings()

class Client(object):
	def __init__(self, key, base_url):
		self.key = key
		self.base = base_url
		pp = pprint.PrettyPrinter(indent=4)
		self.p = pp.pprint
		self.verify = True

	def _send_request(self, url, type='GET', body={}, headers={}):
		headers['Authorization'] =  "Basic %s" % self.key
		url = self.base+url
		if type=='GET':
			resp = requests.get(url, verify=self.verify, headers=headers)
		elif type=='DELETE':
			resp = requests.delete(url, verify=self.verify, data=body, headers=headers)
		elif type=='PUT':
			resp = requests.put(url, verify=self.verify, data=body, headers=headers)
		elif type=='POST':
			resp = requests.post(url, verify=self.verify, data=body, headers=headers)
		try: return resp.json(), resp.status_code
		except: return {}, resp.status_code

	def pp(self, url, type='GET', body={}, headers={}):
		self.p(self._send_request(url, type, body, headers))

	def keys(self, type='GET', body={}, headers={}):
		return self._send_request("keys", type, body, headers)

	def users(self, type='GET', body={}, headers={}):
		return self._send_request("users", type, body, headers)

	def roles(self, type='GET', body={}, headers={}):
		return self._send_request("roles", type, body, headers)

	def privs(self, type='GET', body={}, headers={}):
		return self._send_request("privs", type, body, headers)

	def __repr__(self):
		return "<API Client for $s>" % self.base
