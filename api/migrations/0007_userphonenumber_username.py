# Generated by Django 5.0.1 on 2024-06-10 15:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_users_biographie_alter_userphonenumber_value'),
    ]

    operations = [
        migrations.AddField(
            model_name='userphonenumber',
            name='username',
            field=models.CharField(default='', max_length=25),
        ),
    ]
