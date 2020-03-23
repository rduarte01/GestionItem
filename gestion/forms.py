from django import forms
from .models import Fase

class FaseForm(forms.ModelForm):
    """Hace referencia al modelo Fase que será representado por medio de esta clase formulario en el navegador web
    con sus respectivos campos a completar
    """
    class Meta:
        model = Fase
        fields = ['id_Fase', 'nombre', 'descripcion'] #campos a ser representados en el formulario web a completar
