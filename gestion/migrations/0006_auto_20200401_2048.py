# Generated by Django 3.0.4 on 2020-04-01 20:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0005_usuario'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='usuario',
            options={'permissions': (('es_administrador', 'Puede hacer tareas de Administrador'),)},
        ),
    ]
