from marshmallow import ValidationError, fields, post_load, validate

from app.models.coach_model import CoachModel
from app.schemas import CustomSchema


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
