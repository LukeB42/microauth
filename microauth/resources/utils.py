import gzip
import functools 
from microauth import app
from sqlalchemy import or_, and_
from cStringIO import StringIO as IO
from microauth.resources.models import *
from flask import after_this_request, request

def get(key, cls, attrs=(), page=0, per_page=50):

	if page and per_page:
		if key.systemwide:
			return cls.query.filter(or_(cls.key == None, cls.key == key)).paginate(page, per_page).items
		return cls.query.filter(cls.key == key).paginate(page,per_page).items

	if attrs:
		(attr, identifier) = attrs
		attribute = getattr(cls, attr)
		if attribute:
			if key.systemwide: # Possibly search for duplicates and resolve to the local object.
				item = cls.query.filter(
					or_(and_(attribute==identifier, cls.key == None),
					and_(attribute==identifier, cls.key == key))
				).first()
			else:
				item = cls.query.filter(and_(attribute==identifier, cls.key == key)).first()
			return item

		raise Exception('Unrecognised attribute "%s" of %s.' % (attr, repr(cls)))

	if key.systemwide:
		return cls.query.filter(or_(cls.key == None, cls.key == key)).all()
	return cls.query.filter(cls.key == key).all()


def gzipped(f):
	if not app.config['GZIP_HERE']:
		return f

	@functools.wraps(f)
	def view_func(*args, **kwargs):

		@after_this_request
		def zipper(response):
			accept_encoding = request.headers.get('Accept-Encoding', '')

			if 'gzip' not in accept_encoding.lower():
				return response

			response.direct_passthrough = False

			if (response.status_code < 200 or
				response.status_code >= 300 or
				'Content-Encoding' in response.headers):
				return response
			gzip_buffer = IO()
			gzip_file = gzip.GzipFile(mode='wb', 
									  fileobj=gzip_buffer)
			gzip_file.write(response.data)
			gzip_file.close()

			response.data = gzip_buffer.getvalue()
			response.headers['Content-Encoding'] = 'gzip'
			response.headers['Vary'] = 'Accept-Encoding'
			response.headers['Content-Length'] = len(response.data.replace(' ',''))

			return response

		return f(*args, **kwargs)

	return view_func
