from django.db import models


class EmailAccount(models.Model):
    login = models.EmailField(unique=True)
    password = models.CharField(max_length=255)


class Message(models.Model):
    subject = models.CharField(max_length=255)
    sent_date = models.DateTimeField()
    received_date = models.DateTimeField()
    body = models.TextField()
    attachments = models.JSONField(default=list)  # Список прикрепленных файлов

