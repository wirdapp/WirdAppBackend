# Generated by Django 4.2 on 2024-02-06 00:45

from django.db import migrations, models
from datetime import datetime


def copy_data(apps, schema_editor):
    contest_model = apps.get_model('core', 'contest')
    for instance in contest_model.objects.all():
        announcements = instance.announcements if instance.announcements else {}
        data = {}
        for announcement in announcements:
            data.update({f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}": announcement})

        instance.announcements1 = data
        instance.save()


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='contest',
            name='announcements1',
            field=models.JSONField(default=dict),
        ),
        migrations.RunPython(copy_data),
        migrations.RemoveField(
            model_name='contest',
            name='announcements',
        ),
        migrations.RenameField(
            model_name='contest',
            old_name='announcements1',
            new_name='announcements'
        ),
    ]
