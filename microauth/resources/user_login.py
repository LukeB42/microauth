from flask.ext import restful
from flask.ext.restful import abort, reqparse

from sqlalchemy import exc

from microauth import db
from microauth.resources.user import User


class UserLogin(restful.Resource):
    def get(self, username):
        parser = reqparse.RequestParser()
        parser.add_argument(
            "password", type=str, help="Password of account", required=True
        )
        args = parser.parse_args()

        user = User.query.filter_by(username=username).first()

        if user is None:
            return {"error": "User {0} not found.".format(username)}, 404

        if user.verify_password(args.password):
            status = "ok"
        else:
            status = "failed"

        return {"status": status}
