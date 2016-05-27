import os
import bcrypt
import optparse
from flask.ext import restful
from pkgutil import extend_path
from flask.ext.sqlalchemy import SQLAlchemy
from flask import Flask, send_from_directory
from sqlalchemy.engine.reflection import Inspector

__path__ = extend_path(__path__, __name__)
__all__ = ["run", "client", "repl", "resources", "models", "utils"]

app = Flask("microauth")
app.config.from_object("microauth.config")
app.version = "Microauth 0.1.3"
app.config['HTTP_BASIC_AUTH_REALM'] = app.version

api = restful.Api(app, prefix='/v1')

db = SQLAlchemy(app)

from microauth import models
from microauth.resources import api_key
from microauth.resources import users
from microauth.resources import groups
from microauth.resources import privs
from microauth.resources import events
from microauth.resources import config

def init():

    try:
        import setproctitle
        setproctitle.setproctitle("microauth")
    except ImportError:
        pass

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



    api.add_resource(api_key.KeyCollection,     "/keys")
    api.add_resource(api_key.KeyResource,       "/keys/<string:name>")

    api.add_resource(users.UserCollection,      "/users")
    api.add_resource(users.UserResource,        "/users/<string:username>")
    api.add_resource(users.UserLogin,           "/users/<string:username>/login")
    
    api.add_resource(groups.GroupCollection,    "/groups")
    api.add_resource(groups.GroupResource,      "/groups/<string:name>")
    api.add_resource(groups.GroupResourcePrivs, "/groups/<string:name>/privs")
    api.add_resource(groups.GroupResourceUsers, "/groups/<string:name>/users")
    api.add_resource(groups.GrantPrivs,         "/groups/<string:name>/grant")
    api.add_resource(groups.DenyPrivs,          "/groups/<string:name>/deny")
    api.add_resource(groups.RevokePrivs,        "/groups/<string:name>/revoke")

    api.add_resource(privs.PrivCollection,      "/privs")
    api.add_resource(privs.PrivResource,        "/privs/<string:name>")

    api.add_resource(events.EventCollection,    "/events")
    api.add_resource(events.EventResource,      "/events/<string:username>")

    api.add_resource(config.ConfigResource,     "/config")
