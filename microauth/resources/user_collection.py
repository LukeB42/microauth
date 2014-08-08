from flask.ext import restful
from flask.ext.restful import abort, reqparse

from sqlalchemy import exc

from microauth import db
from microauth.resources.user import User

class UserCollection(restful.Resource):
    def get(self):
        return [user.jsonify() for user in User.query.all()]

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument(
            "username", type=str, help="Username of account", required=True
        )
        parser.add_argument(
            "name", type=str, help="Name of account", required=True
        )
        parser.add_argument(
            "email", type=str, help="Email address of account", required=True
        )
        parser.add_argument(
            "password", type=str, help="Password of account", required=True
        )
        args = parser.parse_args()

        try:
            user = User(args.username, args.email, args.name, args.password)
            db.session.add(user)
            db.session.commit()
        except exc.IntegrityError:
            abort(
                409,
                message="Username {0} or email {1} already in use.".format(
                    args.username, args.email
                )
            )

        return {
            "username": args.username,
            "name": args.name,
            "email": args.email
        }, 201
