from __future__ import annotations

import datetime
from enum import Enum

from app.common.uuid_generator import generate_id
from app.models import db
from app.models.action_card_model import ActionCardBatchModel, ActionCardModel
from app.models.model_model import Model
from app.models.user_model import UserModel


class WorkshopParticipantStatus(Enum):
    CREATED = "created"
    EXISTING = "existing"
    FORMSENT = "formsent"
    TOCHECK = "tocheck"
    READY = "ready"


class WorkshopParticipantModel(db.EmbeddedDocument):
    user = db.ReferenceField(UserModel, db_field="userId")
    status = db.StringField(max_length=32)


class WorkshopRoundCarbonFootprintModel(db.EmbeddedDocument):
    participant = db.LazyReferenceField(UserModel, db_field="participantId")
    footprint = db.DictField()


class WorkshopRoundCarbonVariablesModel(db.EmbeddedDocument):
    participant = db.LazyReferenceField(UserModel, db_field="participantId")
    variables = db.DictField()


class WorkshopRoundConfigModel(db.EmbeddedDocument):
    actionCardType = db.StringField()
    targetedYear = db.IntField()
    budget = db.IntField()
    actionCardBatches = db.ListField(
        db.LazyReferenceField(ActionCardBatchModel), db_field="actionCardBatchIds"
    )


class WorkshopRoundModel(db.EmbeddedDocument):
    year = db.IntField()
    carbonVariables = db.ListField(
        db.EmbeddedDocumentField(WorkshopRoundCarbonVariablesModel)
    )
    carbonFootprints = db.ListField(
        db.EmbeddedDocumentField(WorkshopRoundCarbonFootprintModel)
    )
    roundConfig = db.EmbeddedDocumentField(WorkshopRoundConfigModel)
    globalCarbonVariables = db.DictField()


class WorkshopModel(db.Document):
    """
    This is an abstract class.
    Please inherit from it if you want to create a new type of workshop
    """

    meta = {"collection": "workshops"}

    # Basic Info
    workshopId = db.StringField(primary_key=True, default=generate_id)
    name = db.StringField(
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

    # Configuration
    startYear = db.IntField(default=2020)
    endYear = db.IntField(default=2050)
    yearIncrement = db.IntField(default=3)

    # Participants
    participants = db.ListField(
        db.EmbeddedDocumentField(WorkshopParticipantModel), default=[]
    )

    # Model
    model = db.ReferenceField(Model, db_field="modelId")

    # Rounds
    rounds = db.ListField(db.EmbeddedDocumentField(WorkshopRoundModel))

    def __repr__(self):
        return (
            f"<Workshop {self.workshopId} | {self.name} "
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

    def get_participant_ids(self) -> list:
        return [p.user.id for p in self.participants]

    def get_workshop_participant(self, participant_id: str):
        for workshop_participant in self.participants:
            if workshop_participant.user.id == participant_id:
                return workshop_participant

        return None

    def fetch_actions_cards(self) -> None:
        action_cards = ActionCardModel.find_all()
        self.model.actionCards = action_cards

    def fetch_actions_card_batches(self) -> None:
        # Append action card batches from coach to field model
        action_cards_batches = ActionCardBatchModel.find_action_card_batches_by_coach(
            coach_id=self.coachId
        )
        self.model.actionCardBatches = action_cards_batches
