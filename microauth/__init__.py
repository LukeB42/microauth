import os
import bcrypt
from flask.ext import restful
from flask.ext.sqlalchemy import SQLAlchemy
from flask import Flask, send_from_directory
from sqlalchemy.engine.reflection import Inspector

app = Flask("microauth")
app.config.from_object("microauth.config")
db = SQLAlchemy(app)
api = restful.Api(app, prefix='/v1')

from microauth.resources import api_key
from microauth.resources import users
from microauth.resources import roles
from microauth.resources import privs
from microauth.resources import models

inspector = Inspector.from_engine(db.engine)
tables = [table_name for table_name in inspector.get_table_names()]
if 'users' not in tables:
	db.create_all()
	master = models.APIKey(name = app.config['MASTER_KEY_NAME'])
	if app.config['MASTER_KEY']: master.key = app.config['MASTER_KEY']
	else: master.key = master.generate_key_str()
	print master.key
	master.active     = True
	master.systemwide = True
	master.global_del = True
	db.session.add(master)
	db.session.commit()

api.add_resource(api_key.KeyCollection, "/keys")
api.add_resource(api_key.KeyResource,   "/keys/<string:name>")

api.add_resource(users.UserCollection,  "/users")
api.add_resource(users.UserResource,    "/users/<string:username>")
api.add_resource(users.UserLogin,       "/users/<string:username>/login")

api.add_resource(roles.RoleCollection,  "/roles")
api.add_resource(roles.RoleResource,    "/roles/<string:name>")
api.add_resource(roles.GrantPrivs,      "/roles/<string:name>/grant")
api.add_resource(roles.DenyPrivs,       "/roles/<string:name>/deny")
api.add_resource(roles.RevokePrivs,     "/roles/<string:name>/revoke")

api.add_resource(privs.PrivCollection,  "/privs")
api.add_resource(privs.PrivResource,    "/privs/<string:name>")


@app.route('/')
def docs_index():
	f = open('docs/_build/html/index.html')
	response = f.read()
	f.close()
	return response

@app.route('/<path:path>')
def docs(path):
	return send_from_directory('docs/_build/html', path)
