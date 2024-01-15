# Generated by Django 4.2 on 2024-01-15 12:42

import datetime
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('admin_panel', '0002_initial'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PointRecord',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('record_date', models.DateField(default=datetime.date(2024, 1, 15))),
                ('timestamp', models.DateTimeField(default=datetime.datetime(2024, 1, 15, 6, 42, 51, 89771))),
                ('point_total', models.IntegerField(default=0)),
                ('contest_criterion', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='admin_panel.contestcriterion')),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='contest_person_points', to='core.contestperson')),
                ('polymorphic_ctype', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='polymorphic_%(app_label)s.%(class)s_set+', to='contenttypes.contenttype')),
            ],
            options={
                'ordering': ('-record_date',),
                'unique_together': {('person', 'contest_criterion', 'record_date')},
            },
        ),
        migrations.CreateModel(
            name='CheckboxPointRecord',
            fields=[
                ('pointrecord_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='member_panel.pointrecord')),
                ('checked', models.BooleanField(verbose_name=False)),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('member_panel.pointrecord',),
        ),
        migrations.CreateModel(
            name='MultiCheckboxPointRecord',
            fields=[
                ('pointrecord_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='member_panel.pointrecord')),
                ('choices', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=200), blank=True, default=list, size=None)),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('member_panel.pointrecord',),
        ),
        migrations.CreateModel(
            name='NumberPointRecord',
            fields=[
                ('pointrecord_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='member_panel.pointrecord')),
                ('number', models.IntegerField(default=0)),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('member_panel.pointrecord',),
        ),
        migrations.CreateModel(
            name='RadioPointRecord',
            fields=[
                ('pointrecord_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='member_panel.pointrecord')),
                ('choice', models.CharField(default='', max_length=200)),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('member_panel.pointrecord',),
        ),
        migrations.CreateModel(
            name='UserInputPointRecord',
            fields=[
                ('pointrecord_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='member_panel.pointrecord')),
                ('user_input', models.TextField(default='', max_length=1024)),
                ('reviewed_by_admin', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('member_panel.pointrecord',),
        ),
    ]
