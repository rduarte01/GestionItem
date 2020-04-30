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
    """DEFINE LAS OPCIONES DE LOS ESTADOS DEL PROYECTOS"""
    id_proyecto= models.AutoField(primary_key = True) ###### clave de proyecto
    """SERA EL IDENTIFICADOR PARA DIFERENCIAR EN LA BD"""
    nombre= models.CharField(max_length=30)
    """SERA EL NOMBRE DEL PROYECTO A CREAR"""
    descripcion= models.CharField(max_length=100)
    """INFORMACION REFERENTE AL PROYECTO A CREAR"""
    estado= models.CharField('Estado', max_length = 10, blank = False, null = False, choices = choises_data_type, default = 'CREADO')
    """EL ESTADO DEL PROYECTO SEGUN AVANCE ESTARA VARIANDO, POR DEFAULT QUEDA EN CREADO"""

    class Meta:
        """ SE AGREGAN DOS PERMISOS NECESARIOS, UNO PARA EL GERENTE Y OTRO PARA EL ADMINISTRADOR DEL SISTEMA"""
        permissions = (("is_gerente", "Permiso de gerente de proyectos"),
                       ("is_administradorSistema", "Permiso de Administrador del sistema"),
                        ("crear_item", "Puede Crear Item"),
                        ("editar_item", "Puede Editar Item"),
                        ("desactivar_item", "Puede Desactivar Item"),
                        ("reversionar_item", "Puede Reversionar Item"),
                        ("aprobar_item", "Puede Aprobar Item"),
                        ("crear_lb", "Puede Crear LB"),
                        ("cerrar_lb", "Puede Cerrar LB"),
                        ("generar_solicitud", "Puede Generar Solicitud de Cambio"),

                )
        """DEFINE LOS PERMISOS DEL MODELO PROYECTO"""

class Fase(models.Model):
    """Se tiene el modelo fase, el cual será utilizado en el proyecto para albergar a los items y poder
    dividirlos en etapas.
    Las fases tendrán dos estados: Abierta y Cerrada, por defecto adoptará el estado de Abierto."""

    choises_data_type = (
        ("Abierta", "Abierta"),
        ("Cerrada", "Cerrada")
    )
    """DEFINE LOS ESTADOS DEL MODELO FASE"""

    id_Fase = models.AutoField(primary_key = True)
    """ID DE LA FASE"""
    nombre = models.CharField('Nombre', max_length = 100, blank = False, null = False)
    """GUARDA EL NOMBRE DE LA FASE"""
    descripcion = models.TextField('Descripción', blank = False, null = False)
    """GUARDA LA DESCRIPCION DE LA FASE"""
    estado = models.CharField('Estado', max_length = 10, blank = False, null = False, choices = choises_data_type, default = 'Abierta')
    """GUARDA EL ESTADO DE LA FASE"""
    id_Proyecto = models.ForeignKey(Proyecto, on_delete = models.CASCADE)
    """SSE RELACIONA LA FASE CON EL PROYECTO"""
    #TI = [*]
    #ti = models.ForeignKey(TipoItem, on_delete = models.CASCADE, blank = True, null = True)
    #id_Rol = models.ManyToMany(Rol)
    #Falta agregar relacion con LB e Item, cada uno de ellos en los modelos respectivos como FK

    class Meta:
        """Las fases son manejadas por roles, por tanto, el modelo Fase tiene sus respectivos roles, los cuales seran
        iguales para todas las fases de un proyecto, la diferencia radica en el usuario que posea un determinado rol ya
        que los mismos se manejan por fases. En conclusión: Un usuario puede tener un rol solamente en una fase o en
        varias fases, esto depende del gerente el proyecto, quien es el encargado de asignar los roles a los usuarios"""

    """PERMISOS QUE REQUIERE FASE"""
    verbose_name = 'Fase'
    """NOMBRE DEL MODELO DENTRO DE ADMIN"""
    verbose_name_plural = 'Fases'
    """NOMBRE DEL MODELO DENTRO DE ADMIN"""
    ordering = ['id_Fase']
    """ORDENA POR ID DE FASE"""

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

    def __str__(self):
        return '{}'.format(self.nombre)


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
    usuario = models.CharField(max_length=50)
    """GUARDA EL NOMBRE DE USUARIO"""
    fecha = models.CharField(max_length=50)
    """GUARDA LA FECHA DE LA ACCION"""
    accion = models.CharField(max_length=100)
    """GUARDA LA ACCION REALIZADA"""
    proyecto = models.CharField(max_length=100, null=True)
    """PARA FILTRAR AUDITORIA DE UN PROYECTO EN ESPECIFICO"""
    id_proyecto = models.IntegerField(null=True)
    """PARA FILTRAR AUDITORIA DE UN PROYECTO EN ESPECIFICO"""
    fase = models.CharField(max_length=100, null=True)
    """PARA FILTRAR AUDITORIA DE UN PROYECTO EN ESPECIFICO"""

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
    """TABLA QUE RELACIONARA LA FASE CON EL ROL"""
    id_fase=models.ForeignKey(Fase,on_delete=models.CASCADE)
    """ID FASE"""
    id_rol=models.ForeignKey(Group,on_delete=models.CASCADE)
    """ID DEL ROL"""
    id_usuario=models.ForeignKey(User,on_delete=models.CASCADE,default=0)

