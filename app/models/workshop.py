from __future__ import annotations
import datetime
from mongoengine import *
from app.models.user_model import UserModel
from app.common.uuid_generator import generate_id
from app.models import db

class Workshop(db.Document):
    """
    This is an abstract class.
    Please inherit from it if you want to create a new type of workshop
    """

    meta = {"collection": "workshop", "allow_inheritance": True}

    workshopId = db.StringField(primary_key=True, default=generate_id)
    title = db.StringField(required=True, max_length=128, min_length=1, default='Atelier CAPLC')
    createdAt = db.DateTimeField(default=datetime.datetime.utcnow)
    updatedAt = db.DateTimeField(default=datetime.datetime.utcnow)
    startAt = db.DateTimeField(default=datetime.datetime.utcnow)
    creatorId = db.ReferenceField(UserModel, reverse_delete_rule=NULLIFY)
    coachId = db.ReferenceField(UserModel, reverse_delete_rule=NULLIFY)
    eventUrl = db.StringField(default='caplc.com')
    location = db.StringField(required=True, max_length=256, min_length=1, default='CAPLC')

    def __repr__(self):
        return f"<Workshop {self.workshopId} | {self.title} - animated by {self.coachId} at {self.location} on {self.startAt.strftime('%d/%m/%y')}>"

    @classmethod
    def find_by_id(cls, workshop_id: str) -> Workshop:
        try:
            workshop = cls.objects.get(workshopId=workshop_id)
        except db.DoesNotExist:
            workshop = None
        return workshop

    @classmethod
    def find_by_coach_id(cls, coach_id: str) -> Workshop:
        try:
            workshop = cls.objects.get(coachId=coach_id)
        except db.DoesNotExist:
            workshop = None
        return workshop
