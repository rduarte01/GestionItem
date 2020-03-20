from django.db import models

from django.contrib.auth.models import User
#    Proyecto= models.ForeignKey(Proyecto, null=False, blank=False)

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

    """
    MENU---> GERENTE, ADMINISTRADOR, USUARIO SIN SER ACEPTADO, USUARIO ACEPTADO
    PLANTILLA
        
    """