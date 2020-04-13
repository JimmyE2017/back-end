from marshmallow import fields, validate

from app.schemas import CustomSchema


class WorkshopSchema(CustomSchema):
    title = fields.Str(required=True, validate=validate.Length(min=1, max=128))
    startAt = fields.Str()
    creatorId = fields.Str()
    coachId = fields.Str()
    location = fields.Str(validate=validate.Length(min=1, max=256))
    eventUrl = fields.Str()
