# Generated by Django 3.0.5 on 2020-04-22 14:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0003_item_estado'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='item',
            options={'ordering': ['id_item'], 'verbose_name': 'Item', 'verbose_name_plural': 'Items'},
        ),
        migrations.AlterModelOptions(
            name='lineabase',
            options={'ordering': ['nombreLB'], 'verbose_name': 'Linea Base', 'verbose_name_plural': 'Lineas Base'},
        ),
        migrations.AddField(
            model_name='lineabase',
            name='estado',
            field=models.CharField(choices=[('Cerrada', 'Cerrada'), ('Rota', 'Rota'), ('Comprometida', 'Comprometida')], default='Cerrada', max_length=50, verbose_name='Estado'),
        ),
    ]