from email.policy import default

from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class TipoItem(models.Model):
    """"
        Este es el modelo Tipo de  item, con dos atributos id como primary key  y nombre como string
    """


    id_ti = models.AutoField(primary_key=True,default=1)
    nombre = models.CharField(max_length=20, default="Nombre Para el tipo de Item", help_text='Nombre del Tipo de Item')

    class Meta:
        permissions = (
            ("importar_tipo_item", "Poder importar Tipo Item"),
            ("crear_tipo_item", "Puede crear un Tipo de Item"),
        )
        ordering=['nombre']


class Atributo(models.Model):
    """"
       Este es el modelo Atributo, que se relaciona con Tipo de Item
    """

    choises_data_type = (
        ("Decimal", "Decimal"),
        ("Date", "Date"),
        ("File", "File"),
        ("String", "Cadena"),
        ("Boolean", "Boolean")
    )
    id_atributo=models.AutoField(primary_key=True)
    nombre=models.CharField(max_length=20,default="atriuto",help_text='Nombre del atributo del Tipo de Item')
    es_obligatorio= models.BooleanField(default=True)
    tipo_dato=models.CharField(max_length=8,choices=choises_data_type,default='Decimal')
    ti=models.ForeignKey(TipoItem,on_delete=models.CASCADE)
    class Meta:
        ordering=['nombre']
