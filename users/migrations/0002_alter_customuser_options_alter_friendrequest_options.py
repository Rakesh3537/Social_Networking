# Generated by Django 5.0 on 2024-06-06 17:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customuser',
            options={'ordering': ['email']},
        ),
        migrations.AlterModelOptions(
            name='friendrequest',
            options={'ordering': ['created_at']},
        ),
    ]
