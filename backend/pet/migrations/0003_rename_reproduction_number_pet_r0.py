# Generated by Django 5.0.3 on 2024-08-24 03:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pet', '0002_alter_pet_antiviral_effectiveness'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pet',
            old_name='reproduction_number',
            new_name='R0',
        ),
    ]
