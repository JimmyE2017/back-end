from __future__ import annotations

import datetime
from enum import Enum

from app.common.uuid_generator import generate_id
from app.models import db
from app.models.model_model import Model


class ParticipantStatus(Enum):
    CREATED = "created"
    EXISTING = "existing"
    FORMSENT = "formsent"
    TOCHECK = "tocheck"
    READY = "ready"


class WorkshopParticipants(db.EmbeddedDocument):
    from app.models.user_model import UserModel

    user = db.ReferenceField(UserModel)
    status = db.StringField(max_length=32)


class WorkshopModel(db.Document):
    """
    This is an abstract class.
    Please inherit from it if you want to create a new type of workshop
    """

    meta = {"collection": "workshops"}

    workshopId = db.StringField(primary_key=True, default=generate_id)
    title = db.StringField(
        required=True, max_length=128, min_length=1, default="Atelier CAPLC"
    )
    createdAt = db.DateTimeField(default=datetime.datetime.utcnow)
    updatedAt = db.DateTimeField(default=datetime.datetime.utcnow)
    startAt = db.DateTimeField(required=True)
    creatorId = db.StringField(required=True)
    coachId = db.StringField(required=True)
    eventUrl = db.StringField(default="caplc.com")
    city = db.StringField(max_length=128, min_length=1)
    address = db.StringField(max_length=512)
    participants = db.ListField(
        db.EmbeddedDocumentField(WorkshopParticipants), default=[]
    )
    model = db.ReferenceField(Model)

    def __repr__(self):
        return (
            f"<Workshop {self.workshopId} | {self.title} "
            f"- animated by {self.coachId} at {self.city} on {self.startAt} "
            f"- with {len(self.participants)} participants>"
        )

    @classmethod
    def find_by_id(cls, workshop_id: str) -> WorkshopModel:
        try:
            workshop = cls.objects.get(workshopId=workshop_id)
        except db.DoesNotExist:
            workshop = None
        return workshop

    @classmethod
    def find_by_coach_id(cls, coach_id: str) -> WorkshopModel:
        try:
            workshops = cls.objects(coachId=coach_id)
        except db.DoesNotExist:
            workshops = []
        return workshops
