from email.policy import default
from django.db import models
from django.contrib.auth.models import User,Group
from django.db.models.signals import post_save
from django.dispatch import receiver

class Proyecto(models.Model):
    """
    PRIMARY_KEY AUTOMATICO A MEDIDA QUE SE AGREGA PROYECTOS
    MODELO DE PROYECTO GUARDARA EL NOMBRE, DESCRIPCION, LISTA DE USUARIOS AÑADIDOS A EL
    LA LISTA DE FASES QUE PERTENECEN AL MISMO,
    UN ESTADO QUE SERA IDENTIFICADO EN LA BD COMO
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

    class Meta:
        """ SE AGREGAN DOS PERMISOS NECESARIOS, UNO PARA EL GERENTE Y OTRO PARA EL ADMINISTRADOR DEL SISTEMA"""
        permissions = (("is_gerente", "Permiso de gerente de proyectos"),
                       ("is_administradorSistema", "Permiso de Administrador del sistema"),
                       )


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
class TipoItem(models.Model):
    """"
        Este es el modelo Tipo de  item, con dos atributos id como primary key  y nombre como string
    """
    id_ti = models.AutoField(primary_key=True)
    ''' atributo que sive para identificar univocamente a cada tipo Item'''
    nombre = models.CharField(max_length=20)
    '''atributo que sirve para para almacenar el nombre del tipo de item'''
    fase=models.ForeignKey(Fase,on_delete=models.CASCADE,null=True,blank=True)
    ''' atributpp que sirve para hacer referencia de a que fase corresponde el tipo de  item'''
    class Meta:
        ''' Clase que sirve para proveer metadatos al modelo TipoItem'''
        permissions = (
            ("importar_tipo_item", "Poder importar Tipo Item"),
            ("crear_tipo_item", "Puede crear un Tipo de Item"),
        )
        '''en estas variables especificamos los permisos que vamos  tener para este modelo TipoItem'''
        ordering=['nombre']
        '''en este especificamos  como vamos a ordenar '''
class Atributo(models.Model):
    """"
       Este es el modelo Atributo, que se relaciona con Tipo de Item, y sirve para representa todos los valores
       debe de tener un atributo al crearlo
    """
    choises_data_type = (
        ("Decimal", "Decimal"),
        ("Date", "Date"),
        ("File", "File"),
        ("String", "Cadena"),
        ("Boolean", "Boolean"),
    )
    '''
        En esta variable especificamos, las opciones que se van a tener para especificar el tipo de dato del atributo
    '''
    id_atributo=models.AutoField(primary_key=True,blank=False)
    ''' variable que sirve para identificar univocamente a cada atributi'''
    nombre=models.CharField(max_length=20,blank=False)
    '''varible que sirve para almacena el nombre del atributo'''
    es_obligatorio= models.BooleanField(default=True,blank=False)
    '''variable que sirve para identificar si un atributo es obligatorio o no'''
    tipo_dato=models.CharField(max_length=8,choices=choises_data_type,default='Decimal',blank=False)
    ''' variable que sirve para almacenar el tipo de dato del atributo'''
    ti=models.ForeignKey(TipoItem,on_delete=models.CASCADE)
    '''variable que sirve para hacer referencia a que tipo de item esta asociado el atributo'''
    class Meta:
        '''Clase que provee meta datos de como para el modelo Atributo'''
        ordering=['nombre']
        '''para saber por que atibuto vamos a ordenar'''




class Auditoria(models.Model):
    """TABLA EN DONDE SE GUARDAN LAS MODIFICACIONES QUE REALIZAN TODOS LOS USUARIOS EN EL SISTEMA"""
    usuario= models.CharField(max_length=50)
    """GUARDA EL NOMBRE DE USUARIO"""
    fecha= models.CharField(max_length=50)
    """GUARDA LA FECHA DE LA ACCION"""
    accion= models.CharField(max_length=100)
    """GUARDA LA ACCION REALIZADA"""

class User_Proyecto(models.Model):
    """MODELO PROYECTO CON USER EN DONDE SE SOLUCIONA LA RELACION MUCHOS A MUCHOS, GUARDA
    LAS RELACIONES ENTRE USUARIOS Y PROYECTOS
    """
    user_id = models.IntegerField()
    """USER RELACIONADO CON PROYECTO"""
    proyecto_id = models.IntegerField()
    """PROYECTO RELACIONADO CON USER"""
    activo = models.BooleanField(default=False)
    """SI EL USUARIO ESTA ACTIVO EN EL PROYECTO, CASO CONTRARIO YA NO PERTENECE AL MISMO"""

class FASE_ROL(models.Model):
    id_fase=models.ForeignKey(Fase,on_delete=models.CASCADE)
    id_rol=models.ForeignKey(Group,on_delete=models.CASCADE)

#Ger
class Permisos(models.Model):
    """Modelo creado especificamente para la creacion
    de permisos dentro de un proyecto, para la asignacion
    a usuarios quienes no son gerentes del proyecto"""
    class Meta:
        default_permissions = ()
        permissions = (
            ("crear_item", "Puede Crear Item"),
            ("editar_item", "Puede Editar Item"),
            ("desactivar_item", "Puede Desactivar Item"),
            ("reversionar_item", "Puede Reversionar Item"),
            ("aprobar_item", "Puede Aprobar Item"),
            ("crear_lb", "Puede Crear LB"),
            ("cerrar_lb", "Puede Cerrar LB"),
            ("generar_solicitud", "Puede Generar Solicitud de Cambio"),


        )

class Usuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    esta_aprobado = models.BooleanField(
        default=False
    )
    class Meta:
        permissions = (
            ('es_administrador','Puede hacer tareas de Administrador'),
        )


'''
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
'''