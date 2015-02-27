import requests
import pprint
import json
import cmd
import os
os.environ['no_proxy'] = '127.0.0.1,localhost'
requests.packages.urllib3.disable_warnings()

class Client(object):
	def __init__(self, key, base_url, timeout=2.000):
		self.key = key
		self.base = base_url
		pp = pprint.PrettyPrinter(indent=4)
		self.p = pp.pprint
		self.verify = True
		self.username = None
		self.timeout = timeout

	def _send_request(self, url, type='GET', body={}, headers={}):
		headers['Authorization'] =  "Basic %s" % self.key
		url = self.base+url
		if type=='GET':
			resp = requests.get(url, verify=self.verify, headers=headers, timeout=self.timeout)
		elif type=='DELETE':
			resp = requests.delete(url, verify=self.verify, data=body, headers=headers, timeout=self.timeout)
		elif type=='PUT':
			resp = requests.put(url, verify=self.verify, data=body, headers=headers, timeout=self.timeout)
		elif type=='POST':
			resp = requests.post(url, verify=self.verify, data=body, headers=headers, timeout=self.timeout)
		try: return resp.json(), resp.status_code
		except: return {}, resp.status_code


	def get(url, body={}, headers={}):
		return self._send_request(url, body, headers)


	def put(url, body={}, headers={}):
		return self._send_request(url, type='PUT', body, headers)

	def post(url, body={}, headers={}):
		return self._send_request(url, type='POST', body, headers)

	def delete(url, body={}, headers={}):
		return self._send_request(url, type='DELETE', body, headers)

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

	def remote_user(self):
		if not self.username: raise Exception("No username attribute defined.")
		return self._send_request('/users/' + self.username)[0]

	def can(priv):
		if self.username:
			(resp, status) =  self._send_request('/users/%s?can=%s' % (self.username, priv))
			if status == 200: return resp
		raise Exception("No username attribute defined.")

	def __repr__(self):
		return "<API Client for $s>" % self.base
