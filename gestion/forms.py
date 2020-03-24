from django import forms
from django.forms import Textarea
from .models import Proyecto, User_Proyecto


class  FormUser_Proyecto(forms.ModelForm):
    class Meta:
        model = User_Proyecto
        fields=["user"]
        widgets = {
            "user": forms.CheckboxSelectMultiple(),
        }

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

                  ]
        """CAMPOS A MOSTRAR EN EL FORMULARIO"""
        labels= {
            "nombre":"Ingrese un Nombre para el proyecto",
            "descripcion":"Ingrese una descripcion si lo desea",
            "estado":"Selecciona el estado que tendra el proyecto",

        }
        """LA ETIQUETA DE CADA CAMPO"""
        widgets={
            "nombre": forms.TextInput(attrs={'class': 'form-control'}),
            "descripcion": forms.TextInput(attrs={'class': 'form-control'}),
            "estado":forms.RadioSelect(choices=[
                (1, 'Creado'),
                (2, 'Iniciado')
            ]),

        }
        """LOS WIDGETS PARA CADA CAMPO AJUSTANDO A LO QUE SE NECESITA"""


from django import forms
from .models import Fase

class FaseForm(forms.ModelForm):
    """Hace referencia al modelo Fase que será representado por medio de esta clase formulario en el navegador web
    con sus respectivos campos a completar
    """
    class Meta:
        model = Fase
        fields = ['id_Fase', 'nombre', 'descripcion'] #campos a ser representados en el formulario web a completar

        labels = {
            "id_Fase": "N° Fase",
            "nombre": "Nombre",
            "descripcion": "Descripción",
            "estado": "Estado",
        }

        widgets = {
            "id_Fase": forms.TextInput(attrs = {'class': 'form-control input-lg'}),
            "nombre" : forms.TextInput(attrs = {'class': 'form-control'}),
            "descripcion": forms.TextInput(attrs = {'class': 'form-control'}),
            "estado": forms.TextInput(attrs = {'class': 'form-control'}),
        }