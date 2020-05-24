from marshmallow import Schema, ValidationError

from app.common.errors import EmptyBodyError, InvalidDataError


class CustomSchema(Schema):
    class Meta:
        ordered = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def loads_or_400(self, data: bytes, **kwargs) -> (dict, dict, int):
        if len(data) == 0:
            raise EmptyBodyError

        # Validate data
        try:
            data = self.loads(data, **kwargs)
        except ValidationError as e:
            raise InvalidDataError(details=e.messages)

        return data, None, 200
