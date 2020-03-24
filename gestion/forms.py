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