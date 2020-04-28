from marshmallow import ValidationError, fields, post_load, validate

from app.models.action_card_model import ActionCardModel, ActionCardType
from app.schemas import CustomSchema


class ActionCardSchema(CustomSchema):
    actionCardId = fields.Str(dump_only=True)
    number = fields.Integer(strict=True, validate=validate.Range(min=1))
    title = fields.Str(validate=validate.Length(min=1, max=256))
    category = fields.Str(validate=validate.Length(min=1, max=64))
    type = fields.Str(validate=validate.Length(min=1, max=64))
    key = fields.Str(validate=validate.Length(min=1, max=128))
    sector = fields.Str(validate=validate.Length(min=1, max=64))
    cost = fields.Integer(strict=True, validate=validate.Length(min=0))


class ActionCardBatchSchema(CustomSchema):
    actionCardBatchId = fields.Str()
    number = fields.Integer(strict=True, validate=validate.Range(min=1))
    title = fields.Str()
    actionCardIds = fields.List(fields.Str(), validate=validate.Length(min=1))
    type = fields.Str(
        validate=validate.OneOf(
            choices=[action_card_type.value for action_card_type in ActionCardType]
        )
    )

    @post_load(pass_many=True)
    def check_action_card_ids(self, data, many, **kwargs):
        existing_action_cards = {
            k.id: k.type for k in ActionCardModel.objects().only("actionCardId", "type")
        }

        for d in data:
            # Check that all ids are valid id
            for action_card_id in d["actionCardIds"]:
                if action_card_id not in existing_action_cards:
                    raise ValidationError(
                        "actionCardId {} does not exist. (Batch {})".format(
                            action_card_id, d["title"]
                        ),
                        "actionCardIds",
                    )
            # Check that each batch always are the same type
            if (
                len(
                    set(
                        [
                            existing_action_cards[action_card_id]
                            for action_card_id in d["actionCardIds"]
                        ]
                    )
                )
                > 1
            ):
                raise ValidationError(
                    "Action cards within the same batch must be of the same type. "
                    "(Batch {})".format(d["title"]),
                    "actionCardIds",
                )

        # Check that all the action ids are present
        missing_action_card_ids = set(
            [k for k in existing_action_cards.keys()]
        ) - set().union(*[d["actionCardIds"] for d in data])
        if len(missing_action_card_ids) > 0:
            raise ValidationError(
                "All actions cards need to be present. Missing {}".format(
                    ", ".join(missing_action_card_ids)
                ),
                "actionCardIds",
            )

        return data
