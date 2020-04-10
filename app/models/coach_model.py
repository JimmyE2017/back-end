from mongoengine.queryset.queryset import QuerySet

from app.models.user_model import Roles, UserModel


class CoachModel(UserModel):
    @classmethod
    def find_all_coaches(cls) -> QuerySet:
        return cls.objects(role__in=[Roles.ADMIN.value, Roles.COACH.value]).all()
