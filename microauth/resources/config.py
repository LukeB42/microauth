"""
This module lets Microauth-Login instances obtain their settings from a central
source.
"""
from microauth import db
from sqlalchemy import and_
from flask.ext import restful
from microauth.models import Group
from microauth.utils import gzipped
from flask.ext.restful import reqparse
from microauth.resources.api_key import auth

class ConfigResource(restful.Resource):

	@gzipped
	def get(self):
		key = auth()
		return key.config.jsonify()

	@gzipped
	def post(self):
		key = auth()

		config = key.config

		parser = reqparse.RequestParser()
		parser.add_argument("priority",type=str, help="Whether to prefer allow groups over deny groups.")
		parser.add_argument("permit_root_login", type=bool, help='Determines whether the username "root" can authenticate')
		parser.add_argument("create_accounts", type=bool, help="Determines whether to create accounts for authenticated users.")
		parser.add_argument("defer_to_original", type=bool, help="Determines whether to fall back to the original login program")
		parser.add_argument("allow",type=str, help="Comma separated list of groups to allow")
		parser.add_argument("deny",type=str, help="Comma separated list of groups to deny")
		args = parser.parse_args()

		if args.priority and args.priority in ['allow', 'deny']:
			key.priority = args.priority

		if args.permit_root_login:
			key.permit_root_login = args.permit_root_login
		if args.create_accounts:
			key.create_accounts = args.create_accounts
		if args.defer_to_original:
			key.defer_to_original = args.defer_to_original
		if args.allow:
			for groupname in args.allow.split(','):
				group = Group.query.filter(and_(Group.key == key, Group.name == groupname)).first()
				if group:
					if not group in config.allow_groups:
						config.allow_groups.append(group)
					else:
						config.allow_groups.remove(group)

		db.session.add(config)
		db.session.commit()
		return config.jsonify()
