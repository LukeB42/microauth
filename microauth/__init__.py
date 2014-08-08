from flask import Flask
from flask.ext import restful

from microauth.resources import user_collection, user_resource

app = Flask("microauth")
api = restful.Api(app)

api.add_resource(user_collection.UserCollection, "/user")
api.add_resource(user_resource.UserResource, "/user/<string:username>")
