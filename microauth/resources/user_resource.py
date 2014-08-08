from flask.ext import restful
from flask.ext.restful import abort, reqparse

from sqlalchemy.orm import exc

from microauth import db
from microauth.resources.user import User

class UserResource(restful.Resource):
    def get(self, username):
        user = User.query.filter_by(username=username).first()
        if user is None:
            return []

        else:
            return user.jsonify()

    def put(self, username):
        parser = reqparse.RequestParser()
        parser.add_argument(
            "username", type=str, help="Username of account"
        )
        parser.add_argument(
            "name", type=str, help="Name of account"
        )
        parser.add_argument(
            "email", type=str, help="Email address of account"
        )
        parser.add_argument(
            "password", type=str, help="Password of account"
        )
        args = parser.parse_args()

        user = User.query.filter_by(username=username).first()
        if args.username is not None:
            user.username = args.username

        if args.name is not None:
            user.name = args.name

        if args.email is not None:
            user.email = args.email

        if args.password is not None:
            user.password = args.password

        db.session.commit()
        return user.jsonify()

    def delete(self, username):
        user = User.query.filter_by(username=username).first()

        try:
            db.session.delete(user)
            db.session.commit()
        except exc.UnmappedInstanceError:
            pass

        return "", 204
