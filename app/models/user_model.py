from __future__ import annotations

import datetime
from enum import Enum

from mongoengine import QuerySet

from app.common.uuid_generator import generate_id
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


class BlacklistTokenModel(db.Document):
    meta = {"collection": "blacklistedTokens"}
    token = db.StringField(required=True)
    blacklistedOn = db.DateTimeField(default=datetime.datetime.utcnow)

    @classmethod
    def is_jti_blacklisted(cls, jti: str) -> bool:
        try:
            query = cls.objects.get(token=jti)
        except db.DoesNotExist:
            query = None
        return query is not None


class UserModel(db.Document):
    meta = {"collection": "users"}

    userId = db.StringField(primary_key=True, default=generate_id)
    firstName = db.StringField(required=True, max_length=64, min_length=1)
    lastName = db.StringField(required=True, max_length=64, min_length=1)
    email = db.StringField(required=True, max_length=256, unique=True)
    password = db.StringField(required=True)
    role = db.StringField(required=True, max_length=32)
    createdAt = db.DateTimeField(default=datetime.datetime.utcnow)
    updatedAt = db.DateTimeField(default=datetime.datetime.utcnow)

    def __repr__(self):
        return f"<User {self.userId}>"

    def allowed(self, access_level: Roles) -> bool:
        return ACCESS_LEVEL[self.role] >= ACCESS_LEVEL[access_level.value]

    @classmethod
    def find_by_id(cls, user_id: str) -> UserModel:
        try:
            user = cls.objects.get(userId=user_id)
        except db.DoesNotExist:
            user = None
        return user

    @classmethod
    def find_by_email(cls, email: str) -> UserModel:
        try:
            user = cls.objects.get(email=email)
        except db.DoesNotExist:
            user = None
        return user

    @classmethod
    def find_all_moderators(cls) -> QuerySet:
        return cls.objects(role__in=[Roles.ADMIN.value, Roles.MODERATOR.value]).all()
