from marshmallow import fields, validate

from app.schemas import CustomSchema


class ActionCardSchema(CustomSchema):
    actionCardId = fields.Str(dump_only=True)
    number = fields.Integer(strict=True, validate=validate.Length(min=1))
    title = fields.Str(validate=validate.Length(min=1, max=256))
    category = fields.Str(validate=validate.Length(min=1, max=64))
    type = fields.Str(validate=validate.Length(min=1, max=64))
    key = fields.Str(validate=validate.Length(min=1, max=128))
    sector = fields.Str(validate=validate.Length(min=1, max=64))
    cost = fields.Integer(strict=True, validate=validate.Length(min=0))
