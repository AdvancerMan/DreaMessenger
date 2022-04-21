# Generated by Django 4.0.2 on 2022-04-21 14:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('messenger', '0007_remove_message_picture_message_picture_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='picture_id',
        ),
        migrations.AddField(
            model_name='message',
            name='picture',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='messages', to='messenger.picturev2'),
        ),
    ]