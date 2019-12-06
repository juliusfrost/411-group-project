from django.db import models
from django.contrib.postgres.fields import JSONField

class EatSession(models.Model):
    session_id = models.TextField(primary_key=True)
    timeframe = models.TextField()
    locked = models.BooleanField()
    name = models.TextField()
    location = models.TextField()
    comments = JSONField()

    class Meta:
        db_table = 'eat_sessions'
