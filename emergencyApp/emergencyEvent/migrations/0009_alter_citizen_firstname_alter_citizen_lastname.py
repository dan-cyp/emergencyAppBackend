# Generated by Django 4.1.7 on 2023-03-10 07:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('emergencyEvent', '0008_location_remove_emergencyevent_pos_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='citizen',
            name='firstName',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='citizen',
            name='lastName',
            field=models.CharField(max_length=255),
        ),
    ]
