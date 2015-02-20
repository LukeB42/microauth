import re
from microauth import db
from flask.ext import restful
from sqlalchemy import and_, or_
from flask.ext.restful import abort, reqparse
from microauth.resources.api_key import auth
from microauth.resources.utils import gzipped, get
from microauth.resources.models import Role, Priv, Acl, User


#
# TODO: post request to move roles into the global namespace.
#
class RoleCollection(restful.Resource):
	@gzipped
	def get(self):
		key = auth()

		parser = reqparse.RequestParser()
		parser.add_argument("page", type=int, help="Current page number.")
		parser.add_argument("per_page", type=int, help="Items per page.")
		args = parser.parse_args()
		if args.page:
			if args.per_page:
				return [role.jsonify() for role in get(key, Role, page=args.page, per_page=args.per_page)]
			return [role.jsonify() for role in get(key, Role, page=args.page)]

		return [role.jsonify() for role in get(key, Role)]

	@gzipped
	def put(self):
		"Create a role on a given API key."
		key = auth()

		parser = reqparse.RequestParser()
		parser.add_argument("name", type=str, help="Name of the role to create.", required=True)
		parser.add_argument("systemwide", type=bool, help="Determines whether the role is systemwide.", default=False)
		args = parser.parse_args()

		roles = []
		response = {}
		msg = "Role names may only contained alphanumeric characters, underscores, spaces and hyphens."

		for n in args.name.split(','):
			if not re.match("^[\w\-\s]+$", n) or get(key, Role, ('name', n)): continue

			r = Role(name=n)
			if not key.systemwide or not args.systemwide:
				r.key = key			

			roles.append(r)
			db.session.add(r)

		if not roles:
			return {"message": "role(s) already present or contain(s) illegal characters."}, 304

		db.session.commit()
		return [r.jsonify() for r in roles], 201

	@gzipped
	def delete(self):
		key = auth()

		parser = reqparse.RequestParser()
		parser.add_argument("name", type=str, help="Name of the role to delete.", required=True)
		args = parser.parse_args()

		roles = []


		for n in args.name.split(','):
			r = get(key, Role, ('name', n))
			if r and ((r.key == key) or key.global_del):
				roles.append(r)
				db.session.delete(r)

		if not roles: return {"message": "Unrecognized role(s)."}, 304
		db.session.commit()

		return {}, 204

class RoleResource(restful.Resource):

	@gzipped
	def get(self, name):
		key = auth()
		role = get(key, Role, ('name', name))
		try: return get(key, Role, ('name', name)).jsonify(with_users=True, with_privs=True)
		except: abort(404, message="Unrecognized role.")

	def post(self, name):
		key = auth()
		parser = reqparse.RequestParser()
		parser.add_argument("add", type=str, help="A list of users to add the role to.")
		parser.add_argument("remove", type=str, help="A list of users to remove the role from.")
		parser.add_argument("allow", type=str, help="A list of permissions to grant to the role.")
		parser.add_argument("deny", type=str, help="A list of permissions to deny the role.")
		parser.add_argument("revoke", type=str, help="A list of permissions to revoke from the role.")
		args = parser.parse_args()

		role = get(key,Role,('name',name))
		if not role: abort(404, message="Unrecognized role.")

		db.session.add(role)
		response = {}

		if args.add:
			users = []
			for n in args.add.split(','):
				user = get(key, User, ('username', n))
				if user:
					users.append(user)
					db.session.add(user)
					user.roles.append(role)
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
					user.roles.remove(role)
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
						and_(Acl.priv == priv, Acl.role == role)
					).first()
					if not acl:
						acl = Acl()
						acl.role = role
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
						and_(Acl.priv == priv, Acl.role == role)
					).first()
					if not acl:
						acl = Acl()
						acl.role = role
						acl.priv = priv
					acl.allowed = False
					deny_acls.append(acl)
			if not deny_privs:
				response['deny'] = {'message': "You didn't specify any recognisable privileges."}
			if deny_acls:
				response['deny'] = [{acl.priv.name: acl.allowed}  for acl in deny_acls]

		if args.revoke and (key.global_del or role.key):
			revoke_privs = []
			revoke_acls  = []
			for n in args.revoke.split(','):
				priv = get(key, Priv, ('name', n))
				if priv:
					revoke_privs.append(priv)
					acl = Acl.query.filter(
						and_(Acl.priv == priv, Acl.role == role)
					).first()
					revoke_acls.append({acl.priv.name: acl.allowed})
					del acl.role
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
		parser.add_argument("name", type=str, help="Name of the role to create.", required=True)
		args = parser.parse_args()

		role = get(key,Role,('name',name))
		if not role: abort(404, message="Unrecognized role.")

		privs = []
		acls=[]

		for n in args.name.split(','):
			priv = get(key, Priv, ('name', n))
			if priv:
				privs.append(priv)
				acl = Acl.query.filter(
					and_(Acl.priv == priv, Acl.role == role)
				).first()
				if not acl:
					acl = Acl()
					acl.role = role
					acl.priv = priv
				acl.allowed = True
				acls.append(acl)
		if not privs:
			return {'message': "You didn't specify any recognisable privileges."}, 304

		db.session.add(role)
		db.session.commit()
		return [{acl.priv.name: acl.allowed}  for acl in acls]

class DenyPrivs(restful.Resource):
	def post(self, name):
		key = auth()

		parser = reqparse.RequestParser()
		parser.add_argument("name", type=str, help="Name of the role to create.", required=True)
		args = parser.parse_args()

		role = get(key,Role,('name',name))
		if not role: abort(404, message="Unrecognized role.")

		privs = []
		acls=[]

		for n in args.name.split(','):
			priv = get(key, Priv, ('name', n))
			if priv:
				privs.append(priv)
				acl = Acl.query.filter(
					and_(Acl.priv == priv, Acl.role == role)
				).first()
				if not acl:
					acl = Acl()
					acl.role = role
					acl.priv = priv
				acl.allowed = False
				acls.append(acl)
		if not privs:
			return {'message': "You didn't specify any recognisable privileges."}, 304

		db.session.add(role)
		db.session.commit()
		return [{acl.priv.name: acl.allowed}  for acl in acls]

class RevokePrivs(restful.Resource):

	def post(self, name):
		key = auth()

		parser = reqparse.RequestParser()
		parser.add_argument("name", type=str, help="Name of the role to create.", required=True)
		args = parser.parse_args()

		role = get(key,Role,('name',name))
		if not role: abort(404, message="Unrecognized role.")

		if not role.key and not key.systemwide:
			return {"message": "Cannot revoke on global roles."}, 304
		privs = []
		acls=[]

		for n in args.name.split(','):
			priv = get(key, Priv, ('name', n))
			if priv and (key.global_del or role.key):
				privs.append(priv)
				acl = Acl.query.filter(
					and_(Acl.priv == priv, Acl.role == role)
				).first()
				acls.append({acl.priv.name: acl.allowed})
				db.session.delete(acl)
		if not privs:
			return {'message': "You didn't specify any recognisable privileges."}, 304

		db.session.add(role)
		db.session.commit()
		return acls
