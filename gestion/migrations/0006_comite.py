# Generated by Django 3.0.4 on 2020-04-12 02:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0005_auto_20200411_0931'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comite',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('id_proyecto', models.IntegerField()),
                ('id_user', models.IntegerField()),
            ],
        ),
    ]
