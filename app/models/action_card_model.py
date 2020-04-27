import datetime
from enum import Enum

from app.common.uuid_generator import generate_id
from app.models import db


class ActionCardCategory(Enum):
    INDIVIDUAL = "individual"
    COLLECTIVE = "collective"


class ActionCardType(Enum):
    ECOFRIENDLY_ACTION = "eco-friendly action"
    AWARENESS = "awareness"
    SYSTEM = "system"


class ActionCardModel(db.Document):
    meta = {"collection": "actionCards"}

    actionCardId = db.StringField(primary_key=True, default=generate_id)
    number = db.IntField(required=True, min_value=0)
    title = db.StringField(required=True)
    category = db.StringField(required=True)
    type = db.StringField(required=True)
    key = db.StringField(required=True)
    sector = db.StringField(required=True)
    cost = db.IntField(required=True, min_value=0)
    createdAt = db.DateTimeField(default=datetime.datetime.utcnow)
    updatedAt = db.DateTimeField(default=datetime.datetime.utcnow)

    @classmethod
    def find_all(cls):
        return cls.objects().order_by("number")
