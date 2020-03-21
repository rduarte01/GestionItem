from django.db import models
from django.contrib.auth import User


# Create your models here.

class Fase(models.Model):
    """Se tiene el modelo fase, el cual será utilizado en el proyecto para albergar a los items y poder
    dividirlos en etapas.
    Las fases tendrán dos estados: Abierta y Cerrada."""
    id_Fase = models.AutoField(primary_key = True, blank = False, null = False, default = 1)
    nombre = models.CharField(max_length = 100, blank = False, null = False)
    descripcion = models.TextField(blank = False, null = False)
    estado = models.CharField(max_length = 10, blank = False, null = False, choices = choises_data_type, default = 'Abierta')
    #id_Proyecto = models.ForeignKeyField(Proyecto, on_delete = models.CASCADE)
    choises_data_type = (
        ("1", "Abierta")
        ("2", "Cerrada")
    )

    class Meta:
        permissions = (("Poder Crear Item", "Crear Item"),
                       ("Poder Aprobar Item", "Aprobar Item"),
                       ("Poder Crear LB", "Crear Linea Base"),
                       ("Poder Modificar Atributo de Item", "Modificar Atributo de Item"),
                       ("Poder Reversionar Item","Reversionar Item"),
                       ("Poder Aprobar Item", "Aprobar Item"),
                       ("Poder Relacionar Item", "Relacionar Item"),
                       ("Poder Generar Solicitud de Cambio", "Generar Solicitud de Cambio"),
                       ("Poder Cambiar Estado de Item", "Cambiar Estado de Item"),
                       )
        verbose_name = 'Fase'
        verbose_name_plural = 'Fases'
        ordering = ['id_Fase']