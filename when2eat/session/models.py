from django.db import models

class EatSession(models.Model):
    session_id = models.TextField(primary_key=True)
    timeframe = models.TextField()
    locked = models.BooleanField()

    class Meta:
        db_table = 'eat_sessions'
