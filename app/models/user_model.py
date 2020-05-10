from __future__ import annotations

import datetime
from enum import Enum

from flask import current_app
from flask_jwt_extended import create_access_token

from app.common.mail.mail_services import send_reset_password_mail
from app.common.uuid_generator import generate_id
from app.models import db


class Roles(Enum):
    GUEST = "guest"
    PARTICIPANT = "participant"
    COACH = "coach"
    ADMIN = "admin"


ACCESS_LEVEL = {
    Roles.GUEST.value: 0,
    Roles.PARTICIPANT.value: 1,  # Not used yet
    Roles.COACH.value: 2,
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
    """
    This is an abstract class.
    Please inherit from it if you want to create a new type of user
    """

    meta = {"collection": "users", "allow_inheritance": True}

    userId = db.StringField(primary_key=True, default=generate_id)
    firstName = db.StringField(required=True, max_length=64, min_length=1)
    lastName = db.StringField(required=True, max_length=64, min_length=1)
    email = db.StringField(required=True, max_length=256, unique=True)
    password = db.StringField()
    role = db.ListField(db.StringField(max_length=32), required=True)
    createdAt = db.DateTimeField(default=datetime.datetime.utcnow)
    updatedAt = db.DateTimeField(default=datetime.datetime.utcnow)
    workshopParticipations = db.ListField(db.StringField())

    def __str__(self):
        return f"User {self.userId} - {self.firstName} {self.lastName}"

    def __repr__(self):
        return f"<User {self.userId} - {self.firstName} {self.lastName}>"

    def allowed(self, access_level: Roles) -> bool:
        return (
            max([ACCESS_LEVEL[r] for r in self.role])
            >= ACCESS_LEVEL[access_level.value]
        )

    def send_reset_password_mail(self) -> str:
        # Genereate temporary access token for password resetting
        token = create_access_token(identity=self.id)
        reset_url = "{url}/reset_password?access_token={token}".format(
            url=current_app.config["PREFERRED_URL_SCHEME"], token=token
        )
        print(token)
        send_reset_password_mail(self.email, reset_url=reset_url)
        return token

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
