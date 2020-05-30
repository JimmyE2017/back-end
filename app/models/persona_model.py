from __future__ import annotations

import datetime

from app.common.uuid_generator import generate_id
from app.models import db


class PersonaModel(db.Document):

    meta = {"collection": "personas"}

    id = db.StringField(primary_key=True, default=generate_id)
    firstName = db.StringField(required=True, max_length=64, min_length=1)
    lastName = db.StringField(required=True, max_length=64, min_length=1)
    description = db.StringField()
    createdAt = db.DateTimeField(default=datetime.datetime.utcnow)
    updatedAt = db.DateTimeField(default=datetime.datetime.utcnow)
    carbonFormAnswers = db.DictField(required=True)

    def __str__(self):
        return f"Persona {self.id} - {self.firstName} {self.lastName}"

    def __repr__(self):
        return f"<Persona {self.id} - {self.firstName} {self.lastName}>"

    @classmethod
    def find_by_id(cls, id: str) -> PersonaModel:
        try:
            persona = cls.objects.get(id=id)
        except db.DoesNotExist:
            persona = None
        return persona
