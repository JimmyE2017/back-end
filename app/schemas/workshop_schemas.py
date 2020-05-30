from marshmallow import (
    ValidationError,
    fields,
    post_dump,
    post_load,
    pre_dump,
    validate,
)

from app.models.action_card_model import ActionCardType
from app.models.workshop_model import (
    WorkshopModel,
    WorkshopRoundCarbonFootprintModel,
    WorkshopRoundCarbonVariablesModel,
    WorkshopRoundCollectiveChoicesModel,
    WorkshopRoundConfigModel,
    WorkshopRoundIndividualChoicesModel,
    WorkshopRoundModel,
)
from app.schemas import CustomSchema
from app.schemas.action_card_schemas import ActionCardBatchSchema, ActionCardSchema
from app.schemas.user_schemas import ParticipantSchema, PersonaSchema


class WorkshopSchema(CustomSchema):
    id = fields.Str(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=128))
    startAt = fields.AwareDateTime(required=True)
    creatorId = fields.Str(dump_only=True)
    coachId = fields.Str(required=True, validate=validate.Length(min=1))
    city = fields.Str(required=True, validate=validate.Length(max=128))
    address = fields.Str(validate=validate.Length(max=512))
    eventUrl = fields.Str(validate=validate.Length(max=1024))


class WorkshopParticipantSchema(CustomSchema):
    status = fields.Str()
    user = fields.Nested(
        ParticipantSchema, only=("id", "firstName", "lastName", "email")
    )
    surveyVariables = fields.Dict(keys=fields.Str())

    @post_dump
    def flatten_participant(self, data, **kwargs):
        data = {**data["user"], **data}
        del data["user"]
        return data


class WorkshopModelSchema(CustomSchema):
    id = fields.Str()
    footprintStructure = fields.Dict()
    variableFormulas = fields.Dict()
    globalCarbonVariables = fields.Dict()
    actionCards = fields.List(fields.Nested(ActionCardSchema))
    actionCardBatches = fields.List(fields.Nested(ActionCardBatchSchema))
    personas = fields.List(fields.Nested(PersonaSchema))

    @post_dump
    def rename_fk(self, data, **kwargs):
        for d in data["actionCards"]:
            d["actionCardId"] = d.pop("id")
        for d in data["actionCardBatches"]:
            d["actionCardBatchId"] = d.pop("id")
        for d in data["personas"]:
            d["personaId"] = d.pop("id")
        return data


class CarbonFootprintSchema(CustomSchema):
    participantId = fields.Str(required=True)
    footprint = fields.Dict()

    @pre_dump
    def fetch_id(self, data, **kwargs):
        data.participantId = data.participant.pk
        return data

    @post_load
    def make_object(self, data, **kwargs):
        data["participant"] = data.pop("participantId")  # Rename key
        return WorkshopRoundCarbonFootprintModel(**data)


class CarbonVariablesSchema(CustomSchema):
    participantId = fields.Str(required=True)
    variables = fields.Dict()

    @pre_dump
    def fetch_id(self, data, **kwargs):
        data.participantId = data.participant.pk
        return data

    @post_load
    def make_object(self, data, **kwargs):
        data["participant"] = data.pop("participantId")  # Rename key
        return WorkshopRoundCarbonVariablesModel(**data)


class WorkshopRoundConfigSchema(CustomSchema):
    actionCardType = fields.Str(
        required=True,
        validate=validate.OneOf(choices=[t.value for t in ActionCardType]),
    )
    targetedYear = fields.Int(required=True)
    budget = fields.Int(required=True)
    actionCardBatchIds = fields.List(fields.Str())

    @pre_dump
    def fetch_id(self, data, **kwargs):
        data.actionCardBatchIds = [acb.pk for acb in data.actionCardBatches]
        return data

    @post_load
    def make_object(self, data, **kwargs):
        data["actionCardBatches"] = data.pop("actionCardBatchIds")
        return WorkshopRoundConfigModel(**data)


class WorkshopRoundCollectiveChoicesSchema(CustomSchema):
    actionCardIds = fields.List(fields.Str())

    @pre_dump
    def fetch_ids(self, data, **kwargs):
        data.actionCardIds = [acb.pk for acb in data.actionCards]
        return data

    @post_load
    def make_object(self, data, **kwargs):
        data["actionCards"] = data.pop("actionCardIds")
        return WorkshopRoundCollectiveChoicesModel(**data)


class WorkshopRoundIndividualChoicesSchema(CustomSchema):
    participantId = fields.Str(required=True)
    actionCardIds = fields.List(fields.Str())

    @pre_dump
    def fetch_ids(self, data, **kwargs):
        data.participantId = data.participant.pk
        data.actionCardIds = [acb.pk for acb in data.actionCards]
        return data

    @post_load
    def make_object(self, data, **kwargs):
        data["participant"] = data.pop("participantId")
        data["actionCards"] = data.pop("actionCardIds")
        return WorkshopRoundIndividualChoicesModel(**data)


class WorkshopRoundSchema(CustomSchema):
    year = fields.Integer(strict=True, required=True)
    carbonVariables = fields.List(fields.Nested(CarbonVariablesSchema), required=True)
    carbonFootprints = fields.List(fields.Nested(CarbonFootprintSchema), required=True)
    roundConfig = fields.Nested(WorkshopRoundConfigSchema)
    globalCarbonVariables = fields.Dict(keys=fields.Str())
    individualChoices = fields.List(fields.Nested(WorkshopRoundIndividualChoicesSchema))
    collectiveChoices = fields.Nested(WorkshopRoundCollectiveChoicesSchema)

    @post_dump
    def clean_choices(self, data, **kwargs):
        # Remove individualChoices or collectiveChoices if they are None
        if data["individualChoices"] is None:
            del data["individualChoices"]
        if data["collectiveChoices"] is None:
            del data["collectiveChoices"]
        return data

    @post_load
    def make_object(self, data, **kwargs):
        return WorkshopRoundModel(**data)


class WorkshopDetailSchema(WorkshopSchema):
    startYear = fields.Integer(strict=True)
    endYear = fields.Integer(strict=True)
    yearIncrement = fields.Integer(strict=True, validate=validate.Range(min=1))

    participants = fields.List(fields.Nested(WorkshopParticipantSchema))
    model = fields.Nested(WorkshopModelSchema, dump_only=True)
    rounds = fields.List(fields.Nested(WorkshopRoundSchema))

    @classmethod
    def validate_partipant_id_in_rounds(cls, data, participant_ids, **kwargs):
        for workshop_round in data["rounds"]:
            for cv in workshop_round.carbonVariables:
                if cv.participant.pk not in participant_ids:
                    raise ValidationError(
                        f"Invalid participant id in round {workshop_round.year}'s"
                        f" carbonVariables : {cv.participant.pk}",
                        "carbonVariables",
                    )
            for cf in workshop_round.carbonFootprints:
                if cf.participant.pk not in participant_ids:
                    raise ValidationError(
                        f"Invalid participant id in round {workshop_round.year}'s"
                        f" carbonFootprints : {cf.participant.pk}",
                        "carbonFootprints",
                    )
        return data

    @post_dump
    def rename_fk(self, data, **kwargs):
        data["model"]["modelId"] = data["model"].pop("id")
        for d in data["participants"]:
            d["participantId"] = d.pop("id")
        return data

    @post_load
    def make_object(self, data, **kwargs):
        return WorkshopModel(**data)
