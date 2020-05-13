from __future__ import annotations

import datetime
from enum import Enum

from flask import current_app
from flask_jwt_extended import create_access_token
from mongoengine import QuerySet

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

MAPPING_ROLES_CLASS = {
    Roles.PARTICIPANT.value: "UserModel.ParticipantModel",
    Roles.COACH.value: "UserModel.CoachModel",
    Roles.ADMIN.value: "UserModel.CoachModel",
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

    # User specific fields
    userId = db.StringField(primary_key=True, default=generate_id)
    firstName = db.StringField(required=True, max_length=64, min_length=1)
    lastName = db.StringField(required=True, max_length=64, min_length=1)
    email = db.StringField(required=True, max_length=256, unique=True)
    password = db.StringField()
    role = db.ListField(db.StringField(max_length=32), required=True)
    createdAt = db.DateTimeField(default=datetime.datetime.utcnow)
    updatedAt = db.DateTimeField(default=datetime.datetime.utcnow)

    # Coach specific fields
    city = db.StringField(max_length=256)
    workshopsCount = db.IntField()
    awarenessRaisedCount = db.IntField()

    # Participant specific fields
    workshopParticipations = db.ListField(db.StringField(), default=[])

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

    @classmethod
    def find_coach_by_id(cls, user_id: str) -> UserModel:
        try:
            user = cls.objects.get(
                userId=user_id, role__in=[Roles.ADMIN.value, Roles.COACH.value]
            )
        except db.DoesNotExist:
            user = None
        return user

    @classmethod
    def find_coach_by_email(cls, email: str) -> UserModel:
        try:
            user = cls.objects.get(
                email=email, role__in=[Roles.ADMIN.value, Roles.COACH.value]
            )
        except db.DoesNotExist:
            user = None
        return user

    @classmethod
    def find_all_coaches(cls) -> QuerySet:
        return cls.objects(role__in=[Roles.ADMIN.value, Roles.COACH.value]).all()

    def add_participant_role(self) -> None:
        """
        To use when we want to update the role of the user to participant.
        Init data specific to the participant
        :return:
        """
        self.role.append(Roles.PARTICIPANT.value)
        self.workshopParticipations = []

        return
