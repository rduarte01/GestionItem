from django.db import models

# Create your models here.

class Proyecto(models.Model):
    nombre:models.CharField(max_length=10,default='nombre de tu usuario')
    class Meta:
        permissions = (
            ("cerrar_proyecto", "Cerrar Proyectos"),
            #("cre_proyecto", "Cerrar Proyectos"),
        )


class Fase(models.Model):
    nombre:models.CharField(max_length=10,default="nombre de la fase")
    cantida=models.IntegerField()
    class Meta:
        permissions=(
            ("cerrar_fase","Cerrar Fases"),
        )

class TipoItem(models.Model):
    codigo=models.CharField(max_length=10,default="codigo Tipo Item")
    class Meta:
        permissions=(
            ("importar_tipo_item","Poder importar Tipo Item"),
        )

