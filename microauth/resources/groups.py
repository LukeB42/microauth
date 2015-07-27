"""
This file defines the interface to groups.
TODO: modifying a collection of groups in one call.
"""
import re
from microauth import db
from flask.ext import restful
from sqlalchemy import and_, or_
from microauth.utils import gzipped, get
from flask.ext.restful import abort, reqparse
from microauth.resources.api_key import auth
from microauth.models import Group, Priv, Acl, User


class GroupCollection(restful.Resource):
	@gzipped
	def get(self):
		key = auth()

		parser = reqparse.RequestParser()
		parser.add_argument("page", type=int, help="Current page number.")
		parser.add_argument("per_page", type=int, help="Items per page.")
		args = parser.parse_args()
		if args.page:
			if args.per_page:
				return [group.jsonify() for group in get(key, Group, page=args.page, per_page=args.per_page)]
			return [group.jsonify() for group in get(key, Group, page=args.page)]

		return [group.jsonify() for group in get(key, Group)]

	@gzipped
	def put(self):
		"Create a group on a given API key."
		key = auth()

		parser = reqparse.RequestParser()
		parser.add_argument("name", type=str, help="Name of the group to create.", required=True)
		parser.add_argument("systemwide", type=bool, help="Determines whether the group is systemwide.", default=False)
		args = parser.parse_args()

		groups = []
		response = {}
		msg = "Group names may only contained alphanumeric characters, underscores, spaces and hyphens."

		for n in args.name.split(','):
			if not re.match("^[\w\-\s]+$", n) or get(key, Group, ('name', n)): continue

			r = Group(name=n)
			if not key.systemwide or not args.systemwide:
				r.key = key			

			groups.append(r)
			db.session.add(r)

		if not groups:
			return {"message": "group(s) already present or contain(s) illegal characters."}, 304

		db.session.commit()
		return [r.jsonify() for r in groups], 201


	def post(self):
		key = auth()
		if not key.systemwide: abort(403)

		# TODO: Use a comma-separated list of names to modify multiple groups in one request.
		parser = reqparse.RequestParser()
		parser.add_argument("name", type=str, help="Name of groups.", required=True)
		parser.add_argument("systemwide", type=bool, help="Systemwide flag", required=True, default=None)
		args = parser.parse_args()

		groups = []

		for n in args.name.split(','):
			r = get(key, Group, ('name', n))
			if r:

				if args.systemwide == True:
					already = get(key,Group,('name',n), local=False)
					if len(already) > 1:
						abort(409, message="A systemwide group with this name already exists.")
					r.key.groups.remove(r)

				elif args.systemwide == False and key.global_del:
					r.key = key

				groups.append(r)
				db.session.add(r)

		db.session.commit()
		return [group.jsonify() for group in groups]


	@gzipped
	def delete(self):
		key = auth()

		parser = reqparse.RequestParser()
		parser.add_argument("name", type=str, help="Name of the group to delete.", required=True)
		args = parser.parse_args()

		groups = []


		for n in args.name.split(','):
			r = get(key, Group, ('name', n))
			if r and ((r.key == key) or key.global_del):
				groups.append(r)
				db.session.delete(r)

		if not groups: return {"message": "Unrecognized group(s)."}, 304
		db.session.commit()

		return {}, 204

class GroupResource(restful.Resource):

	@gzipped
	def get(self, name):
		key = auth()
		group = get(key, Group, ('name', name))
		try: return get(key, Group, ('name', name)).jsonify(with_users=True, with_privs=True)
		except: abort(404, message="Unrecognized group.")

	def post(self, name):
		key = auth()
		parser = reqparse.RequestParser()
		parser.add_argument("add", type=str, help="A list of users to add the group to.")
		parser.add_argument("remove", type=str, help="A list of users to remove the group from.")
		parser.add_argument("allow", type=str, help="A list of permissions to grant to the group.")
		parser.add_argument("deny", type=str, help="A list of permissions to deny the group.")
		parser.add_argument("revoke", type=str, help="A list of permissions to revoke from the group.")
		args = parser.parse_args()

		group = get(key,Group,('name',name))
		if not group: abort(404, message="Unrecognized group.")

		db.session.add(group)
		response = {}

		if args.add:
			users = []
			for n in args.add.split(','):
				user = get(key, User, ('username', n))
				if user:
					users.append(user)
					db.session.add(user)
					user.groups.append(group)
			if not users:
				response['add'] = {'message': "You didn't specify any recognisable users."}
			else:
				response['add'] = [u.username for u in users]

		if args.remove:
			users = []
			for n in args.remove.split(','):
				user = get(key, User, ('username', n))
				if user:
					users.append(user)
					db.session.add(user)
					user.groups.remove(group)
			if not users:
				response['remove'] = {'message': "You didn't specify any recognisable users."}
			else:
				response['remove'] = [u.username for u in users]

		if args.allow:
			allow_privs = []
			allow_acls  = []
			for n in args.allow.split(','):
				priv = get(key, Priv, ('name', n))
				if priv:
					allow_privs.append(priv)
					acl = Acl.query.filter(
						and_(Acl.priv == priv, Acl.group == group)
					).first()
					if not acl:
						acl = Acl()
						acl.group = group
						acl.priv = priv
					acl.allowed = True
					allow_acls.append(acl)
			if not allow_privs:
				response['allow'] = {'message': "You didn't specify any recognisable privileges."}
			if allow_acls:
				response['allow'] = [{acl.priv.name: acl.allowed}  for acl in allow_acls]

		if args.deny:
			deny_privs = []
			deny_acls  = []

			for n in args.deny.split(','):
				priv = get(key, Priv, ('name', n))
				if priv:
					deny_privs.append(priv)
					acl = Acl.query.filter(
						and_(Acl.priv == priv, Acl.group == group)
					).first()
					if not acl:
						acl = Acl()
						acl.group = group
						acl.priv = priv
					acl.allowed = False
					deny_acls.append(acl)
			if not deny_privs:
				response['deny'] = {'message': "You didn't specify any recognisable privileges."}
			if deny_acls:
				response['deny'] = [{acl.priv.name: acl.allowed}  for acl in deny_acls]

		if args.revoke and (key.global_del or group.key):
			revoke_privs = []
			revoke_acls  = []
			for n in args.revoke.split(','):
				priv = get(key, Priv, ('name', n))
				if priv:
					revoke_privs.append(priv)
					acl = Acl.query.filter(
						and_(Acl.priv == priv, Acl.group == group)
					).first()
					revoke_acls.append({acl.priv.name: acl.allowed})
					del acl.group
					del acl.priv
					db.session.delete(acl)
			if not revoke_privs:
				response['revoke'] =  {'message': "You didn't specify any recognisable privileges."}
			else:
				response['revoke'] = [acl for acl in revoke_acls]

		if db.session.dirty:
			db.session.commit()
		return response

