from email.policy import default
from django.db import models
from django.contrib.auth.models import User


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

class Proyecto(models.Model):
    """
    PRIMARY_KEY AUTOMATICO A MEDIDA QUE SE AGREGA PROYECTOS
    MODELO DE PROYECTO GUARDARA EL NOMBRE, DESCRIPCION, LISTA DE USUARIOS AÑADIDOS A EL
    LA LISTA DE FASES QUE PERTENECEN AL MISMO,
    UN ESTADO QUE SERA IDENTIFICADO EN LA BD COMO
    CREADO=1
    INICIADO=2
    FINALIZADO=3
    CANCELADO=4
    POR ULTIMO SE TENDRA LA LISTA DE ROLES QUE PERTENECEN AL PROYECTO
    """
    #id_proyecto= models.IntegerField(auto_created = True, primary_key = True, serialize = False) ###### clave de proyecto
    id_proyecto= models.IntegerField(primary_key = True)
    nombre= models.CharField(max_length=30)#####3required=false para que no sea obligatorio
    descripcion= models.CharField(max_length=100)
    ###-Usuarios: Usuario[*]    FALTA CREAR
    ###-Fases: Fases[*]
    estado= models.IntegerField()
    ###-Rol: Rol[*]
    usuario = models.ManyToManyField(User)