#Ger
class Permisos(models.Model):
    """Modelo creado especificamente para la creacion
    de permisos dentro de un proyecto, para la asignacion
    a usuarios quienes no son gerentes del proyecto"""
    class Meta:
        """DEFINE METADATOS PARA EL MODELO PERMISO"""
        default_permissions = ()
        """PARA NO AÑADIR LOS PERMISOS POR DEFAULT DE DJANGO"""
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
        """LISTA DE PERMISOS ASOCIADOS AL PROYECTO"""

class Usuario(models.Model):
    """MODELO QUE SE UTILIZA PARA ALMACENAR EL ESTADO DEL USUARIO Y SU PERMISO"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    """HACE REFERENCIA AL MODELO USER DE DJANGO"""
    esta_aprobado = models.BooleanField(
        default=False
    )
    """VARIABLE QUE INDICA ESTADO DEL USUARIO EN EL SISTEMA"""
    class Meta:
        """DEFINE METADATOS PARA EL MODELO USUARIO"""
        permissions = (
            ('es_administrador','Puede hacer tareas de Administrador'),
        )
        """LISTA DE PERMISOS ASOCIADOS AL SISTEMA"""


class Item(models.Model):
    """MODELO DE ITEM"""

    choises_data_type = (
        ("Creado", "Creado"),
        ("Aprobado", "Aprobado"),
        ("Finalizado", "Finalizado"),
        ("En revision", "En revision")
        #Falta cancelado
    )
    """ESTADOS POSIBLES DE CADA UNO DE LOS ITEMS DEL PROYECTO, POR DEFECTO, AL CREAR UN ITEM TENDRA ESTADO CREADO"""

    id_item= models.AutoField(primary_key = True) ###### clave de proyecto
    """GUARDA EL ID DEL ITEM"""
    nombre= models.CharField(max_length=30)
    """NOMBRE DEL ITEM"""
    descripcion= models.CharField(max_length=100)
    """DESCRIPCION DEL ITEM"""
    costo=models.IntegerField()
    """COSTO DEL ITEM"""
    ti=models.ForeignKey(TipoItem, null=True ,on_delete = models.CASCADE)
    """TIPO DE ITEM QUE SE ASIGNARA AL ITEM"""
    fase=models.ForeignKey(Fase, on_delete = models.CASCADE)
    """FASE  A LA CUAL PERTENECE EL ITEM"""
    actual=models.BooleanField(default=True)
    """SI ESTA EN TRUE SERA QUE EL ITEM ESTA ACTIVO Y NO UNA VERSION ANTERIOR"""
    estado = models.CharField('Estado', max_length = 20, blank = False, null = False, choices = choises_data_type, default = 'Creado')
    """ATRIBUTO CORRESPONDIENTE AL ESTADO QUE ADOPTARÁ UN DETERMINADO ITEM, EL MISMO VARÍA DURANTE EL TRANSCURSO DEL PROYECTO SEGÚN LO QUE EL USUARIO DECIDA"""

    def __str__(self):
        """HACE REFERENCIA A LA MANERA EN LA CUAL QUEREMOS VISUALIZAR LOS ITEMS, EN ESTE CASO LOS VEREMOS POR SU NOMBRE, POR DEFECTO SE 
        VISUALIZA DE LA SIGUIENTE MANERA: ITEM OBJECT(1), ITEM OBJECT(2), Y ASÍ SUCESIVAMENTE. 
        """
        return self.nombre
        """SE VISUALIZA LOS ITEMS POR SU NOMBRE"""

class Relacion(models.Model):
    """MODELO DE RELACION DE ITEMS"""
    id_relacion= models.AutoField(primary_key = True) ###### clave de proyecto
    """ID DE RELACION"""
    inicio_item=models.IntegerField()
    """ITEM DE INICIO DE RELACION"""
    fin_item= models.IntegerField()
    """ITEM FIN DE RELACION"""


class Atributo_Item(models.Model):
    """MODELO DE ATRIBUTO DE TI, EN EL CUAL SE GUARDARA EL VALOR DEPENDIENDO DEL TI"""
    id_atributo= models.AutoField(primary_key = True) ###### clave de proyecto
    """ID DEL ATRIBUTO_Item"""
    idAtributoTI= models.ForeignKey(Atributo, on_delete = models.CASCADE)
    """ID DEL TI CON EL CUAL SE IDENTIFICARA"""
    id_item= models.ForeignKey(Item, on_delete = models.CASCADE)
    """EL ITEM AL CUAL ESTA ASIGNADO"""
    #tipo=models.CharField(max_length=20)
    valor=models.CharField(max_length=1000,null=True)
    """VALOR QUE SERA STRING PERO DEPENDIENDO DEL ATRIBUTO SE PODRA OBTENER EL VALOR REQUERIDO"""

class Versiones(models.Model):
    """TABLA DE VERSIONES EL CUAL RELACIONA LA VERSION DEL ITEM"""
    id= models.AutoField(primary_key = True) ###### clave de proyecto
    """ID AUTOMATICO"""
    id_Version= models.IntegerField()
    """VERSION DEL ITEM"""
    id_item= models.IntegerField()
    """ITEM ASIGNADO"""

class Comite(models.Model):
    """TABLA QUE TENDRA LA RELACION USUARIO-PROYECTO PERO PARA UN COMITE DE UN PROYECTO EN ESPECIFICO"""
    id = models.AutoField(primary_key=True)  ###### clave de proyecto
    """ID AUTOMATICO"""
    id_proyecto=models.IntegerField()
    """ID DEL PROYECTO"""
    id_user=models.IntegerField()
    """ID DEL USUARIO"""

#-----------------------MODELO LINEA BASE-----------------------------------------

class LineaBase(models.Model):
    """
    HACE REFERENCIA A UN CONJUNTO DETERMINADO DE ITEMS APROBADOS EN UNA FASE, LOS CUALES PASAN A FORMAR PARTE DE UNA LINEA BASE, EL USUARIO ES QUIEN DECIDE
    EL MOMENTO EN EL CUAL DESEA QUE ESTOS ITEMS SE AGRUPEN DE ESTA MANERA, UNA VEZ MÁS SEÑALANDO QUE LOS MISMOS DEBEN ESTAR APROBADOS OBLIGATORIAMENTE. 
    """

    choices_data_type = (
        ("Cerrada", "Cerrada"),
        ("Rota", "Rota"),
        ("Comprometida", "Comprometida")
    )
    """
    POSIBLES OPCIONES DE ESTADO DE LAS LINEAS BASE, POR DEFECTO LA LB TENDRÁ ESTADO CERRADA 
    """
    idLB = models.AutoField(primary_key = True)
    """
    HACE REFERENCIA AL ID QUE VA A LLEVAR CADA LINEA BASE EN UNA FASE DETERMINADA, CABE DESTACAR QUE EL ID ES UNICO E IRREPETIBLE
    """
    nombreLB = models.CharField('Nombre de Linea Base', max_length = 50, blank = False, null = False)
    """
    HACE REFERENCIA AL NOMBRE QUE LLEVARA LA LINEA BASE EN UNA FASE DETERMINADA, ASI COMO EL ID, TAMBIÉN EL NOMBRE ES UNICO E IRREPETIBLE
    """
    #items = models.ForeignKey(Item, on_delete = models.CASCADE)
    """
    HACE REFERENCIA AL CONJUNTO DE ITEMS QUE COMPONEN LA LINEA BASE
    """
    #idFase = models.ForeignKey(Fase, on_delete = models.CASCADE)
    """
    HACE REFERENCIA A LA FASE A LA CUAL PERTENECE LA LINEA BASE, PUEDE MÁS DE UNA LINEA BASE EN UNA MISMA FASE PERO NO PUEDEN COMPARTIR ITEMS
    """
    estado = models.CharField('Estado', max_length = 50, blank = False, null = False, choices = choices_data_type, default = 'Cerrada')
    """HACE REFERENCIA A UN ESTADO EN CONCRETO DE UNA DETERMINADA LINEA BASE, LA MISMA TENDRÁ POR DEFECTO EL ESTADO CERRADA"""
    
    class Meta:
        ordering = ['nombreLB']
        """SE ORDENARAN LAS LINEAS BASE DE ACUERDO AL NOMBRE"""
        verbose_name = 'Linea Base'
        """DENOMINACION SINGULAR DE UNA LINEA BASE"""
        verbose_name_plural = 'Lineas Base'
        """DENOMINACION PLURAL DE UNA LINEA BASE, EN ESTE CASO MAS DE UNA"""

class LB_item(models.Model):
    """
    ESTA CLASE SERÁ UTILIZADA PARA RELACIONAR UNA LINEA BASE CON UN ITEM, ASI TENDRÁ SOLO EL ID DE UN ITEM Y EL ID DE LA
    LINEA BASE A LA CUAL PERTENECE, UN ATRIBUTO ADICIONAL SERÁ EL ID DE LA CLASE LB_item.
    """
    id = models.AutoField(primary_key = True)
    """ID PERTENECIENTE A LA FASE LB_item"""
    item = models.ForeignKey(Item, on_delete = models.CASCADE)
    """ID PERTENECIENE A LA CLASE Item"""
    lb = models.ForeignKey(LineaBase, on_delete = models.CASCADE)
    """ID PERTENECIENTE A LA CLASE LineaBase"""