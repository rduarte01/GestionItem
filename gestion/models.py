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


class Fase(models.Model):
    """Se tiene el modelo fase, el cual será utilizado en el proyecto para albergar a los items y poder
    dividirlos en etapas.
    Las fases tendrán dos estados: Abierta y Cerrada, por defecto adoptará el estado de Abierto."""

    choises_data_type = (
        ("1", "Abierta")
        ("2", "Cerrada")
    )

    id_Fase = models.AutoField(primary_key = True, blank = False, null = False, default = 1)
    nombre = models.CharField(max_length = 100, blank = False, null = False)
    descripcion = models.TextField(blank = False, null = False)
    estado = models.CharField(max_length = 10, blank = False, null = False, choices = choises_data_type, default = 'Abierta')
    #id_Proyecto = models.ForeignKeyField(Proyecto, on_delete = models.CASCADE)
    #Items = [*]
    #TI = [*]
    #id_Rol = models.ManyToMany(Rol)
    #Falta agregar relacion con LB e Item, cada uno de ellos en los modelos respectivos como FK ID_Fase
    #PRESI, EN TU MODELO DE TI DEBE IR COMO FK EL ID_FASE

    class Meta:
        """Las fases son manejadas por roles, por tanto, el modelo Fase tiene sus respectivos roles, los cuales seran
        iguales para todas las fases de un proyecto, la diferencia radica en el usuario que posea un determinado rol ya
        que los mismos se manejan por fases. En conclusión: Un usuario puede tener un rol solamente en una fase o en
        varias fases, esto depende del gerente el proyecto, quien es el encargado de asignar los roles a los usuarios"""

        permissions = (
           '''
            ("Poder Crear Item", "Crear Item"),
            ("Poder Aprobar Item", "Aprobar Item"),
            ("Poder Crear LB", "Crear Linea Base"),
            ("Poder Modificar Atributo de Item", "Modificar Atributo de Item"),
            ("Poder Reversionar Item", "Reversionar Item"),
            ("Poder Aprobar Item", "Aprobar Item"),
            ("Poder Relacionar Item", "Relacionar Item"),
            ("Poder Generar Solicitud de Cambio", "Generar Solicitud de Cambio"),
            ("Poder Cambiar Estado de Item", "Cambiar Estado de Item"),
        '''
           ("cerrar_fase","Puede cerrar Fase"),

        )
        verbose_name = 'Fase'
        verbose_name_plural = 'Fases'
        ordering = ['id_Fase']