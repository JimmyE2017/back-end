from __future__ import annotations

import datetime

from mongoengine import DoesNotExist

from app.common.uuid_generator import generate_id
from app.models import db
from app.models.persona_model import PersonaModel


class Model(db.Document):
    meta = {"collection": "models"}

    modelId = db.StringField(primary_key=True, default=generate_id)
    footprintStructure = db.DictField(required=True)
    globalCarbonVariables = db.DictField(required=True)
    variableFormulas = db.DictField(required=True)
    createdAt = db.DateTimeField(default=datetime.datetime.utcnow)
    updatedAt = db.DateTimeField(default=datetime.datetime.utcnow)
    personas = db.ListField(db.ReferenceField(PersonaModel, db_field="id"), default=[])

    @classmethod
    def find_last_created_model(cls) -> Model:
        model = cls.objects.order_by("-createdAt").first()
        if model is None:
            raise DoesNotExist("No model in DB")
        return model

    @classmethod
    def find_by_id(cls, model_id: str) -> Model:
        try:
            model = cls.objects.get(modelId=model_id)
        except db.DoesNotExist:
            model = None
        return model
