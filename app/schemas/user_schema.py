from marshmallow import Schema, fields, post_load, validate

from app.models.user_model import UserModel


class LoginSchema(Schema):
    email = fields.Str(required=True)
    password = fields.Str(required=True)


class UserSchema(Schema):
    user_id = fields.Int(dump_only=True)
    first_name = fields.Str(required=True, validate=validate.Length(min=1, max=64))
    last_name = fields.Str(required=True, validate=validate.Length(min=1, max=64))
    email = fields.Email(required=True, max=256)
    password = fields.Str(
        required=True, validate=validate.Length(min=8), load_only=True
    )
    role = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    class Meta:
        fields = (
            "user_id",
            "first_name",
            "last_name",
            "email",
            "password",
            "role",
            "created_at",
            "updated_at",
        )
        ordered = True

    @post_load
    def load_user(self, data, **kwargs):
        return UserModel(**data)
