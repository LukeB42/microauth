"""
This file presents the interfaces to users functions,
mainly listing them, verifying their rights and authenticating them.

Note that whenever authentication is attempted that an Event is created
and added to the database.
"""

import re
import datetime
import cStringIO
from flask import request
from flask.ext import restful
from flask.ext.restful import abort, reqparse

from sqlalchemy.orm import exc

from microauth import app, db
from microauth.models import *
from microauth.utils import gzipped, get
from microauth.resources.api_key import auth

class UserCollection(restful.Resource):

	@gzipped
	def get(self):
		key = auth()

		parser = reqparse.RequestParser()
		parser.add_argument("page", type=int, help="Current page number.")
		parser.add_argument("per_page", type=int, help="Items per page.")
		parser.add_argument("id", type=str, help="Unique ID")
		args = parser.parse_args()
		if args.page:
			if args.per_page:
				return [user.jsonify() for user in get(key, User, page=args.page, per_page=args.per_page)]
			return [user.jsonify() for user in get(key, User, page=args.page)]

		if args.id:
			user = get(key, User, ('uid', args.id))
			if not user: abort(404)
			return user.jsonify()

		return [user.jsonify() for user in get(key, User)]

	@gzipped
	def put(self):

		key = auth()

		parser = reqparse.RequestParser()
		parser.add_argument("username", type=str, help="Username of account", required=True)
		parser.add_argument("name", type=str, help="Name of account", required=True)
		parser.add_argument("email", type=str, help="Email address of account", required=True)
		parser.add_argument("password", type=str, help="Password of account", required=True)
		parser.add_argument("systemwide", type=bool, help="Determines whether this user has a parent API Key", default=None)
		args = parser.parse_args()

		msg = "%s may only contain alphanumeric characters, underscores, spaces and hyphens."
		if not re.match("^[\w\-\s]+$",args.username): abort(422, message=msg % "Usernames")
		if not re.match("^[\w\-\s]+$",args.name):     abort(422, message=msg % "Names")

		if get(key, User, ('username', args.username)):
			return {"message":"User already exists."}, 304

		try:
			user = User(args.username, args.email, args.name, args.password)
			if not key.systemwide or not args.systemwide: user.key = key
			db.session.add(user)
			db.session.commit()
		except exc.IntegrityError:
			abort(
				409,
				message="Username {0} or email {1} already in use.".format(args.username, args.email)
			)

		return user.jsonify(), 201

class UserResource(restful.Resource):

	def get(self, username):

		key = auth()
		user = get(key, User, ('username', username))

		if user is None:
			return {}, 404
		else:
			parser = reqparse.RequestParser()
			parser.add_argument(
				"can", type=str, help="Determine permission", required=False
			)
			args = parser.parse_args()
			if args.can:
				return user.can(args.can)
			return user.jsonify(with_groups=True)

	@gzipped
	def post(self, username):

		key = auth()
		user = get(key, User, ('username', username))

		parser = reqparse.RequestParser()
		parser.add_argument("username", type=str, help="Username of account")
		parser.add_argument("name", type=str, help="Name of account")
		parser.add_argument("email", type=str, help="Email address of account")
		parser.add_argument("key", type=str, help="Key to introduce the user to (requires systemwide:0)")
		parser.add_argument("password", type=str, help="Password of account")
		parser.add_argument("systemwide", type=bool, help="A global user", default=None)
		args = parser.parse_args()

		if user is None:
			abort(404, message="User {0} not found.".format(username))

		#
		# Attaching keyfiles to users. Modify here to do things like stegenography etc.
		#
		if 'keyfile' in request.files.keys():
			f = request.files['keyfile']
			print f
			print "Nonzero:", f.__nonzero__()
			tmp_buffer = cStringIO.StringIO(f.read())
			user.keyfile = tmp_buffer.read()
			db.session.add(user)
			db.session.commit()
			tmp_buffer.close()
			request.files['keyfile'].close()
			return {'message': 'User modified.'}

		if args.username:
			already = get(key, User, ('username', username))
			if already: abort(422, message="This username is already in use.")
			user.username = args.username

		if args.name: user.name = args.name
		if args.email: user.email = args.email
		if args.password: user.change_passwd(args.password)

		if key.systemwide:
			if args.systemwide:
				del user.key
			if args.systemwide == False:
				if key.name == app.config["MASTER_KEY_NAME"] and args.key:
					new_key = APIKey.query.filter(APIKey.name == app.config['MASTER_KEY_NAME']).first()
					new_key.users.append(user)
				else:
					key.users.append(user)

		db.session.commit()
		return user.jsonify()

	@gzipped
	def delete(self, username):
		key = auth()
		user = get(key, User, ('username', username))
		if not user.key and not key.global_del:
			abort(304, message="Your API key cannot delete systemwide users.")

		try:
			db.session.delete(user)
			db.session.commit()
		except exc.UnmappedInstanceError:
			pass

		return "", 204


class UserLogin(restful.Resource):

	def get(self, username):
		key = auth()
		user = get(key, User, ('username', username))

		if user is None:
			abort(404, message="User {0} not found.".format(username))

		parser = reqparse.RequestParser()
		parser.add_argument("password", type=str, help="Password of account", required=True)
		args = parser.parse_args()

		if user.verify_password(args.password):
			user.last_login = datetime.datetime.now()
			ev = Event(user=user, key=key, success=True)
			print ev
			db.session.add(ev)
			print db.session.dirty
			db.session.commit()
			return True
		ev = Event(user=user, key=key, success=False)
		db.session.add(ev)
		db.session.commit()
		return False



	def post(self, username):
		key = auth()
		user = get(key, User, ('username', username))

		if not user: abort(404)

		parser = reqparse.RequestParser()
		parser.add_argument("password", type=str, help="Password of account", default=None)
		args = parser.parse_args()

		if args.password:
			if user.verify_password(args.password):
				user.last_login = datetime.datetime.now()

				ev = Event(user=user, key=key, success=True)
				db.session.add(ev)
				db.session.commit()
				return True
			ev = Event(user=user, key=key, success=False)
			db.session.add(ev)
			db.session.commit()
			return False

		#
		# File-based authentication would be good for card readers
		# stegenographically embedded UIDs in cat macros or thumbprints.
		# (write output to a file-like object and send it over the wire)
		#

		if 'keyfile' in request.files.keys():
			f = request.files['keyfile']
			print f
			print "Nonzero:", f.__nonzero__()
			tmp_buffer = cStringIO.StringIO(f.read())
			request.files['keyfile'].close()
			if user.keyfile == tmp_buffer.read():
				tmp_buffer.close()
				user.last_login = datetime.datetime.now()
				ev = Event(user=user, key=key, success=True)
				db.session.add(ev)
				db.session.commit()
				return True
			tmp_buffer.close()
			ev = Event(user=user, key=key, success=False)
			db.session.add(ev)
			db.session.commit()
			return False

		return {},400
