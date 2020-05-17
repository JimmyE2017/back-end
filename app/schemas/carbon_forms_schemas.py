from marshmallow import ValidationError, fields, post_load, pre_dump

from app.schemas import CustomSchema


class CarbonFormAnswersSchema(CustomSchema):
    id = fields.Str(dump_only=True)
    workshopId = fields.Str(dump_only=True)
    participantId = fields.Str(dump_only=True)
    email = fields.Email(load_only=True)
    answers = fields.Dict(keys=fields.Str(), required=True)

    @post_load
    def check_answers_value(self, data, **kwargs):
        for value in data["answers"].values():
            if isinstance(value, dict) or isinstance(value, list):
                raise ValidationError(
                    "Answers value should only be nunbers or string", "answers"
                )
        return data

    @pre_dump
    def fetch_ids(self, data, **kwargs):
        data.workshopId = data.workshop.pk
        data.participantId = data.participant.pk
        return data