#
# Classes defined after here are undocumented but behave as expected.
#

class GrantPrivs(restful.Resource):
	def post(self, name):
		key = auth()

		parser = reqparse.RequestParser()
		parser.add_argument("name", type=str, help="Name of the group to create.", required=True)
		args = parser.parse_args()

		group = get(key,Group,('name',name))
		if not group: abort(404, message="Unrecognized group.")

		privs = []
		acls=[]

		for n in args.name.split(','):
			priv = get(key, Priv, ('name', n))
			if priv:
				privs.append(priv)
				acl = Acl.query.filter(
					and_(Acl.priv == priv, Acl.group == group)
				).first()
				if not acl:
					acl = Acl()
					acl.group = group
					acl.priv = priv
				acl.allowed = True
				acls.append(acl)
		if not privs:
			return {'message': "You didn't specify any recognisable privileges."}, 304

		db.session.add(group)
		db.session.commit()
		return [{acl.priv.name: acl.allowed}  for acl in acls]

class DenyPrivs(restful.Resource):
	def post(self, name):
		key = auth()

		parser = reqparse.RequestParser()
		parser.add_argument("name", type=str, help="Name of the group to create.", required=True)
		args = parser.parse_args()

		group = get(key,Group,('name',name))
		if not group: abort(404, message="Unrecognized group.")

		privs = []
		acls=[]

		for n in args.name.split(','):
			priv = get(key, Priv, ('name', n))
			if priv:
				privs.append(priv)
				acl = Acl.query.filter(
					and_(Acl.priv == priv, Acl.group == group)
				).first()
				if not acl:
					acl = Acl()
					acl.group = group
					acl.priv = priv
				acl.allowed = False
				acls.append(acl)
		if not privs:
			return {'message': "You didn't specify any recognisable privileges."}, 304

		db.session.add(group)
		db.session.commit()
		return [{acl.priv.name: acl.allowed}  for acl in acls]

class RevokePrivs(restful.Resource):

	def post(self, name):
		key = auth()

		parser = reqparse.RequestParser()
		parser.add_argument("name", type=str, help="Name of the group to create.", required=True)
		args = parser.parse_args()

		group = get(key,Group,('name',name))
		if not group: abort(404, message="Unrecognized group.")

		if not group.key and not key.systemwide:
			return {"message": "Cannot revoke on global groups."}, 304
		privs = []
		acls=[]

		for n in args.name.split(','):
			priv = get(key, Priv, ('name', n))
			if priv and (key.global_del or group.key):
				privs.append(priv)
				acl = Acl.query.filter(
					and_(Acl.priv == priv, Acl.group == group)
				).first()
				acls.append({acl.priv.name: acl.allowed})
				db.session.delete(acl)
		if not privs:
			return {'message': "You didn't specify any recognisable privileges."}, 304

		db.session.add(group)
		db.session.commit()
		return acls

class GroupResourcePrivs(restful.Resource):
	def get(self, name):
		key = auth()
		group = get(key, Group, ('name', name))
		if not group: abort(404, message="Unrecognized group.")
		return group.jsonify(with_privs=True)['privileges']


class GroupResourceUsers(restful.Resource):
	def get(self, name):
		key = auth()
		group = get(key, Group, ('name', name))
		if not group: abort(404, message="Unrecognized group.")
		return group.jsonify(with_users=True)['users']
