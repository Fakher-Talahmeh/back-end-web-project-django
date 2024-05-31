# Generated by Django 5.0.4 on 2024-05-30 12:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_alter_students_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notification',
            name='course_name',
        ),
        migrations.RemoveField(
            model_name='notification',
            name='start_time',
        ),
        migrations.AddField(
            model_name='notification',
            name='message',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='notification',
            name='title',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]