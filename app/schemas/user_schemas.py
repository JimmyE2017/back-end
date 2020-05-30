from marshmallow import fields, pre_dump, validate

from app.models.city_model import Cities
from app.models.user_model import ACCESS_LEVEL, Roles
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


class UserSchema(CustomSchema):
    id = fields.Str(dump_only=True)
    firstName = fields.Str(required=True, validate=validate.Length(min=1, max=64))
    lastName = fields.Str(required=True, validate=validate.Length(min=1, max=64))
    email = fields.Email(required=True, max=256)


class ParticipantSchema(UserSchema):
    workshopParticipations = fields.List(fields.Str(), dump_only=True)


class CoachSchema(UserSchema):
    password = fields.Str(
        required=True, validate=validate.Length(min=8), load_only=True
    )
    city = fields.Str(
        required=True, validate=validate.OneOf(choices=[city.value for city in Cities])
    )
    role = fields.Str(
        required=True,
        validate=validate.OneOf(choices=[Roles.COACH.value, Roles.ADMIN.value]),
    )
    workshopsCount = fields.Integer(default=0)
    awarenessRaisedCount = fields.Integer(default=0)

    @pre_dump
    def stringify_role(self, in_data, **kwargs):
        in_data["role"] = max(
            {k: v for k, v in ACCESS_LEVEL.items() if k in in_data["role"]}.items(),
            key=lambda x: x[1],
        )[0]
        return in_data


class PersonaSchema(CustomSchema):
    id = fields.Str(dump_only=True)
    firstName = fields.Str(required=True, validate=validate.Length(min=1, max=64))
    lastName = fields.Str(required=True, validate=validate.Length(min=1, max=64))
    description = fields.Str(required=False)
    surveyVariables = fields.Dict(keys=fields.Str())

    @pre_dump
    def rename_carbon_form_answers(self, data, **kwargs):
        data.surveyVariables = data.carbonFormAnswers
        return data
