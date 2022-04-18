from django.contrib.auth.models import User
from django.db import models


class Dialogue(models.Model):
    users = models.ManyToManyField(User, related_name='dialogues')
    updated_at = models.DateTimeField(auto_now_add=True)
    is_tetatet = models.BooleanField(default=False)

    def __str__(self):
        return 'Dialogue ' + str([user.username for user in self.users.all()])


class Picture(models.Model):
    data = models.BinaryField(max_length=1024 * 1024, editable=True)

    def __str__(self):
        return f'Picture with id {self.pk}'


class Message(models.Model):
    dialogue = models.ForeignKey(Dialogue, on_delete=models.CASCADE, related_name='messages')
    from_user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='messages', blank=True, null=True)
    picture = models.ForeignKey(Picture, on_delete=models.SET_NULL, related_name='messages', blank=True, null=True)
    is_edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Message with id {self.pk} from {self.from_user.username} to dialogue {self.dialogue}'
