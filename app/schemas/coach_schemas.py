from marshmallow import fields, validate

from app.schemas import CustomSchema


class CoachSchema(CustomSchema):
    firstName = fields.Str(required=True, validate=validate.Length(min=1, max=64))
    lastName = fields.Str(required=True, validate=validate.Length(min=1, max=64))
    email = fields.Email(required=True, max=256)
    password = fields.Str(
        required=True, validate=validate.Length(min=8), load_only=True
    )