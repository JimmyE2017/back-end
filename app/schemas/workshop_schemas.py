from marshmallow import ValidationError, fields, post_load, validate

from app.models.coach_model import CoachModel
from app.schemas import CustomSchema
from app.schemas.action_card_schemas import ActionCardBatchSchema, ActionCardSchema


class WorkshopSchema(CustomSchema):
    workshopId = fields.Str(dump_only=True)
    title = fields.Str(required=True, validate=validate.Length(min=1, max=128))
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
