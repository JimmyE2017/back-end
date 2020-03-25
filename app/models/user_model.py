from __future__ import annotations

import datetime
from enum import Enum
from typing import List

from app.models import db


class Roles(Enum):
    GUEST = "guest"
    PARTICIPANT = "participant"
    MODERATOR = "moderator"
    ADMIN = "admin"


ACCESS_LEVEL = {
    Roles.GUEST.value: 0,
    Roles.PARTICIPANT.value: 1,  # Not used yet
    Roles.MODERATOR.value: 2,
    Roles.ADMIN.value: 3,
}


class BlacklistTokenModel(db.Model):
    __tablename__ = "blacklisted_tokens"
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(120), index=True)
    blacklisted_on = db.Column(db.DateTime(), default=datetime.datetime.utcnow)

    @classmethod
    def is_jti_blacklisted(cls, jti: str) -> bool:
        query = cls.query.filter_by(jti=jti).first()
        return query is not None


class UserModel(db.Model):
    __tablename__ = "users"
    user_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), index=False, unique=False, nullable=False)
    last_name = db.Column(db.String(64), index=False, unique=False, nullable=False)
    email = db.Column(db.String(256), index=True, unique=True, nullable=False)
    password = db.Column(db.String(512), index=False, unique=False, nullable=False)
    role = db.Column(db.String(32))
    created_at = db.Column(db.DateTime(), default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime(), default=datetime.datetime.utcnow)

    def __repr__(self):
        return f"<UserModel {self.first_name} {self.last_name}>"

    def allowed(self, access_level: Roles) -> bool:
        return ACCESS_LEVEL[self.role] >= ACCESS_LEVEL[access_level.value]

    @classmethod
    def find_by_id(cls, user_id: int) -> UserModel:
        return cls.query.filter_by(user_id=user_id).first()

    @classmethod
    def find_by_email(cls, email: str) -> UserModel:
        return cls.query.filter_by(email=email).first()

    @classmethod
    def find_all_moderators(cls) -> List[UserModel]:
        return cls.query.filter(
            cls.role.in_([Roles.ADMIN.value, Roles.MODERATOR.value])
        ).all()
