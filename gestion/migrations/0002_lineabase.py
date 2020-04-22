# Generated by Django 3.0.5 on 2020-04-21 02:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LineaBase',
            fields=[
                ('idLB', models.AutoField(primary_key=True, serialize=False)),
                ('nombreLB', models.CharField(max_length=50, verbose_name='Nombre de Linea Base')),
                ('idFase', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gestion.Fase')),
                ('items', models.ManyToManyField(to='gestion.Item')),
            ],
            options={
                'ordering': ['nombreLB'],
            },
        ),
    ]
