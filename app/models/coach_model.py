from mongoengine.queryset.queryset import QuerySet

from app.models import db
from app.models.user_model import Roles, UserModel


class CoachModel(UserModel):
    city = db.StringField(max_length=256, required=True)
    workshopsCount = db.IntField(default=0)
    awarenessRaisedCount = db.IntField(default=0)

    _list_fields_subset = ["userId", "firstName", "lastName", "role", "email", "city"]

    @classmethod
    def find_all_coaches(cls) -> QuerySet:
        return (
            cls.objects(role__in=[Roles.ADMIN.value, Roles.COACH.value])
            .only(*cls._list_fields_subset)
            .all()
        )
