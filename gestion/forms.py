from django import forms
from django.forms import Textarea

from .models import Proyecto

####### se escribe formulario

class RegModelForm(forms.ModelForm):
    class Meta:
        model = Proyecto
        fields = ["nombre","descripcion"]

class form_Proyecto(forms.Form):
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
    ###id_proyecto= forms.IntegerField(auto_created = True, primary_key = True, serialize = False) ###### clave de proyecto
    nombre= forms.CharField(max_length=30)
    descripcion= forms.CharField(widget=Textarea)
    ###-Usuarios: Usuario[*]    FALTA CREAR
    ###-Fases: Fases[*]
    estado= forms.IntegerField()
    ###-Rol: Rol[*]