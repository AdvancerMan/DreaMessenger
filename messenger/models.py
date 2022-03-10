from django.contrib.auth.models import User
from django.db import models


class Dialogue(models.Model):
    users = models.ManyToManyField(User, related_name='dialogues')
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str([user.username for user in self.users.all()])


class Message(models.Model):
    dialogue = models.ForeignKey(Dialogue, on_delete=models.CASCADE, related_name='messages')
    from_user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='messages', blank=True, null=True)
    picture = models.BinaryField(max_length=1024 * 1024, editable=True)
    is_edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
