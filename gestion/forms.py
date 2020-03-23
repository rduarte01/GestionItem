from django import forms
from django.forms import Textarea

from .models import Proyecto,TipoItem,Atributo   #, Usuario
####### se escribe formulario

"""class FormUsuario(forms.ModelForm):
    class Meta:
        model = Usuario
        fields=["nombre"]
"""

class FormProyecto(forms.ModelForm):
    class Meta:
        model = Proyecto
        fields = [
                "id_proyecto",
                "nombre",
                "descripcion",
                "estado",
                "usuario"
                  ]
        labels= {
            "id_proyecto": "N° ID",
            "nombre":"Nombre",
            "descripcion":"Descripcion",
            "estado":"Estado",
            "usuario": "Selecciona Usuarios para Agregar al Proyecto"
        }
        widgets={
            "id_proyecto": forms.TextInput(attrs={'class': 'form-control'}),
            "nombre": forms.TextInput(attrs={'class': 'form-control'}),
            "descripcion": forms.TextInput(attrs={'class': 'form-control'}),
            "estado":forms.TextInput(attrs={'class': 'form-control'}),
            "usuario": forms.CheckboxSelectMultiple(),
        }
class TipoItemForm(forms.Form):
    """
        En esta clase se define la estrutura del formulario para crear un tipo de item
    """
    nombre=forms.CharField(label="Nombre del Tipo de Item ",max_length=100,required=True,
                           widget=forms.TextInput(
                                            attrs={"placeholder":"Nombre Tipo Item",
                                                   }
                                                 )
                           )
    cantidad=forms.IntegerField(label="Cantidad de Atributos del Tipo de Item",max_value=10,required=True,
                                widget=forms.TextInput(attrs={"placeholder": "Cantidad Tipo Item",
                                                            })
                                )


class AtributeForm(forms.ModelForm):
    class Meta:
        model=Atributo
        fields=('nombre','es_obligatorio','tipo_dato')

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

class SettingsUserForm(forms.Form):

    is_admin=forms.BooleanField(required=False)
    is_manager=forms.BooleanField(required=False)

    State_CHOICES = [
        ('True', 'Aprobado'),
        ('False', 'Desactivado'),
    ]


    estado=forms.ChoiceField(
        required=True,
        widget=forms.Select,
        choices=State_CHOICES,
    )
