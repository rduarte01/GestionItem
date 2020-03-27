from django import forms
from django.forms import Textarea
from .models import Proyecto, Fase
from django.contrib.auth.models import User, Permission

class FormUserAgg(forms.ModelForm):
    class Meta:
        model = User
        fields=['username']
        permissions =forms.ModelMultipleChoiceField(
            queryset = Permission.objects.all(),
            required= False,
        )


class FormProyecto(forms.ModelForm):
    """
    FORMULARIO PARA INICIO DE PROYECTO EN DONDE SE MOSTRARN LOS CAMPOS COMO NOMBRE DE PROYECTO,
    DESCRIPCION, ESTADO Y SE DESPLEGARAN LOS USUARIOS A SER AÑADIDOS AL PROYECTO EN CREACION
    """
    fase = forms.IntegerField()

    class Meta:
        """META PARA DEFINIR LOS CAMPOS A MOSTRAR EN EL FORMULARIO"""
        model = Proyecto
        """SE REALIZA FORMULARIO DEL MODELO PROYECTO"""
        fields = [
                "nombre",
                "descripcion",
                "users",
                  ]
        """CAMPOS A MOSTRAR EN EL FORMULARIO"""
        labels= {
            "nombre":"Ingrese un Nombre para el proyecto",
            "descripcion":"Ingrese una descripcion si lo desea",
            "users":"Seleccione los usuarios a añadir",
        }
        """LA ETIQUETA DE CADA CAMPO"""
        widgets={
            "nombre": forms.TextInput(attrs={'class': 'form-control'}),
            "descripcion": forms.TextInput(attrs={'class': 'form-control'}),
            "users": forms.CheckboxSelectMultiple(),
        }
        """LOS WIDGETS PARA CADA CAMPO AJUSTANDO A LO QUE SE NECESITA"""

class FaseForm(forms.ModelForm):
    """
    HACE REFERENCIA AL MODELO FASE QUE SERA REPRESENTADO POR MEDIO DE ESTA CLASE FORMLARIO EN EL NAVEGADOR WEB
    CON SUS RESPECTIVOS CAMPOS A COMPLETAR
    """
    class Meta:
        model = Fase
        fields = [#'id_Fase',
                  'nombre',
                  'descripcion'
        ]
        """CAMPOS A SER COMPLETADOS EN EL FORMULARIO WEB A PRESENTAR"""

        labels = {
        #"id_Fase": "N° Fase",
        "nombre": "Nombre",
        "descripcion": "Descripción",
        #"estado": "Estado",
        #"id_Proyecto": "ID_Proyecto",
        }

        widgets = {
        #"id_Fase": forms.IntegerField(),
        "nombre" : forms.TextInput(attrs = {'class': 'form-control'}),
        "descripcion": forms.TextInput(attrs = {'class': 'form-control'}),
        #"estado": forms.TextInput(attrs = {'class': 'form-control'}),
        }

class FormAyuda(forms.Form):
    Consulta = forms.CharField(widget=forms.Textarea)
