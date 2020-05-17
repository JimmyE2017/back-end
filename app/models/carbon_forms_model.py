from __future__ import annotations

from datetime import datetime

from app.common.uuid_generator import generate_id
from app.models import db
from app.models.user_model import UserModel
from app.models.workshop_model import WorkshopModel


class CarbonFormAnswersModel(db.Document):
    meta = {
        "collection": "carbonFormAnswers",
        "indexes": [{"fields": ["workshop", "participant"], "unique": True}],
    }

    carbonFormAnswersId = db.StringField(primary_key=True, default=generate_id)
    workshop = db.LazyReferenceField(
        WorkshopModel, required=True, db_field="workshopId"
    )
    participant = db.LazyReferenceField(
        UserModel, required=True, db_field="participantId"
    )
    answers = db.DictField(required=True)
    createdAt = db.DateTimeField(default=datetime.utcnow)
    updatedAt = db.DateTimeField(default=datetime.utcnow)

    @classmethod
    def find_by_workshop_id_and_participant_id(
        cls, workshop_id: str, participant_id: str
    ) -> CarbonFormAnswersModel:
        try:
            carbon_form_answers = cls.objects.get(
                workshop=workshop_id, participant=participant_id
            )
        except db.DoesNotExist:
            carbon_form_answers = None
        return carbon_form_answers
