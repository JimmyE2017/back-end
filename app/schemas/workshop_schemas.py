from marshmallow import fields, post_dump, post_load, pre_dump, validate

from app.models.action_card_model import ActionCardType
from app.models.workshop_model import (
    WorkshopModel,
    WorkshopRoundCarbonFootprintModel,
    WorkshopRoundCarbonVariablesModel,
    WorkshopRoundConfigModel,
    WorkshopRoundModel,
)
from app.schemas import CustomSchema
from app.schemas.action_card_schemas import ActionCardBatchSchema, ActionCardSchema
from app.schemas.user_schemas import ParticipantSchema


class WorkshopSchema(CustomSchema):
    id = fields.Str(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=128))
    startAt = fields.AwareDateTime(required=True)
    creatorId = fields.Str(dump_only=True)
    coachId = fields.Str(required=True, validate=validate.Length(min=1))
    city = fields.Str(required=True, validate=validate.Length(max=128))
    address = fields.Str(validate=validate.Length(max=512))
    eventUrl = fields.Str(validate=validate.Length(max=1024))


class WorkshopParticipantSchema(CustomSchema):
    status = fields.Str()
    user = fields.Nested(
        ParticipantSchema, only=("id", "firstName", "lastName", "email")
    )
    surveyVariables = fields.Dict(keys=fields.Str())

    @post_dump
    def flatten_participant(self, data, **kwargs):
        data = {**data["user"], **data}
        del data["user"]
        return data


class WorkshopModelSchema(CustomSchema):
    id = fields.Str()
    footprintStructure = fields.Dict()
    variableFormulas = fields.Dict()
    globalCarbonVariables = fields.Dict()
    actionCards = fields.List(fields.Nested(ActionCardSchema))
    actionCardBatches = fields.List(fields.Nested(ActionCardBatchSchema))


class CarbonFootprintSchema(CustomSchema):
    participantId = fields.Str(required=True)
    footprint = fields.Dict()

    @pre_dump
    def fetch_id(self, data, **kwargs):
        data.participantId = data.participant.pk
        return data

    @post_load
    def make_object(self, data, **kwargs):
        data["participant"] = data.pop("participantId")  # Rename key
        return WorkshopRoundCarbonFootprintModel(**data)


class CarbonVariablesSchema(CustomSchema):
    participantId = fields.Str(required=True)
    variables = fields.Dict()

    @pre_dump
    def fetch_id(self, data, **kwargs):
        data.participantId = data.participant.pk
        return data

    @post_load
    def make_object(self, data, **kwargs):
        data["participant"] = data.pop("participantId")  # Rename key
        return WorkshopRoundCarbonVariablesModel(**data)


class WorkshopRoundConfigSchema(CustomSchema):
    actionCardType = fields.Str(
        required=True,
        validate=validate.OneOf(choices=[t.value for t in ActionCardType]),
    )
    targetedYear = fields.Int(required=True)
    budget = fields.Int(required=True)
    actionCardBatchIds = fields.List(fields.Str())

    @pre_dump
    def fetch_id(self, data, **kwargs):
        data.actionCardBatchIds = [acb.pk for acb in data.actionCardBatches]
        return data

    @post_load
    def make_object(self, data, **kwargs):
        data["actionCardBatches"] = data.pop("actionCardBatchIds")
        return WorkshopRoundConfigModel(**data)


class WorkshopRoundSchema(CustomSchema):
    year = fields.Integer(strict=True)
    carbonVariables = fields.List(fields.Nested(CarbonVariablesSchema), required=True)
    carbonFootprints = fields.List(fields.Nested(CarbonFootprintSchema), required=True)
    roundConfig = fields.Nested(WorkshopRoundConfigSchema)
    globalCarbonVariables = fields.Dict(keys=fields.Str())

    @post_load
    def make_object(self, data, **kwargs):
        return WorkshopRoundModel(**data)


class WorkshopDetailSchema(WorkshopSchema):
    startYear = fields.Integer(strict=True)
    endYear = fields.Integer(strict=True)
    yearIncrement = fields.Integer(strict=True, validate=validate.Range(min=1))

    participants = fields.List(fields.Nested(WorkshopParticipantSchema))
    model = fields.Nested(WorkshopModelSchema, dump_only=True)
    rounds = fields.List(fields.Nested(WorkshopRoundSchema))

    @post_dump
    def sort_model_action_cards(self, data, **kwargs):
        action_cards = data["model"]["actionCards"]
        action_cards = sorted(action_cards, key=lambda x: x["cardNumber"])

        data["model"]["actionCards"] = action_cards
        return data

    @post_dump
    def sort_model_action_card_batches(self, data, **kwargs):
        action_card_batches = data["model"]["actionCardBatches"]
        action_card_batches = sorted(action_card_batches, key=lambda x: x["name"])

        data["model"]["actionCardBatches"] = action_card_batches
        return data

    @post_load
    def make_object(self, data, **kwargs):
        return WorkshopModel(**data)
