from flask import Flask
from flask.ext import restful
from flask.ext.sqlalchemy import SQLAlchemy


app = Flask("microauth")

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/test.db"
db = SQLAlchemy(app)

api = restful.Api(app)

from microauth.resources import user_collection, user_resource

api.add_resource(user_collection.UserCollection, "/user")
api.add_resource(user_resource.UserResource, "/user/<string:username>")
