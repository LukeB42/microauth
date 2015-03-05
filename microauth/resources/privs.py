import re
from microauth import db
from sqlalchemy import and_
from flask.ext import restful
from flask.ext.restful import abort, reqparse
from microauth.resources.models import Priv, Acl, Role
from microauth.resources.utils import gzipped, get
from microauth.resources.api_key import auth

class PrivResource(restful.Resource):
	def get(self, name):
		key = auth()
		priv = get(key, Priv, ('name',name))
		if priv: return priv.jsonify()
		abort(404)

class PrivCollection(restful.Resource):

	@gzipped
	def get(self, name=None):
		key = auth()

		parser = reqparse.RequestParser()
		parser.add_argument("page", type=int, help="Current page number.")
		parser.add_argument("per_page", type=int, help="Items per page.")
		args = parser.parse_args()
		if args.page:
			if args.per_page:
				return [priv.jsonify() for priv in get(key, Priv, page=args.page, per_page=args.per_page)]
			return [priv.jsonify() for priv in get(key, Priv, page=args.page)]

		privs = get(key,Priv)
		return [priv.jsonify() for priv in privs]

	def put(self):
		key = auth()

		parser = reqparse.RequestParser()
		parser.add_argument("name", type=str, help="Name of the privilege to create.", required=True)
		parser.add_argument("systemwide", type=bool, help="Determines whether the privilege is systemwide.", default=False)
		args = parser.parse_args()

		msg="Privilege names can only contain any combination of alphanumeric characters, hyphens, underscores and whitespace."

		privs=[]
		names = args.name.split(',')
		for name in names:
			if not re.match("^[\w\-\s,]+$",name): abort(422, message=msg)

			priv = get(key, Priv, ('name',name))
			if priv: continue

			priv = Priv(name=name)
			if not key.systemwide or not args.systemwide:
				key.privs.append(priv)
			privs.append(priv)
			db.session.add(priv)

		if not privs: return [],304
		db.session.commit()
		return [priv.jsonify() for priv in privs],201

	def post(self):
		key = auth()

		parser = reqparse.RequestParser()
		parser.add_argument("name", type=str, help="Name of the privilege to create.", required=True)
		parser.add_argument("systemwide", type=bool, help="Determines whether the privilege is systemwide.", required=True, default=None)
		args = parser.parse_args()

		msg="Privilege names may only contain alphanumeric characters, hyphens, underscores and whitespace."
		if not re.match("^[\w\-\s,]+$",args.name): abort(422, message=msg)

		privs=[]
		names = args.name.split(',')
		for name in names:
			priv = get(key, Priv, ('name',name))
			if priv: privs.append(priv)
		if not privs: return abort(404)

		# Be careful with reparenting global privs to the local scope, as they disappear from
		# other applications ACLs.
		for priv in privs:
			if key.systemwide and key.global_del and args.systemwide == False and not priv.key:
				key.privs.append(priv)
			elif args.systemwide == True and key.systemwide:
				key.privs.remove(priv)

		db.session.add(priv)
		db.session.commit()
		return [priv.jsonify() for priv in privs]

	def delete(self):
		key = auth()

		parser = reqparse.RequestParser()
		parser.add_argument("name", type=str, help="Name of the privilege to delete.", required=True)
		args = parser.parse_args()

		privs=[]
		names = args.name.split(',')
		for name in names:
			priv = get(key, Priv, ('name',name))
			if priv: privs.append(priv)
		if not privs: return abort(404)

		for priv in privs:
			if not priv.key and not key.global_del: continue
			for acl in priv.roles:
				db.session.delete(acl)
			db.session.delete(priv)

		db.session.commit()
		
		return {}, 204

