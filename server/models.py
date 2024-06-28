from . import db
from uuid import uuid4
from flask_login import UserMixin
from sqlalchemy.dialects.postgresql import JSON

def get_uuid():
    return uuid4().hex

class User(db.Model, UserMixin):
    id = db.Column(db.String(100), unique=True, primary_key=True, default=get_uuid)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    username = db.Column(db.String(150))
    hs2048 = db.Column(db.Integer)

    def to_json(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
        }