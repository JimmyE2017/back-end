from marshmallow import Schema, ValidationError

from app.common.errors import EMPTY_BODY_ERROR, INVALID_DATA_ERROR


class CustomSchema(Schema):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def loads_or_400(self, data: bytes) -> (dict, dict, int):
        if len(data) == 0:
            err_msg, err_code = EMPTY_BODY_ERROR.get_error()
            return None, err_msg, err_code

        # Validate data
        try:
            data = self.loads(data)
        except ValidationError as e:
            err_msg, err_code = INVALID_DATA_ERROR.get_error()
            err_msg.update({"details": e.messages})
            return None, err_msg, err_code

        return data, None, 200
