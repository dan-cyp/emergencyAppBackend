# Generated by Django 4.1.7 on 2023-03-07 12:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('emergencyEvent', '0002_accessedtime'),
    ]

    operations = [
        migrations.AddField(
            model_name='emergencyevent',
            name='checked',
            field=models.BooleanField(default=False),
        ),
    ]