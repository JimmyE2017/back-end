from __future__ import annotations

from enum import Enum

from app.models import db


class ParticipantStatus(Enum):
    CREATED = "created"
    EXISTING = "existing"
    FORMSENT = "formsent"
    TOCHECK = "tocheck"
    READY = "ready"


class ParticipantModel(db.EmbeddedDocument):
    from app.models.user_model import UserModel

    user = db.ReferenceField(UserModel)
    status = db.StringField(max_length=32)
