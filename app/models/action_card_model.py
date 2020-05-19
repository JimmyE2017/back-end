import datetime
from enum import Enum

from app.common.uuid_generator import generate_id
from app.models import db


class ActionCardType(Enum):
    INDIVIDUAL = "individual"
    COLLECTIVE = "collective"


class ActionCardCategory(Enum):
    ECOFRIENDLY_ACTION = "eco-friendly action"
    AWARENESS = "awareness"
    SYSTEM = "system"


class ActionCardImpactType(Enum):
    INDIVIDUAL = "individual"
    COLLECTIVE = "collective"
    SYSTEM = "system"


class ActionCardOperationModel(db.EmbeddedDocument):
    variable = db.StringField(required=True)
    operation = db.DictField(required=True)


class ActionCardModel(db.Document):
    meta = {"collection": "actionCards"}

    actionCardId = db.StringField(primary_key=True, default=generate_id)
    cardNumber = db.IntField(required=True, min_value=0)
    name = db.StringField(required=True)
    category = db.StringField(required=True)
    type = db.StringField(required=True)
    key = db.StringField(required=True)
    sector = db.StringField(required=True)
    cost = db.IntField(required=True, min_value=0)
    impactType = db.StringField()
    operations = db.ListField(
        db.EmbeddedDocumentField(ActionCardOperationModel), default=[]
    )
    createdAt = db.DateTimeField(default=datetime.datetime.utcnow)
    updatedAt = db.DateTimeField(default=datetime.datetime.utcnow)

    @classmethod
    def find_all(cls):
        return cls.objects().order_by("number")


class ActionCardBatchModel(db.Document):
    meta = {"collection": "actionCardBatches"}

    actionCardBatchId = db.StringField(primary_key=True, default=generate_id)
    coachId = db.StringField()
    name = db.StringField(required=True)
    actionCardIds = db.ListField(db.StringField(), required=True)
    type = db.StringField(required=True)
    default = db.BooleanField()
    createdAt = db.DateTimeField(default=datetime.datetime.utcnow)
    updatedAt = db.DateTimeField(default=datetime.datetime.utcnow)

    @classmethod
    def get_default_batches(cls):
        return cls.objects(default=True).all()

    @classmethod
    def find_default_batches(cls):
        return cls.objects(default=True).all()

    @classmethod
    def find_action_card_batches_by_coach(cls, coach_id):
        return cls.objects(coachId=coach_id).all()
