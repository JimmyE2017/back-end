from marshmallow import Schema, ValidationError

from app.common.errors import EmptyBodyError, InvalidDataError


class CustomSchema(Schema):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def loads_or_400(self, data: bytes) -> (dict, dict, int):
        if len(data) == 0:
            raise EmptyBodyError

        # Validate data
        try:
            data = self.loads(data)
        except ValidationError as e:
            raise InvalidDataError(details=e.messages)

        return data, None, 200
