"""
This file defines an /events endpoint that permits API keys to
review login attempts.
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

class EventCollection(restful.Resource):

	@gzipped
	def get(self):
		key = auth()

		parser = reqparse.RequestParser()
		parser.add_argument("page", type=int, help="Current page number.")
		parser.add_argument("per_page", type=int, help="Items per page.")
		parser.add_argument("id", type=str, help="Unique ID")
		args = parser.parse_args()

		res = [event.jsonify() for event in get(key, Event)]
		res.reverse()

		# Pagination is performed here to ensure we
		# return the latest entries first.
		if args.page:
			if args.per_page:
				p   = args.page
				p   = p-1
				pp  = args.per_page
				return(res[p*pp:(p*pp)+pp])
			res = [event.jsonify() for event in get(key, Event, page=args.page)]
			res.reverse()
			return(res)

		if args.id:
			event = get(key, Event, ('uid', args.id))
			if not event: abort(404)
			return event.jsonify()

		# Return the last 50 elements by default
		return(res[-50:])

class EventResource(restful.Resource):

	def get(self, username):

		key = auth()
		user = get(key, User, ('username', username))


		parser = reqparse.RequestParser()
		parser.add_argument("page", type=int, help="Current page number.")
		parser.add_argument("per_page", type=int, help="Items per page.")
		args = parser.parse_args()

		if not user: return {}, 404

		res = [event.jsonify() for event in user.events]
		res.reverse()

		if args.page:
			if args.per_page:
				p   = args.page
				p   = p-1
				pp  = args.per_page
				return(res[p*pp:(p*pp)+pp])

		return(res[-50:])
