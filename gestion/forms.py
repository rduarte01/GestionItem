from django import forms
from django.forms import Textarea
from .models import Proyecto


class FormProyecto(forms.ModelForm):
    """
    FORMULARIO PARA INICIO DE PROYECTO EN DONDE SE MOSTRARN LOS CAMPOS COMO NOMBRE DE PROYECTO,
    DESCRIPCION, ESTADO Y SE DESPLEGARAN LOS USUARIOS A SER AÑADIDOS AL PROYECTO EN CREACION
    """
    class Meta:
        """META PARA DEFINIR LOS CAMPOS A MOSTRAR EN EL FORMULARIO"""
        model = Proyecto
        """SE REALIZA FORMULARIO DEL MODELO PROYECTO"""
        fields = [
                "nombre",
                "descripcion",
                "estado",
                "usuario"
                  ]
        """CAMPOS A MOSTRAR EN EL FORMULARIO"""
        labels= {
            "nombre":"Ingrese un Nombre para el proyecto",
            "descripcion":"Ingrese una descripcion si lo desea",
            "estado":"Selecciona el estado que tendra el proyecto",
            "usuario": "Selecciona Usuarios para Agregar al Proyecto"
        }
        """LA ETIQUETA DE CADA CAMPO"""
        widgets={
            "nombre": forms.TextInput(attrs={'class': 'form-control'}),
            "descripcion": forms.TextInput(attrs={'class': 'form-control'}),
            "estado":forms.CheckboxSelectMultiple(),
            "usuario": forms.CheckboxSelectMultiple(),
        }
        """LOS WIDGETS PARA CADA CAMPO AJUSTANDO A LO QUE SE NECESITA"""

