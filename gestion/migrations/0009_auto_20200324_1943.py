# Generated by Django 3.0.4 on 2020-03-24 19:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0008_auto_20200322_0547'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='proyecto',
            options={'permissions': (('is_gerente', 'Puede hacer todas las actividades relacionadas con el geren'),)},
        ),
    ]
