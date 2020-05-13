from datetime import datetime

from flask_jwt_extended import get_jwt_identity

from app.common.errors import EntityNotFoundError, PermissionDeniedError
from app.models.action_card_model import ActionCardBatchModel, ActionCardModel
from app.models.user_model import UserModel
from app.schemas.action_card_schemas import ActionCardBatchSchema, ActionCardSchema


def get_all_action_cards() -> (dict, int):
    action_cards = ActionCardModel.find_all()
    return ActionCardSchema(many=True).dump(action_cards), 200


def get_coach_action_card_batches(coach_id: str) -> (dict, int):
    # Check if given coach_id exists in DB
    coach = UserModel.find_coach_by_id(user_id=coach_id)
    if coach is None:
        raise EntityNotFoundError

    # Retrieve data
    data = ActionCardBatchModel.find_action_card_batches_by_coach(coach_id)
    return ActionCardBatchSchema(many=True).dump(data), 200


def update_coach_action_card_batches(coach_id: str, data: bytes) -> (dict, int):
    # Check if given coach_id exists in DB
    coach = UserModel.find_coach_by_id(user_id=coach_id)
    if coach is None:
        raise EntityNotFoundError(msg="Coach does not exist")

    # Prevent another coach from updating another coach action card batches
    if coach_id != get_jwt_identity():
        raise PermissionDeniedError(
            msg="You can't update the action card batches of another coach !"
        )

    # Validate and serialize data
    schema = ActionCardBatchSchema(many=True)
    data, err_msg, err_code = schema.loads_or_400(data)
    if err_msg:
        return err_msg, err_code

    # Retrieve current action card batches
    current_action_card_batches = {
        o.actionCardBatchId: o
        for o in ActionCardBatchModel.find_action_card_batches_by_coach(coach_id)
    }

    # Process provided data
    output = []
    for d in data:
        if (
            "actionCardBatchId" in d
            and d["actionCardBatchId"] in current_action_card_batches
        ):
            # Update action card batch if already existing
            action_card_batch = current_action_card_batches[d["actionCardBatchId"]]
            for k, v in d.items():
                setattr(action_card_batch, k, v)
            action_card_batch.updatedAt = datetime.utcnow()
        else:
            # Create new object otherwise
            action_card_batch = ActionCardBatchModel(
                **{k: v for k, v in d.items() if k != "actionCardId"}
            )

        action_card_batch.coachId = coach_id
        action_card_batch.save()
        output.append(action_card_batch)

    new_ids = {o.id: None for o in output}
    # Delete current action card batches that are not in provided data
    for o_id, action_card_batch in current_action_card_batches.items():
        if o_id not in new_ids:
            action_card_batch.delete()

    return ActionCardBatchSchema(many=True).dump(output), 200
