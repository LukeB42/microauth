"""
This file models data for storage in a database,
You may want to check the .jsonify() methods too.
"""
# "build your application with a local key, and when it's ready, enable system-wide"

import os
import json
import bcrypt
from microauth import app, db
from sqlalchemy import and_, or_
from microauth.resources.utils import uid
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

class APIKey(db.Model):
	__tablename__ = 'api_keys'
	id         = db.Column(db.Integer, primary_key=True)
	name       = db.Column(db.String(80))
	key        = db.Column(db.String(120))	
	active     = db.Column(db.Boolean())
	created    = db.Column(db.DateTime(), default=db.func.now())
	systemwide = db.Column(db.Boolean())
	global_del = db.Column(db.Boolean())
	users = db.relationship("User", backref="key")
	privs = db.relationship("Priv", backref="key")
	roles = db.relationship("Role", backref="key")

	def generate_key_str(self):
		return bcrypt.hashpw(os.urandom(20),
			bcrypt.gensalt(app.config["BCRYPT_ROUNDS"])).decode()

	def __repr__(self):
		return '<APIKey "%s">' % self.name

	def jsonify(self, with_objs=False, with_key_str=False):
		response = {}
		response['name']       = self.name
		if with_key_str:
			response['apikey'] = self.key
		response['active'] = self.active
		response['systemwide'] = self.systemwide
		if with_objs:
			users = []
			roles = []
			privs = []
			for i in self.users: users.append(i.username)
			for i in self.roles: roles.append(i.name)
			for i in self.privs: privs.append(i.name)
			response['users']      = users
			response['roles']      = roles
			response['privileges'] = privs
		if self.systemwide:
			response['global_delete'] = self.global_del
		return response

# http://docs.sqlalchemy.org/en/rel_0_9/orm/extensions/associationproxy.html
class Acl(db.Model):
	__tablename__ = 'acl'
	priv_id = db.Column(db.Integer(), db.ForeignKey('privs.id'), primary_key=True)
	role_id = db.Column(db.Integer(), db.ForeignKey('roles.id'), primary_key=True)
	created = db.Column(db.DateTime(), default=db.func.now())
	allowed = db.Column(db.Boolean())	
	priv	= db.relationship('Priv', backref="roles")

	def __repr__(self):
		if not self.priv or not self.role:
			return "<Acl>"
		a = "deny"
		if self.allowed: a = "allow"

		if self.role and self.role.key:
			return "<Acl %s/%s/%s:%s>" % (self.role.key.name, self.role.name, self.priv.name, a)
		return "<Acl */%s/%s:%s>" % (self.role.name, self.priv.name, a)

class Priv(db.Model):
	__tablename__ = 'privs'
	id      = db.Column(db.Integer, primary_key=True)
	name    = db.Column(db.String(20))
	key_id  = db.Column(db.Integer(), db.ForeignKey("api_keys.id"))
	created = db.Column(db.DateTime(), default=db.func.now())

	def __repr__(self):
		return "<Priv %s>" % self.name

	def jsonify(self):
		response =  {'name': self.name, 'systemwide':True}
		if self.key:
			response['systemwide'] = False
			response['parent_key'] = self.key.name
		if self.created:
			response['created'] = self.created.strftime("%A, %d. %B %Y %I:%M%p")
		return response

user_roles = db.Table('user_roles',
	db.Column('role_id', db.Integer(), db.ForeignKey('roles.id')),
	db.Column('user_id', db.Integer(), db.ForeignKey('users.id'))
)

class Role(db.Model):
	__tablename__ = 'roles'
	id      = db.Column(db.Integer, primary_key=True)
	name    = db.Column(db.String(20))
	users   = db.relationship("User", backref="roles")
	key_id  = db.Column(db.Integer(), db.ForeignKey("api_keys.id"))
	users   = db.relationship("User", secondary=user_roles, backref="roles")
	privs   = db.relationship("Acl", backref="role")
	created = db.Column(db.DateTime(), default=db.func.now())

	def add_parent(self, parent):
		self.parents.append(parent)

	def add_parents(self, *parents):
		for parent in parents:
			self.add_parent(parent)

	@staticmethod
	def get_by_name(name):
		return Role.query.filter_by(name=name).first()

	def __repr__(self):
		return "<Role %s>" % self.name

	def jsonify(self, with_users=False, with_privs=False):
		response = {'name': self.name,
		'systemwide': True}
		if self.created:
			response['created'] = self.created.strftime("%A, %d. %B %Y %I:%M%p")
		if self.key:
			response['systemwide'] = False
			response['parent_key'] = self.key.name
		if with_users:
			users = []
			for i in self.users: users.append(i.username)
			response['users'] = users
		if with_privs:
			privs = []
			for i in self.privs: privs.append({i.priv.name: i.allowed})
			response['privileges'] = privs
		return response


class User(db.Model):
	__tablename__ = 'users'
	id          = db.Column(db.Integer, primary_key=True)	
	username    = db.Column(db.String(15))                # The username (required)
	email       = db.Column(db.String(20), unique=True)   # The email address (required)
	name        = db.Column(db.String(30))                # The name of the user (required)
	uid         = db.Column(db.String(20), default=uid()) # An immutable unique ID so that usernames can be changed
	preferences = db.Column(db.PickleType())              # A field for storing json (cannot be queried directly)
	password    = db.Column(db.String(30))                # Password (required)
	keyfile     = db.Column(db.LargeBinary(2*1000000000)) # Binary object for embedding keyfiles. (2gb default)
	key_id      = db.Column(db.Integer(), db.ForeignKey("api_keys.id"))
	created     = db.Column(db.DateTime(), default=db.func.now())
	last_login  = db.Column(db.DateTime())

	def __init__(self, username, email, name, password, extra={}, keyfile=None):
		self.username = username
		self.email = email
		self.name = name
		self.keyfile = keyfile
		self.extra = json.dumps(extra) # app-specific fields
		self.password = bcrypt.hashpw(
			password.encode(), bcrypt.gensalt(app.config["BCRYPT_ROUNDS"])
		).decode()

	def jsonify(self, with_roles=False, with_preferences=False):
		response = {
			"username": self.username,
			"name": self.name,
			"email": self.email,
			"systemwide": False,
			"id": self.uid,
			"created": self.created.strftime("%A, %d. %B %Y %I:%M%p")
		}
		if self.last_login:
			response['last_login'] = self.last_login.strftime("%A, %d. %B %Y %I:%M%p")
		if with_preferences and type(self.preferences) == dict:
			response['preferences'] = self.preferenes
		if not self.key: response['systemwide'] = True
		if with_roles:
			roles = []
			for r in self.roles: roles.append(r.name)
			response['roles'] = roles
		return response

	def change_passwd(self, password):
		self.password = bcrypt.hashpw(password.encode(),
			bcrypt.gensalt(app.config["BCRYPT_ROUNDS"])).decode()


	def verify_password(self, password):
		if bcrypt.hashpw(
			password.encode(), self.password.encode()
		) == self.password.encode():
			return True
		else:
			return False

	def can(self, priv):
		# Make use of self.key.systemwide to determine whether keyless privs count.
		permission = []
		priv = Priv.query.filter(Priv.name == priv).first()
		if priv:
			for r in self.roles:
				for p in r.privs:
					if p.priv_id == priv.id:
						permission.append(p.allowed)
			if True in permission: return True
		else: return None
		return False

	def __hash__(self):
		return hash(self.username)

	def __eq__(self, other):
		return self.id == other.id

	def __repr__(self):
		return "<User %s>" % self.username
