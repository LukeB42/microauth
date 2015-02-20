#!/usr/bin/env python
import requests
import pprint
import json
import cmd
import os
from microauth.resources.models import APIKey
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
			resp = requests.delete(url, verify=self.verify, headers=headers)
		elif type=='PUT':
			resp = requests.put(url, verify=self.verify, data=body, headers=headers)
		elif type=='POST':
			resp = requests.POST(url, verify=self.verify, data=body, headers=headers)
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

class repl(cmd.Cmd):

	prompt = "> "		
	intro = "Microauth repl."
	ruler = '-'

	def do_setkey(self,key):
		if key:
			self.c.key = key
			print 'Changed active API key to "%s"' % key
		else:
			print "Usage: setkey <key>"

	def do_getkey(self,line):
		print self.c.key

	def do_get(self,line):
		self.c.pp(line)

	def do_put(self,line):
		self.c.pp(line, 'PUT')

	def do_post(self,line):
		self.c.pp(line,'POST')

	def do_delete(self,line):
		self.c.pp(line, 'DELETE')

	def do_EOF(self,line):
		return True

	def postloop(self):
		print

if __name__ == "__main__":
	r = repl()
	r.c = Client('','https://localhost:7789/v1/')
	r.c.key = APIKey.query.first().key
	r.c.verify = False
	r.cmdloop()
