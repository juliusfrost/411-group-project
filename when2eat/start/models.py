from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField

class UserProfile(models.Model):
    id = models.OneToOneField(User, on_delete=models.CASCADE,
                                primary_key=True)
    session = models.ForeignKey("session.EatSession", null=True, on_delete=models.SET_NULL)
    host = models.BooleanField(null = True)
    availability = JSONField(null = True)
    preferences = JSONField(null = True)

    class Meta:
        db_table = 'user_profile'
