# Generated by Django 5.0.1 on 2024-06-10 14:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_users_password'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserPhoneNumber',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('value', models.CharField(default='', max_length=15)),
                ('createdAt', models.DateTimeField(auto_now_add=True, null=True)),
                ('updatedAt', models.DateTimeField(auto_now=True, null=True)),
                ('userId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.users')),
            ],
        ),
    ]