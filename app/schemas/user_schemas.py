from marshmallow import fields, validate

from app.schemas import CustomSchema


class LoginSchema(CustomSchema):
    email = fields.Str(required=True)
    password = fields.Str(required=True)


class ForgottenPasswordSchema(CustomSchema):
    email = fields.Str(required=True)


class NewPasswordSchema(CustomSchema):
    password = fields.Str(
        required=True, validate=validate.Length(min=8), load_only=True
    )
