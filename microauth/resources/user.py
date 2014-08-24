import bcrypt

from microauth import app, db


class User(db.Model):
    username = db.Column(db.String(80), primary_key=True)
    email = db.Column(db.String(254), unique=True)
    name = db.Column(db.String(120))
    password = db.Column(db.String(120))

    def __init__(self, username, email, name, password):
        self.username = username
        self.email = email
        self.name = name
        self.password = bcrypt.hashpw(
            password.encode(), bcrypt.gensalt(app.config["BCRYPT_ROUNDS"])
        ).decode()

    def jsonify(self):
        return {
            "username": self.username,
            "name": self.name,
            "email": self.email
        }

    def verify_password(self, password):
        if bcrypt.hashpw(
            password.encode(), self.password.encode()
        ) == self.password.encode():
            return True
        else:
            return False
