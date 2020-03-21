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
                "id_proyecto",
                "nombre",
                "descripcion",
                "estado",
                "usuario"
                  ]
        """CAMPOS A MOSTRAR EN EL FORMULARIO"""
        labels= {
            "id_proyecto": "N° ID",
            "nombre":"Nombre",
            "descripcion":"Descripcion",
            "estado":"Estado",
            "usuario": "Selecciona Usuarios para Agregar al Proyecto"
        }
        """LA ETIQUETA DE CADA CAMPO"""
        widgets={
            "id_proyecto": forms.TextInput(attrs={'class': 'form-control'}),
            "nombre": forms.TextInput(attrs={'class': 'form-control'}),
            "descripcion": forms.TextInput(attrs={'class': 'form-control'}),
            "estado":forms.TextInput(attrs={'class': 'form-control'}),
            "usuario": forms.CheckboxSelectMultiple(),
        }
        """LOS WIDGETS PARA CADA CAMPO AJUSTANDO A LO QUE SE NECESITA"""

