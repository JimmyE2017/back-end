from app.models.action_card_model import ActionCardModel
from app.schemas.action_card_schemas import ActionCardSchema


def get_all_action_cards() -> (dict, int):
    action_cards = ActionCardModel.find_all()
    schema = ActionCardSchema(many=True)
    return schema.dump(action_cards), 200
