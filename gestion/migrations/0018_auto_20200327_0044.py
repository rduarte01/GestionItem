# Generated by Django 3.0.4 on 2020-03-27 00:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0017_auto_20200326_2307'),
    ]

    operations = [
        migrations.AlterField(
            model_name='atributo',
            name='ti',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gestion.TipoItem'),
        ),
    ]
