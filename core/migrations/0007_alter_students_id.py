# Generated by Django 5.0.4 on 2024-05-30 09:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_alter_coruseschedules_id_alter_studentsreg_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='students',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]