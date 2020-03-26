from django import forms
from django.forms import Textarea
from django.contrib.auth.models import User, Group, Permission
from .models import Proyecto,TipoItem,Atributo   #, Usuario
####### se escribe formulario
from django.forms.widgets import SelectMultiple, CheckboxSelectMultiple
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

class SettingsUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username','email','esta_aprobado']
        labels = {
            'username': 'Nombre de Usuario',
            'email': 'Correo Electronico del Usuario',
            'esta_aprobado': 'Estado del usuario',
        }
        OPTIONS = (
            ('True', "Aprobado"),
            ('False', "En Espera"),
        )
        widgets = {
            'username': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Nombre de usuario',
                    'id': 'username'
                }
            ),
            'email': forms.EmailInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Correo Electronico del Usuario',
                    'id': 'email'
                }
            ),
            'esta_aprobado': forms.RadioSelect(choices=[
                (True, 'Activo'),
                (False, 'En Espera')
            ]),
        }


class RolForm(forms.ModelForm):
    class Meta:

        model = Group
        fields = "__all__"

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            for perm in self.permissions:
                self.fields[perm].widget.attrs['class'] = 'form-control'

        widgets={
            'name':forms.TextInput(
                attrs={
                    'class':'form-control',
                    'placeholder':'Ingrese nombre del Rol',
                }
            ),
            'permissions':forms.CheckboxSelectMultiple(),
        }


