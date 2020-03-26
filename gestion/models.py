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

    choises_data_type = (
        ("CREADO", "CREADO"),
        ("INICIADO", "INICIADO"),
        ("FINALIZADO", "FINALIZADO"),
        ("CANCELADO", "CANCELADO")
    )


    id_proyecto= models.AutoField(primary_key = True) ###### clave de proyecto
    """SERA EL IDENTIFICADOR PARA DIFERENCIAR EN LA BD"""
    nombre= models.CharField(max_length=30)
    """SERA EL NOMBRE DEL PROYECTO A CREAR"""
    descripcion= models.CharField(max_length=100)
    """INFORMACION REFERENTE AL PROYECTO A CREAR"""
    estado= models.CharField('Estado', max_length = 10, blank = False, null = False, choices = choises_data_type, default = 'CREADO')
    """EL ESTADO DEL PROYECTO SEGUN AVANCE ESTARA VARIANDO, POR DEFAULT QUEDA EN CREADO"""
    users= models.ManyToManyField(User, blank=True)
    ###-Fases: Fases[*]
    ###-Rol: Rol[*]


class Fase(models.Model):
    """Se tiene el modelo fase, el cual será utilizado en el proyecto para albergar a los items y poder
    dividirlos en etapas.
    Las fases tendrán dos estados: Abierta y Cerrada, por defecto adoptará el estado de Abierto."""

    choises_data_type = (
        ("Abierta", "Abierta"),
        ("Cerrada", "Cerrada")
    )

    id_Fase = models.AutoField(primary_key = True)
    nombre = models.CharField('Nombre', max_length = 100, blank = False, null = False)
    descripcion = models.TextField('Descripción', blank = False, null = False)
    estado = models.CharField('Estado', max_length = 10, blank = False, null = False, choices = choises_data_type, default = 'Abierta')
    id_Proyecto = models.ForeignKey(Proyecto, on_delete = models.CASCADE)
    #TI = [*]
    #ti = models.ForeignKey(TipoItem, on_delete = models.CASCADE, blank = True, null = True)
    #id_Rol = models.ManyToMany(Rol)
    #Falta agregar relacion con LB e Item, cada uno de ellos en los modelos respectivos como FK

    class Meta:
        """Las fases son manejadas por roles, por tanto, el modelo Fase tiene sus respectivos roles, los cuales seran
        iguales para todas las fases de un proyecto, la diferencia radica en el usuario que posea un determinado rol ya
        que los mismos se manejan por fases. En conclusión: Un usuario puede tener un rol solamente en una fase o en
        varias fases, esto depende del gerente el proyecto, quien es el encargado de asignar los roles a los usuarios"""

    permissions = (
        ("Poder Aprobar Fase", "Aprobar Fase"),
        ("Poder Crear Fase", "Crear Fase")
    )
    verbose_name = 'Fase'
    verbose_name_plural = 'Fases'
    ordering = ['id_Fase']


class Auditoria(models.Model):
    """TABLA EN DONDE SE GUARDAN LAS MODIFICACIONES QUE REALIZAN TODOS LOS USUARIOS EN EL SISTEMA"""
    usuario= models.CharField(max_length=50)
    fecha= models.CharField(max_length=50)
    accion= models.CharField(max_length=100)

class User_Proyecto(models.Model):
    """MODELO PROYECTO CON USER EN DONDE SE SOLUCIONA LA RELACION MUCHOS A MUCHOS, GUARDA
    LAS RELACIONES ENTRE USUARIOS Y PROYECTOS
    """
    user_id = models.IntegerField()
    proyecto_id = models.IntegerField()
    activo = models.BooleanField(default=False)
