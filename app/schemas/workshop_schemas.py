from marshmallow import ValidationError, fields, post_dump, post_load, validate

from app.models.coach_model import CoachModel
from app.schemas import CustomSchema
from app.schemas.action_card_schemas import ActionCardBatchSchema, ActionCardSchema


class WorkshopSchema(CustomSchema):
    id = fields.Str(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=128))
    startAt = fields.AwareDateTime(required=True)
    creatorId = fields.Str(dump_only=True)
    coachId = fields.Str(required=True, validate=validate.Length(min=1))
    city = fields.Str(required=True, validate=validate.Length(max=128))
    address = fields.Str(validate=validate.Length(max=512))
    eventUrl = fields.Str(validate=validate.Length(max=1024))

    @post_load
    def check_coach_id_exist(self, data, **kwargs):
        coach_id = data["coachId"]
        coach = CoachModel.find_by_id(coach_id)
        if coach is None:
            raise ValidationError(
                "Coach does not exist : {}".format(coach_id), "coachId"
            )

        return data


class WorkshopModelSchema(CustomSchema):
    id = fields.Str()
    footprintStructure = fields.Dict()
    variableFormulas = fields.Dict()
    globalCarbonVariables = fields.Dict()
    actionCards = fields.List(fields.Nested(ActionCardSchema))
    actionCardBatches = fields.List(fields.Nested(ActionCardBatchSchema))


class WorkshopDetailSchema(WorkshopSchema):
    model = fields.Nested(WorkshopModelSchema)
    # participants = fields.List(fields.Nested(WorkshopParticipantSchema))

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
